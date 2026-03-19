"""Background tasks for AI analysis of code and work activities"""
import logging

from app.tasks.celery_app import celery_app
from app.database import SessionLocal
from app.models import GitCommit, JiraTicket, WorkActivity, WorkType, DeveloperProfile, CodeReview
from app.ai.agents.code_analyzer import CodeComplexityAnalyzer
from app.ai.agents.work_classifier import WorkTypeClassifier
from app.ai.agents.review_quality_analyzer import ReviewQualityAnalyzer

logger = logging.getLogger(__name__)


def _safe_work_type(work_type_str: str) -> WorkType:
    """Map AI work type string to WorkType enum, handling unknown values gracefully"""
    try:
        return WorkType(work_type_str)
    except ValueError:
        mapping = {
            "feature": WorkType.CODE,
            "code": WorkType.CODE,
            "bug_fix": WorkType.BUG_FIX,
            "refactoring": WorkType.REFACTORING,
            "documentation": WorkType.DOCUMENTATION,
            "testing": WorkType.TESTING,
            "research": WorkType.RESEARCH,
            "mentoring": WorkType.MENTORING,
            "config": WorkType.CODE,
            "other": WorkType.OTHER,
            "code_review": WorkType.CODE_REVIEW,
            "dashboard": WorkType.DASHBOARD,
            "operations": WorkType.OPERATIONS,
            "design": WorkType.DESIGN,
            "meeting": WorkType.MEETING,
        }
        return mapping.get(work_type_str.lower(), WorkType.CODE)


def get_db():
    """Get database session for tasks"""
    db = SessionLocal()
    return db


@celery_app.task(name="app.tasks.analysis_tasks.analyze_git_commits")
def analyze_git_commits(developer_id: int, limit: int = 100):
    """
    Analyze unanalyzed Git commits for a developer using AI

    Args:
        developer_id: Developer profile ID
        limit: Max number of commits to analyze

    Returns:
        Dict with analysis results
    """
    db = get_db()

    try:
        # Get developer
        developer = (
            db.query(DeveloperProfile)
            .filter(DeveloperProfile.id == developer_id)
            .first()
        )

        if not developer:
            return {"error": "Developer not found"}

        # Get unanalyzed commits
        commits = (
            db.query(GitCommit)
            .filter(
                GitCommit.developer_id == developer_id,
                GitCommit.analyzed == False,
            )
            .order_by(GitCommit.committed_at.desc())
            .limit(limit)
            .all()
        )

        if not commits:
            logger.info(f"No unanalyzed commits found for developer {developer_id}")
            return {"analyzed_count": 0}

        logger.info(f"Analyzing {len(commits)} commits for developer {developer.github_username}")

        # Initialize AI analyzer
        analyzer = CodeComplexityAnalyzer()

        analyzed_count = 0
        work_activities_created = 0

        for commit in commits:
            try:
                # Dedup: skip if WorkActivity already exists for this source
                existing = db.query(WorkActivity).filter_by(
                    developer_id=developer_id,
                    source_type="git",
                    source_id=str(commit.id),
                ).first()
                if existing:
                    commit.analyzed = True
                    continue

                # Analyze commit
                analysis = analyzer.analyze_commit(
                    commit_message=commit.message,
                    files_changed=commit.files_changed,
                    additions=commit.additions,
                    deletions=commit.deletions,
                    diff=None,
                )

                # Save analysis result
                commit.analysis_result = analysis
                commit.analyzed = True

                # Create work activity
                # support both old "impact_level" and new "impact" key names
                impact_str = analysis.get("impact", analysis.get("impact_level", "medium"))
                work_activity = WorkActivity(
                    developer_id=developer_id,
                    activity_date=commit.committed_at.date(),
                    work_type=_safe_work_type(analysis.get("work_type", "feature")),
                    complexity_score=analysis["complexity_score"],
                    impact_score=_map_impact_to_score(impact_str),
                    quality_score=analysis["quality_score"],
                    time_estimate_hours=_estimate_time_from_complexity(
                        analysis["complexity_score"]
                    ),
                    source_type="git",
                    source_id=str(commit.id),
                    ai_analysis={
                        "commit_sha": commit.commit_sha,
                        "repo": commit.repo_name,
                        "message": commit.message,
                        **analysis,
                    },
                    artifacts=[
                        {
                            "type": "commit",
                            "sha": commit.commit_sha,
                            "repo": commit.repo_name,
                            "url": f"https://github.com/{commit.repo_name}/commit/{commit.commit_sha}",
                        }
                    ],
                )

                db.add(work_activity)
                work_activities_created += 1
                analyzed_count += 1

                # Commit in batches
                if analyzed_count % 10 == 0:
                    db.commit()
                    logger.info(f"Analyzed {analyzed_count} commits so far...")

            except Exception as e:
                logger.error(f"Error analyzing commit {commit.id}: {e}")
                continue

        # Final commit
        db.commit()

        logger.info(
            f"Successfully analyzed {analyzed_count} commits, "
            f"created {work_activities_created} work activities"
        )

        return {
            "analyzed_count": analyzed_count,
            "work_activities_created": work_activities_created,
        }

    except Exception as e:
        logger.error(f"Error in analyze_git_commits: {e}")
        return {"error": str(e)}

    finally:
        db.close()


