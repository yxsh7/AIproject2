"""AI-powered insights generation service"""
import logging
from datetime import date, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import (
    DeveloperProfile,
    WorkActivity,
    ProductivityScore,
    AIInsight,
    InsightType,
)
from app.ai.base import get_ai_chat_model
from app.config import settings

logger = logging.getLogger(__name__)

# Thresholds used by the insights engine
_TREND_THRESHOLD = 5.0          # score delta to detect an upward/downward trend
_CONSISTENCY_VARIANCE = 10.0    # variance below which performance is "consistent"
_LOW_ACTIVITY_RATIO = 0.3       # min fraction of days active before flagging
_HIGH_ACTIVITY_PER_DAY = 5      # activities/active-day above which burnout risk fires
_LOW_COLLABORATION_RATIO = 0.05 # min fraction of collaborative activities
_LOW_SCORE_THRESHOLD = 6.0      # score component below which recommendations fire


class InsightsService:
    """Service for generating AI-powered productivity insights"""

    def __init__(self, db: Session):
        self.db = db
        self.ai_model = get_ai_chat_model()

    def generate_developer_insights(
        self,
        developer_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generate comprehensive insights for a developer

        Args:
            developer_id: Developer profile ID
            start_date: Start of analysis period
            end_date: End of analysis period

        Returns:
            List of insights with recommendations
        """
        # Get developer
        developer = (
            self.db.query(DeveloperProfile)
            .filter(DeveloperProfile.id == developer_id)
            .first()
        )

        if not developer:
            logger.error(f"Developer {developer_id} not found")
            return []

        # Default to last 30 days
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        insights = []

        # Generate different types of insights
        insights.extend(self._detect_productivity_patterns(developer, start_date, end_date))
        insights.extend(self._detect_work_style_patterns(developer, start_date, end_date))
        insights.extend(self._detect_anomalies(developer, start_date, end_date))
        insights.extend(self._generate_recommendations(developer, start_date, end_date))

        return insights

    def _detect_productivity_patterns(
        self, developer: DeveloperProfile, start_date: date, end_date: date
    ) -> List[Dict[str, Any]]:
        """Detect productivity patterns and trends"""
        insights = []

        # Get productivity scores for last few periods
        scores = (
            self.db.query(ProductivityScore)
            .filter(ProductivityScore.developer_id == developer.id)
            .order_by(ProductivityScore.period_end.desc())
            .limit(4)
            .all()
        )

        if len(scores) < 2:
            return insights

        # Analyze trend
        recent_scores = [s.overall_score for s in reversed(scores)]
        avg_recent = sum(recent_scores[:2]) / 2 if len(recent_scores) >= 2 else 0
        avg_older = sum(recent_scores[2:]) / 2 if len(recent_scores) >= 4 else avg_recent

        if avg_recent > avg_older + _TREND_THRESHOLD:
            insights.append({
                "insight_type": "productivity_trend",
                "title": "Strong Upward Productivity Trend",
                "description": f"Productivity has improved by {round(avg_recent - avg_older, 1)} points over recent periods. This shows consistent growth and improvement.",
                "confidence": 0.9,
                "recommendations": [
                    "Continue current practices that are driving improvement",
                    "Document what's working well to share with team",
                    "Consider mentoring others with similar growth patterns",
                ],
                "supporting_data": {
                    "recent_average": round(avg_recent, 2),
                    "previous_average": round(avg_older, 2),
                    "improvement": round(avg_recent - avg_older, 2),
                },
            })
        elif avg_recent < avg_older - _TREND_THRESHOLD:
            insights.append({
                "insight_type": "productivity_trend",
                "title": "Declining Productivity Detected",
                "description": f"Productivity has decreased by {round(avg_older - avg_recent, 1)} points. This may indicate burnout, blockers, or changing priorities.",
                "confidence": 0.85,
                "recommendations": [
                    "Schedule 1-on-1 with manager to discuss workload",
                    "Review current projects for blockers or dependencies",
                    "Consider taking time to address technical debt",
                    "Evaluate work-life balance and prevent burnout",
                ],
                "supporting_data": {
                    "recent_average": round(avg_recent, 2),
                    "previous_average": round(avg_older, 2),
                    "decline": round(avg_older - avg_recent, 2),
                },
            })

        # Check score consistency
        if len(recent_scores) >= 3:
            score_variance = sum((s - avg_recent) ** 2 for s in recent_scores) / len(
                recent_scores
            )

            if score_variance < _CONSISTENCY_VARIANCE:
                insights.append({
                    "insight_type": "consistency",
                    "title": "Highly Consistent Performance",
                    "description": "Productivity scores show very consistent performance with minimal variation. This indicates stable, reliable output.",
                    "confidence": 0.9,
                    "recommendations": [
                        "Excellent consistency - maintain current practices",
                        "Consider taking on stretch projects for growth",
                    ],
                    "supporting_data": {
                        "variance": round(score_variance, 2),
                        "scores": [round(s, 2) for s in recent_scores],
                    },
                })

        return insights

    def _detect_work_style_patterns(
        self, developer: DeveloperProfile, start_date: date, end_date: date
    ) -> List[Dict[str, Any]]:
        """Detect patterns in work style and preferences"""
        insights = []

        # Get recent work activities
        activities = (
            self.db.query(WorkActivity)
            .filter(
                WorkActivity.developer_id == developer.id,
                WorkActivity.activity_date >= start_date,
                WorkActivity.activity_date <= end_date,
            )
            .all()
        )

        if not activities:
            return insights

        # Analyze work type preferences
        work_type_counts = {}
        for activity in activities:
            work_type = activity.work_type.value if activity.work_type else "unknown"
            work_type_counts[work_type] = work_type_counts.get(work_type, 0) + 1

        # Find dominant work type
        if work_type_counts:
            dominant_type = max(work_type_counts, key=work_type_counts.get)
            dominant_ratio = work_type_counts[dominant_type] / len(activities)

            if dominant_ratio > 0.5:
                insights.append({
                    "insight_type": "work_preference",
                    "title": f"Strong Focus on {dominant_type.replace('_', ' ').title()}",
                    "description": f"{int(dominant_ratio * 100)}% of work is {dominant_type.replace('_', ' ')}. This shows clear specialization.",
                    "confidence": 0.85,
                    "recommendations": [
                        f"Leverage expertise in {dominant_type.replace('_', ' ')} for high-impact projects",
                        "Consider diversifying work types for skill development",
                        "Mentor others in this area of expertise",
                    ],
                    "supporting_data": {
                        "dominant_type": dominant_type,
                        "percentage": round(dominant_ratio * 100, 1),
                        "work_distribution": {
                            k: round((v / len(activities)) * 100, 1)
                            for k, v in work_type_counts.items()
                        },
                    },
                })

        # Analyze complexity preference
        avg_complexity = sum(a.complexity_score for a in activities) / len(activities)

        if avg_complexity >= 7:
            insights.append({
                "insight_type": "work_preference",
                "title": "Tackles High Complexity Work",
                "description": f"Average complexity score of {round(avg_complexity, 1)} indicates preference for challenging, complex problems.",
                "confidence": 0.9,
                "recommendations": [
                    "Assign to critical, high-complexity initiatives",
                    "Consider technical leadership or architecture roles",
                    "Share problem-solving approaches with team",
                ],
                "supporting_data": {
                    "average_complexity": round(avg_complexity, 2),
                },
            })
        elif avg_complexity <= 3:
            insights.append({
                "insight_type": "work_preference",
                "title": "Focuses on Simpler, Well-Defined Tasks",
                "description": f"Average complexity score of {round(avg_complexity, 1)} suggests focus on straightforward, well-scoped work.",
                "confidence": 0.85,
                "recommendations": [
                    "Gradually introduce more complex challenges for growth",
                    "Pair with senior developers on complex problems",
                    "Current work style excellent for sprint reliability",
                ],
                "supporting_data": {
                    "average_complexity": round(avg_complexity, 2),
                },
            })

        return insights

    def _detect_low_activity(
        self, activities: List[Dict], active_days: int, days_in_period: int
    ) -> List[Dict[str, Any]]:
        """Flag periods where the developer was active less than _LOW_ACTIVITY_RATIO of days."""
        if active_days >= days_in_period * _LOW_ACTIVITY_RATIO:
            return []
        return [{
            "insight_type": "anomaly",
            "title": "Low Activity Detected",
            "description": (
                f"Only {active_days} active days out of {days_in_period} total days. "
                "This may indicate blockers, vacation, or focus on non-tracked work."
            ),
            "confidence": 0.7,
            "recommendations": [
                "Check for blockers or dependencies preventing progress",
                "Ensure all work is being tracked in GitHub/Jira",
                "Discuss with manager if workload is appropriate",
            ],
            "supporting_data": {
                "active_days": active_days,
                "total_days": days_in_period,
                "activity_ratio": round(active_days / days_in_period, 2),
            },
        }]

    def _detect_high_activity(
        self, activities: list, active_days: int
    ) -> List[Dict[str, Any]]:
        """Flag periods where activity rate exceeds _HIGH_ACTIVITY_PER_DAY (burnout risk)."""
        activities_per_day = len(activities) / max(active_days, 1)
        if activities_per_day <= _HIGH_ACTIVITY_PER_DAY:
            return []
        return [{
            "insight_type": "anomaly",
            "title": "Very High Activity Level",
            "description": (
                f"Averaging {round(activities_per_day, 1)} activities per day. "
                "While productivity is high, monitor for burnout risk."
            ),
            "confidence": 0.75,
            "recommendations": [
                "Ensure sustainable pace - high intensity isn't sustainable long-term",
                "Take regular breaks and maintain work-life balance",
                "Discuss workload with manager if feeling overwhelmed",
            ],
            "supporting_data": {
                "activities_per_day": round(activities_per_day, 2),
                "total_activities": len(activities),
                "active_days": active_days,
            },
        }]

    def _detect_collaboration_gap(self, activities: list) -> List[Dict[str, Any]]:
        """Flag when less than _LOW_COLLABORATION_RATIO of activities are collaborative."""
        collaboration_count = sum(
            1 for a in activities
            if a.work_type and a.work_type.value in ["code_review", "pair_programming", "documentation"]
        )
        collaboration_ratio = collaboration_count / len(activities)
        if collaboration_ratio >= _LOW_COLLABORATION_RATIO:
            return []
        return [{
            "insight_type": "collaboration_gap",
            "title": "Limited Collaboration Detected",
            "description": (
                f"Only {int(collaboration_ratio * 100)}% of activities involve collaboration. "
                "Increasing teamwork can improve learning and code quality."
            ),
            "confidence": 0.8,
            "recommendations": [
                "Participate in more code reviews",
                "Pair program on complex features",
                "Contribute to team documentation",
                "Attend team knowledge sharing sessions",
            ],
            "supporting_data": {
                "collaboration_percentage": round(collaboration_ratio * 100, 1),
                "collaboration_count": collaboration_count,
                "total_activities": len(activities),
            },
        }]

    def _detect_anomalies(
        self, developer: DeveloperProfile, start_date: date, end_date: date
    ) -> List[Dict[str, Any]]:
        """Detect anomalies and potential issues."""
        activities = (
            self.db.query(WorkActivity)
            .filter(
                WorkActivity.developer_id == developer.id,
                WorkActivity.activity_date >= start_date,
                WorkActivity.activity_date <= end_date,
            )
            .all()
        )

        if not activities:
            return []

        days_in_period = (end_date - start_date).days + 1
        active_days = len(set(a.activity_date for a in activities))

        return (
            self._detect_low_activity(activities, active_days, days_in_period)
            + self._detect_high_activity(activities, active_days)
            + self._detect_collaboration_gap(activities)
        )

    def _generate_recommendations(
        self, developer: DeveloperProfile, start_date: date, end_date: date
    ) -> List[Dict[str, Any]]:
        """Generate personalized recommendations based on role and performance"""
        insights = []

        # Get latest productivity score
        latest_score = (
            self.db.query(ProductivityScore)
            .filter(ProductivityScore.developer_id == developer.id)
            .order_by(ProductivityScore.period_end.desc())
            .first()
        )

        if not latest_score:
            return insights

        # Identify areas for improvement (lowest scores)
        score_components = {
            "complexity": latest_score.complexity_score,
            "velocity": latest_score.velocity_score,
            "quality": latest_score.quality_score,
            "impact": latest_score.impact_score,
            "collaboration": latest_score.collaboration_score,
            "mentoring": latest_score.mentoring_score,
        }

        # Find lowest scoring component
        lowest_component = min(score_components, key=score_components.get)
        lowest_score = score_components[lowest_component]

        if lowest_score < _LOW_SCORE_THRESHOLD:
            recommendations_map = {
                "complexity": [
                    "Take on more challenging technical problems",
                    "Study system architecture and design patterns",
                    "Pair with senior engineers on complex features",
                    "Spend time on technical deep dives and learning",
                ],
                "velocity": [
                    "Break down large tasks into smaller deliverables",
                    "Focus on consistent daily progress",
                    "Reduce context switching between tasks",
                    "Set daily goals and track completion",
                ],
                "quality": [
                    "Add more tests to code contributions",
                    "Spend more time on code reviews and refactoring",
                    "Follow team coding standards more closely",
                    "Get code reviewed by senior engineers",
                ],
                "impact": [
                    "Align work with team/company OKRs",
                    "Focus on customer-facing features",
                    "Take ownership of critical system components",
                    "Seek high-leverage projects",
                ],
                "collaboration": [
                    "Participate in more code reviews",
                    "Engage in pair programming sessions",
                    "Share knowledge through documentation",
                    "Mentor junior team members",
                ],
                "mentoring": [
                    "Write more technical documentation",
                    "Help onboard new team members",
                    "Share expertise in team meetings",
                    "Review and provide feedback on others' code",
                ],
            }

            insights.append({
                "insight_type": "recommendation",
                "title": f"Improve {lowest_component.title()} Score",
                "description": f"{lowest_component.title()} score of {round(lowest_score, 1)}/10 is below target. Focus on this area for professional growth.",
                "confidence": 0.9,
                "recommendations": recommendations_map.get(lowest_component, []),
                "supporting_data": {
                    "current_score": round(lowest_score, 2),
                    "target_score": 7.0,
                    "gap": round(7.0 - lowest_score, 2),
                },
            })

        # Role-specific recommendations
        if developer.role_level.value in ["intern", "junior"]:
            insights.append({
                "insight_type": "growth_path",
                "title": "Focus on Learning and Growth",
                "description": f"As a {developer.role_level.value}, prioritize learning fundamentals and building consistent output.",
                "confidence": 1.0,
                "recommendations": [
                    "Seek feedback on every code contribution",
                    "Study the codebase to understand architecture",
                    "Ask questions when blocked - don't stay stuck",
                    "Build a habit of daily commits/progress",
                ],
                "supporting_data": {"role_level": developer.role_level.value},
            })
        elif developer.role_level.value in ["senior", "staff", "principal"]:
            insights.append({
                "insight_type": "growth_path",
                "title": "Focus on Impact and Leadership",
                "description": f"As a {developer.role_level.value}, maximize impact through technical leadership and mentoring.",
                "confidence": 1.0,
                "recommendations": [
                    "Lead architecture decisions for major features",
                    "Mentor mid-level and junior engineers",
                    "Identify and solve systemic technical problems",
                    "Drive technical strategy for the team",
                ],
                "supporting_data": {"role_level": developer.role_level.value},
            })

        return insights

    def save_insights(
        self, developer_id: int, insights: List[Dict[str, Any]], period_start: date, period_end: date
    ):
        """Save generated insights to database"""
        # Get organization_id for this developer (default to 1)
        developer = self.db.query(DeveloperProfile).filter(DeveloperProfile.id == developer_id).first()
        organization_id = developer.organization_id if developer else 1

        for insight_data in insights:
            # Validate insight_type — only use recognized enum values
            raw_type = insight_data.get("insight_type", "individual")
            try:
                insight_type = InsightType(raw_type)
            except ValueError:
                insight_type = InsightType.INDIVIDUAL

            # Store extra metadata inside supporting_data JSON
            supporting = dict(insight_data.get("supporting_data", {}))
            supporting["confidence"] = insight_data.get("confidence", 0.5)
            supporting["period_start"] = str(period_start)
            supporting["period_end"] = str(period_end)

            # Convert recommendations list to action_items format
            recs = insight_data.get("recommendations", [])
            action_items = [{"action": r, "assignee": "developer"} for r in recs]

            insight = AIInsight(
                organization_id=organization_id,
                developer_id=developer_id,
                insight_type=insight_type,
                title=insight_data["title"],
                description=insight_data["description"],
                supporting_data=supporting,
                action_items=action_items,
            )
            self.db.add(insight)

        self.db.commit()

    def get_recent_insights(
        self, developer_id: int, limit: int = 10
    ) -> List[AIInsight]:
        """Get recent insights for a developer"""
        return (
            self.db.query(AIInsight)
            .filter(AIInsight.developer_id == developer_id)
            .order_by(AIInsight.created_at.desc())
            .limit(limit)
            .all()
        )
