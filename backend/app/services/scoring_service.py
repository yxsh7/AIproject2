"""Productivity scoring service with role-based evaluation"""
import logging
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.models import (
    DeveloperProfile,
    WorkActivity,
    ProductivityScore,
    WorkType,
    RoleLevel,
)

logger = logging.getLogger(__name__)


# Role-based evaluation weights
# Each role has different expectations for different dimensions
ROLE_WEIGHTS = {
    RoleLevel.INTERN: {
        "complexity": 0.10,  # Learning, simple tasks
        "velocity": 0.15,  # Consistent output expected
        "quality": 0.25,  # Focus on learning good practices
        "impact": 0.10,  # Limited scope
        "collaboration": 0.25,  # Learn from others
        "mentoring": 0.15,  # Minimal expectation
    },
    RoleLevel.JUNIOR: {
        "complexity": 0.15,
        "velocity": 0.20,
        "quality": 0.25,
        "impact": 0.15,
        "collaboration": 0.20,
        "mentoring": 0.05,
    },
    RoleLevel.MID: {
        "complexity": 0.20,
        "velocity": 0.20,
        "quality": 0.20,
        "impact": 0.20,
        "collaboration": 0.15,
        "mentoring": 0.05,
    },
    RoleLevel.SENIOR: {
        "complexity": 0.25,  # Handle complex problems
        "velocity": 0.15,  # Quality over speed
        "quality": 0.20,
        "impact": 0.25,  # Significant impact expected
        "collaboration": 0.10,
        "mentoring": 0.05,  # Start mentoring juniors
    },
    RoleLevel.STAFF: {
        "complexity": 0.25,
        "velocity": 0.10,
        "quality": 0.20,
        "impact": 0.30,  # High impact
        "collaboration": 0.05,
        "mentoring": 0.10,  # Mentor team
    },
    RoleLevel.PRINCIPAL: {
        "complexity": 0.20,
        "velocity": 0.05,  # Architecture/strategy focus
        "quality": 0.20,
        "impact": 0.35,  # Organizational impact
        "collaboration": 0.10,
        "mentoring": 0.10,  # Technical leadership
    },
}