@celery_app.task(name="app.tasks.analysis_tasks.analyze_jira_tickets")
def analyze_jira_tickets(developer_id: int, limit: int = 100):
    """
    Analyze unanalyzed Jira tickets for a developer using AI

    Args:
        developer_id: Developer profile ID
        limit: Max number of tickets to analyze

    Returns:
        Dict with analysis results
    """
    db = get_db()

    try:
        # Get developer
        developer = (
            db.query(DeveloperProfile)
            .filter(DeveloperProfile.id == developer_id)
            .first()
        )

        if not developer:
            return {"error": "Developer not found"}

        # Get unanalyzed tickets
        tickets = (
            db.query(JiraTicket)
            .filter(
                JiraTicket.developer_id == developer_id,
                JiraTicket.analyzed == False,
            )
            .order_by(JiraTicket.created_at.desc())
            .limit(limit)
            .all()
        )

        if not tickets:
            logger.info(f"No unanalyzed tickets found for developer {developer_id}")
            return {"analyzed_count": 0}

        logger.info(f"Analyzing {len(tickets)} tickets for developer {developer.jira_username}")

        # Initialize AI classifier
        classifier = WorkTypeClassifier()

        analyzed_count = 0
        work_activities_created = 0

        for ticket in tickets:
            try:
                # Dedup: skip if WorkActivity already exists for this source
                existing = db.query(WorkActivity).filter_by(
                    developer_id=developer_id,
                    source_type="jira",
                    source_id=str(ticket.id),
                ).first()
                if existing:
                    ticket.analyzed = True
                    continue

                # Get ticket comments
                comments = [comment.comment_text for comment in ticket.comments]

                # Classify ticket
                classification = classifier.classify_ticket(
                    ticket_key=ticket.ticket_key,
                    title=ticket.title,
                    ticket_type=ticket.ticket_type,
                    description=ticket.description,
                    comments=comments,
                    status=ticket.status,
                )

                # Save classification result
                ticket.analysis_result = classification
                ticket.analyzed = True

                # Create work activity
                work_activity = WorkActivity(
                    developer_id=developer_id,
                    activity_date=ticket.created_at.date(),
                    work_type=_safe_work_type(classification.get("work_type", "code")),
                    complexity_score=classification["complexity_score"],
                    impact_score=classification["impact_score"],
                    quality_score=7,  # Default for Jira tickets
                    time_estimate_hours=classification["time_estimate_hours"],
                    source_type="jira",
                    source_id=str(ticket.id),
                    ai_analysis={
                        "ticket_key": ticket.ticket_key,
                        "title": ticket.title,
                        **classification,
                    },
                    artifacts=classification.get("artifacts", []),
                )

                db.add(work_activity)
                work_activities_created += 1
                analyzed_count += 1

                # Commit in batches
                if analyzed_count % 10 == 0:
                    db.commit()
                    logger.info(f"Analyzed {analyzed_count} tickets so far...")

            except Exception as e:
                logger.error(f"Error analyzing ticket {ticket.id}: {e}")
                continue

        # Final commit
        db.commit()

        logger.info(
            f"Successfully analyzed {analyzed_count} tickets, "
            f"created {work_activities_created} work activities"
        )

        return {
            "analyzed_count": analyzed_count,
            "work_activities_created": work_activities_created,
        }

    except Exception as e:
        logger.error(f"Error in analyze_jira_tickets: {e}")
        return {"error": str(e)}

    finally:
        db.close()


@celery_app.task(name="app.tasks.analysis_tasks.analyze_code_reviews")
def analyze_code_reviews(developer_id: int, limit: int = 100):
    """
    Analyze code review quality for a developer using AI.

    Only processes reviews that have raw_comments stored in analysis_result
    (populated by github_service.sync_code_reviews_for_developer).
    Updates quality_score on CodeReview records and creates WorkActivity
    entries (source_type='git_review') with dedup protection.

    Args:
        developer_id: Developer profile ID
        limit: Max number of reviews to analyze

    Returns:
        Dict with analyzed_count
    """
    db = get_db()

    try:
        developer = db.query(DeveloperProfile).filter(DeveloperProfile.id == developer_id).first()
        if not developer:
            return {"error": "Developer not found"}

        # Fetch reviews with null quality_score
        reviews_query = (
            db.query(CodeReview)
            .filter(
                CodeReview.reviewer_id == developer_id,
                CodeReview.quality_score == None,
            )
            .order_by(CodeReview.reviewed_at.desc())
            .limit(limit)
            .all()
        )

        # Filter in Python: only reviews that have raw_comments stored
        reviews = [
            r for r in reviews_query
            if r.analysis_result and "raw_comments" in r.analysis_result
        ]

        if not reviews:
            return {"analyzed_count": 0}

        analyzer = ReviewQualityAnalyzer()
        analyzed_count = 0

        for review in reviews:
            try:
                comments = review.analysis_result.get("raw_comments", [])
                result = analyzer.analyze_review(
                    reviewer_username=developer.github_username or "",
                    pr_title="",
                    review_state=review.review_state or "commented",
                    comments=comments,
                )

                # Update quality score on the review record — always refreshed on re-analysis
                review.quality_score = round(result["quality_score"])
                review.analysis_result = {**review.analysis_result, **result}

                # Dedup check
                existing = db.query(WorkActivity).filter_by(
                    developer_id=developer_id,
                    source_type="git_review",
                    source_id=str(review.id),
                ).first()

                if not existing:
                    work_activity = WorkActivity(
                        developer_id=developer_id,
                        activity_date=review.reviewed_at.date(),
                        work_type=WorkType.CODE_REVIEW,
                        complexity_score=5,
                        impact_score=5,
                        quality_score=round(result["quality_score"]),
                        time_estimate_hours=1,
                        source_type="git_review",
                        source_id=str(review.id),
                        ai_analysis=result,
                        artifacts=[],
                    )
                    db.add(work_activity)

                analyzed_count += 1

                if analyzed_count % 10 == 0:
                    db.commit()

            except Exception as e:
                logger.error(f"Error analyzing review {review.id}: {e}")
                continue

        db.commit()
        return {"analyzed_count": analyzed_count}

    except Exception as e:
        logger.error(f"Error in analyze_code_reviews: {e}")
        return {"error": str(e)}
    finally:
        db.close()


@celery_app.task(name="app.tasks.analysis_tasks.analyze_all_unanalyzed")
def analyze_all_unanalyzed():
    """
    Periodic task to analyze all unanalyzed commits and tickets
    """
    db = get_db()

    try:
        # Get all developers
        developers = db.query(DeveloperProfile).all()

        logger.info(f"Running AI analysis for {len(developers)} developers")

        total_commits = 0
        total_tickets = 0

        for developer in developers:
            try:
                # Analyze commits
                commit_result = analyze_git_commits.delay(developer.id, limit=50)
                total_commits += 1

                # Analyze tickets
                ticket_result = analyze_jira_tickets.delay(developer.id, limit=50)
                total_tickets += 1

                # Analyze code reviews
                analyze_code_reviews.delay(developer.id, limit=50)

            except Exception as e:
                logger.error(f"Error triggering analysis for developer {developer.id}: {e}")
                continue

        return {
            "developers_processed": len(developers),
            "commit_tasks_triggered": total_commits,
            "ticket_tasks_triggered": total_tickets,
        }

    finally:
        db.close()


# Helper functions


def _map_impact_to_score(impact_level: str) -> int:
    """Map impact level to score (0-10)"""
    mapping = {
        "low": 3,
        "medium": 6,
        "high": 9,
        "critical": 10,
    }
    return mapping.get(impact_level.lower(), 5)


def _estimate_time_from_complexity(complexity_score: int) -> int:
    """Estimate time in hours from complexity score"""
    # Very rough estimation
    if complexity_score <= 3:
        return 1
    elif complexity_score <= 5:
        return 2
    elif complexity_score <= 7:
        return 4
    else:
        return 8