class ProductivityScoringService:
    """Service for calculating productivity scores with role-based evaluation"""

    def __init__(self, db: Session):
        self.db = db

    def _compute_score(
        self,
        developer: DeveloperProfile,
        activities: List[WorkActivity],
        start_date: date,
        end_date: date,
    ) -> Optional[ProductivityScore]:
        """Compute a ProductivityScore from pre-fetched activities (no DB queries)."""
        if not activities:
            return None

        complexity_score = self._calculate_complexity_score(activities)
        velocity_score = self._calculate_velocity_score(activities, start_date, end_date)
        quality_score = self._calculate_quality_score(activities)
        impact_score = self._calculate_impact_score(activities)
        collaboration_score = self._calculate_collaboration_score(activities)
        mentoring_score = self._calculate_mentoring_score(activities)

        weights = ROLE_WEIGHTS.get(developer.role_level, ROLE_WEIGHTS[RoleLevel.MID])

        overall_score = (
            complexity_score * weights["complexity"]
            + velocity_score * weights["velocity"]
            + quality_score * weights["quality"]
            + impact_score * weights["impact"]
            + collaboration_score * weights["collaboration"]
            + mentoring_score * weights["mentoring"]
        ) * 10  # Scale to 0-100

        work_breakdown = self._calculate_work_breakdown(activities)

        return ProductivityScore(
            developer_id=developer.id,
            period_start=start_date,
            period_end=end_date,
            period_type="monthly",
            overall_score=round(overall_score, 2),
            complexity_score=round(complexity_score, 2),
            velocity_score=round(velocity_score, 2),
            quality_score=round(quality_score, 2),
            impact_score=round(impact_score, 2),
            collaboration_score=round(collaboration_score, 2),
            mentoring_score=round(mentoring_score, 2),
            breakdown={
                "total_activities": len(activities),
                "work_type_distribution": work_breakdown,
                "role_weights": weights,
            },
            total_commits=self._count_by_source(activities, "git"),
            total_prs=0,
            total_tickets=self._count_by_source(activities, "jira"),
            lines_added=0,
            lines_deleted=0,
            work_breakdown=work_breakdown,
            score_metadata={
                "role_level": developer.role_level.value,
                "evaluation_weights": weights,
                "activity_count": len(activities),
                "days_active": len(set(a.activity_date for a in activities)),
            },
        )

    def calculate_developer_score(
        self,
        developer_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Optional[ProductivityScore]:
        """Calculate productivity score for a developer over a time period."""
        developer = self.db.query(DeveloperProfile).filter(
            DeveloperProfile.id == developer_id
        ).first()

        if not developer:
            logger.error(f"Developer {developer_id} not found")
            return None

        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        activities = (
            self.db.query(WorkActivity)
            .filter(
                WorkActivity.developer_id == developer_id,
                WorkActivity.activity_date >= start_date,
                WorkActivity.activity_date <= end_date,
            )
            .all()
        )

        if not activities:
            logger.info(f"No activities found for developer {developer_id}")
            return None

        return self._compute_score(developer, activities, start_date, end_date)

    def _calculate_complexity_score(self, activities: List[WorkActivity]) -> float:
        """Calculate average complexity score (0-10)"""
        if not activities:
            return 0.0

        complexity_scores = [a.complexity_score for a in activities if a.complexity_score]
        if not complexity_scores:
            return 5.0  # Neutral if no data

        return sum(complexity_scores) / len(complexity_scores)

    def _calculate_velocity_score(
        self, activities: List[WorkActivity], start_date: date, end_date: date
    ) -> float:
        """
        Calculate velocity score based on consistent output (0-10)

        Factors:
        - Number of activities per week
        - Consistency (no big gaps)
        - Sustained effort
        """
        if not activities:
            return 0.0

        days_in_period = (end_date - start_date).days + 1
        weeks_in_period = max(days_in_period / 7, 1)

        # Activities per week
        activities_per_week = len(activities) / weeks_in_period

        # Score based on activity frequency
        # Assuming 5-10 activities per week is good
        if activities_per_week >= 10:
            base_score = 10.0
        elif activities_per_week >= 5:
            base_score = 8.0 + (activities_per_week - 5) * 0.4
        elif activities_per_week >= 2:
            base_score = 5.0 + (activities_per_week - 2) * 1.0
        else:
            base_score = activities_per_week * 2.5

        # Check consistency (active days per week)
        active_days = len(set(a.activity_date for a in activities))
        days_per_week = active_days / weeks_in_period
        consistency_multiplier = min(days_per_week / 4, 1.0)  # 4 days/week = 100%

        return min(base_score * consistency_multiplier, 10.0)

    def _calculate_quality_score(self, activities: List[WorkActivity]) -> float:
        """Calculate average quality score (0-10)"""
        if not activities:
            return 0.0

        quality_scores = [a.quality_score for a in activities if a.quality_score]
        if not quality_scores:
            return 5.0  # Neutral if no data

        return sum(quality_scores) / len(quality_scores)

    def _calculate_impact_score(self, activities: List[WorkActivity]) -> float:
        """Calculate average impact score (0-10)"""
        if not activities:
            return 0.0

        impact_scores = [a.impact_score for a in activities if a.impact_score]
        if not impact_scores:
            return 5.0  # Neutral if no data

        return sum(impact_scores) / len(impact_scores)

    def _calculate_collaboration_score(self, activities: List[WorkActivity]) -> float:
        """
        Calculate collaboration score based on code reviews, PR comments, etc. (0-10)

        Factors:
        - Code reviews done
        - PR comments
        - Pair programming indicators
        - Helping others
        """
        if not activities:
            return 0.0

        # Count collaboration activities
        collaboration_count = sum(
            1
            for a in activities
            if a.work_type
            in [WorkType.CODE_REVIEW, WorkType.MENTORING, WorkType.DOCUMENTATION]
        )

        # Score based on collaboration frequency
        collaboration_ratio = collaboration_count / len(activities)

        # 20%+ collaboration is excellent
        if collaboration_ratio >= 0.20:
            return 10.0
        elif collaboration_ratio >= 0.10:
            return 7.0 + (collaboration_ratio - 0.10) * 30
        elif collaboration_ratio >= 0.05:
            return 5.0 + (collaboration_ratio - 0.05) * 40
        else:
            return collaboration_ratio * 100

    def _calculate_mentoring_score(self, activities: List[WorkActivity]) -> float:
        """
        Calculate mentoring score based on helping others (0-10)

        Factors:
        - Documentation written
        - Code reviews with learning comments
        - Pair programming sessions
        - Knowledge sharing
        """
        if not activities:
            return 0.0

        # Count mentoring-related activities
        mentoring_count = sum(
            1
            for a in activities
            if a.work_type
            in [
                WorkType.DOCUMENTATION,
                WorkType.CODE_REVIEW,
                WorkType.MENTORING,
            ]
        )

        # Check AI analysis for mentoring indicators
        mentoring_indicators = 0
        for activity in activities:
            if activity.ai_analysis:
                analysis = activity.ai_analysis
                # Look for mentoring keywords
                if any(
                    keyword in str(analysis).lower()
                    for keyword in ["mentor", "help", "teach", "guide", "explain"]
                ):
                    mentoring_indicators += 1

        total_mentoring = mentoring_count + mentoring_indicators

        # Score based on mentoring frequency
        mentoring_ratio = total_mentoring / len(activities)

        if mentoring_ratio >= 0.15:
            return 10.0
        elif mentoring_ratio >= 0.10:
            return 7.0 + (mentoring_ratio - 0.10) * 60
        elif mentoring_ratio >= 0.05:
            return 5.0 + (mentoring_ratio - 0.05) * 40
        else:
            return mentoring_ratio * 100

    def _calculate_work_breakdown(
        self, activities: List[WorkActivity]
    ) -> Dict[str, float]:
        """Calculate percentage breakdown by work type"""
        if not activities:
            return {}

        work_type_counts = {}
        for activity in activities:
            work_type = activity.work_type.value if activity.work_type else "unknown"
            work_type_counts[work_type] = work_type_counts.get(work_type, 0) + 1

        total = len(activities)
        return {
            work_type: round((count / total) * 100, 2)
            for work_type, count in work_type_counts.items()
        }

    def _count_by_source(self, activities: List[WorkActivity], source_type: str) -> int:
        """Count activities by source type"""
        return sum(1 for a in activities if a.source_type == source_type)

    def calculate_team_scores(
        self,
        team: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Dict:
        """
        Calculate aggregate productivity scores for a team

        Args:
            team: Team name
            start_date: Start of evaluation period
            end_date: End of evaluation period

        Returns:
            Dict with team aggregate scores and individual scores
        """
        # Get all developers in team
        developers = (
            self.db.query(DeveloperProfile)
            .filter(DeveloperProfile.team == team)
            .all()
        )

        if not developers:
            return {"error": "No developers found in team"}

        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        # Bulk-fetch all activities for the whole team in a single query (avoids N+1)
        dev_ids = [d.id for d in developers]
        all_activities = (
            self.db.query(WorkActivity)
            .filter(
                WorkActivity.developer_id.in_(dev_ids),
                WorkActivity.activity_date >= start_date,
                WorkActivity.activity_date <= end_date,
            )
            .all()
        )
        activities_by_dev: Dict[int, List[WorkActivity]] = {}
        for a in all_activities:
            activities_by_dev.setdefault(a.developer_id, []).append(a)

        individual_scores = []
        for developer in developers:
            score = self._compute_score(
                developer, activities_by_dev.get(developer.id, []), start_date, end_date
            )
            if score:
                individual_scores.append({
                    "developer_id": developer.id,
                    "developer_name": developer.user.full_name if developer.user else "Unknown",
                    "role_level": developer.role_level.value,
                    "overall_score": score.overall_score,
                    "complexity_score": score.complexity_score,
                    "velocity_score": score.velocity_score,
                    "quality_score": score.quality_score,
                    "impact_score": score.impact_score,
                    "collaboration_score": score.collaboration_score,
                    "mentoring_score": score.mentoring_score,
                })

        if not individual_scores:
            return {"error": "No activity data for team"}

        # Calculate team aggregates
        team_size = len(individual_scores)
        aggregate = {
            "team": team,
            "team_size": team_size,
            "period_start": start_date,
            "period_end": end_date,
            "average_overall_score": round(
                sum(s["overall_score"] for s in individual_scores) / team_size, 2
            ),
            "average_complexity_score": round(
                sum(s["complexity_score"] for s in individual_scores) / team_size, 2
            ),
            "average_velocity_score": round(
                sum(s["velocity_score"] for s in individual_scores) / team_size, 2
            ),
            "average_quality_score": round(
                sum(s["quality_score"] for s in individual_scores) / team_size, 2
            ),
            "average_impact_score": round(
                sum(s["impact_score"] for s in individual_scores) / team_size, 2
            ),
            "average_collaboration_score": round(
                sum(s["collaboration_score"] for s in individual_scores) / team_size, 2
            ),
            "average_mentoring_score": round(
                sum(s["mentoring_score"] for s in individual_scores) / team_size, 2
            ),
            "top_performers": sorted(
                individual_scores, key=lambda x: x["overall_score"], reverse=True
            )[:3],
            "individual_scores": individual_scores,
        }

        return aggregate

    def get_score_trends(
        self, developer_id: int, periods: int = 12
    ) -> List[Dict]:
        """
        Get historical productivity score trends

        Args:
            developer_id: Developer profile ID
            periods: Number of periods to retrieve (default: 12 weeks)

        Returns:
            List of scores by period
        """
        scores = (
            self.db.query(ProductivityScore)
            .filter(ProductivityScore.developer_id == developer_id)
            .order_by(ProductivityScore.period_end.desc())
            .limit(periods)
            .all()
        )

        return [
            {
                "period_start": score.period_start.isoformat(),
                "period_end": score.period_end.isoformat(),
                "overall_score": score.overall_score,
                "complexity_score": score.complexity_score,
                "velocity_score": score.velocity_score,
                "quality_score": score.quality_score,
                "impact_score": score.impact_score,
                "collaboration_score": score.collaboration_score,
                "mentoring_score": score.mentoring_score,
            }
            for score in reversed(scores)  # Oldest to newest
        ]

    def save_score(self, score: ProductivityScore) -> ProductivityScore:
        """Save productivity score to database"""
        self.db.add(score)
        self.db.commit()
        self.db.refresh(score)
        return score

    def get_latest_score(self, developer_id: int) -> Optional[ProductivityScore]:
        """Get most recent productivity score for developer"""
        return (
            self.db.query(ProductivityScore)
            .filter(ProductivityScore.developer_id == developer_id)
            .order_by(ProductivityScore.calculated_at.desc())
            .first()
        )
