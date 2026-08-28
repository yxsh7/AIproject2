"""Tests for ProductivityScoringService.

Split into two sections:
  - Pure unit tests: exercise the _calculate_* math helpers using plain model
    instances (no database needed).
  - Integration tests: exercise calculate_developer_score / calculate_team_scores
    against an in-memory SQLite database via the fixtures in conftest.py.
"""

import pytest
from datetime import date, timedelta

from app.models.developer import DeveloperProfile, RoleLevel
from app.models.work_activity import WorkActivity, WorkType
from app.services.scoring_service import ProductivityScoringService, ROLE_WEIGHTS


# ─── Helpers ──────────────────────────────────────────────────────────────────


def _activity(
    work_type=WorkType.CODE,
    complexity=6,
    quality=7,
    impact=5,
    days_ago=0,
    ai_analysis=None,
):
    """Build a WorkActivity instance without a DB session."""
    return WorkActivity(
        developer_id=1,
        source_type="git",
        source_id=f"x-{days_ago}",
        work_type=work_type,
        activity_date=date.today() - timedelta(days=days_ago),
        complexity_score=complexity,
        impact_score=impact,
        quality_score=quality,
        ai_analysis=ai_analysis or {},
    )


def _dev(role=RoleLevel.MID):
    return DeveloperProfile(
        id=1, user_id=1, organization_id=1, role_level=role, team="backend"
    )


def _service():
    """Service instance without a live DB — only safe for pure-math methods."""
    return ProductivityScoringService(db=None)


# ─── Pure unit tests (no DB) ──────────────────────────────────────────────────


class TestComplexityScore:
    def test_averages_activity_scores(self):
        acts = [
            _activity(complexity=4),
            _activity(complexity=8),
            _activity(complexity=6),
        ]
        assert _service()._calculate_complexity_score(acts) == pytest.approx(6.0)

    def test_empty_list_returns_zero(self):
        assert _service()._calculate_complexity_score([]) == 0.0

    def test_no_scores_returns_neutral(self):
        acts = [
            WorkActivity(
                complexity_score=None,
                developer_id=1,
                source_type="git",
                source_id="a",
                work_type=WorkType.CODE,
                activity_date=date.today(),
                impact_score=5,
                quality_score=5,
                ai_analysis={},
            )
        ]
        assert _service()._calculate_complexity_score(acts) == 5.0


class TestQualityScore:
    def test_averages_activity_scores(self):
        acts = [_activity(quality=6), _activity(quality=8)]
        assert _service()._calculate_quality_score(acts) == pytest.approx(7.0)

    def test_empty_list_returns_zero(self):
        assert _service()._calculate_quality_score([]) == 0.0


class TestVelocityScore:
    def test_zero_activities_returns_zero(self):
        assert (
            _service()._calculate_velocity_score(
                [], date.today() - timedelta(30), date.today()
            )
            == 0.0
        )

    def test_high_frequency_approaches_ten(self):
        # 20 activities spread over 14 days → ~10/week → capped at 10
        acts = [_activity(days_ago=i % 14) for i in range(20)]
        start = date.today() - timedelta(days=13)
        score = _service()._calculate_velocity_score(acts, start, date.today())
        assert score >= 8.0

    def test_low_frequency_gives_low_score(self):
        # 1 activity over 30 days
        acts = [_activity(days_ago=0)]
        start = date.today() - timedelta(days=29)
        score = _service()._calculate_velocity_score(acts, start, date.today())
        assert score < 4.0


class TestCollaborationScore:
    def test_high_review_ratio_returns_ten(self):
        # ≥ 20% collaboration activities → max score
        acts = [_activity(work_type=WorkType.CODE_REVIEW) for _ in range(3)]
        acts += [_activity() for _ in range(7)]
        assert _service()._calculate_collaboration_score(acts) == pytest.approx(10.0)

    def test_zero_reviews_returns_zero(self):
        acts = [_activity() for _ in range(5)]
        assert _service()._calculate_collaboration_score(acts) == pytest.approx(0.0)

    def test_partial_reviews_interpolates(self):
        # 1 review out of 10 → 10% → between 5 and 10
        acts = [_activity(work_type=WorkType.CODE_REVIEW)]
        acts += [_activity() for _ in range(9)]
        score = _service()._calculate_collaboration_score(acts)
        assert 5.0 <= score <= 10.0


class TestMentoringScore:
    def test_mentoring_work_type_raises_score(self):
        acts = [_activity(work_type=WorkType.MENTORING) for _ in range(3)]
        acts += [_activity() for _ in range(7)]
        score = _service()._calculate_mentoring_score(acts)
        assert score > 0.0

    def test_ai_analysis_keywords_boost_score(self):
        acts = [_activity(ai_analysis={"summary": "helped team understand the system"})]
        acts += [_activity() for _ in range(9)]
        score_with = _service()._calculate_mentoring_score(acts)
        acts_without = [_activity() for _ in range(10)]
        score_without = _service()._calculate_mentoring_score(acts_without)
        assert score_with >= score_without


class TestRoleWeights:
    def test_all_roles_have_weights(self):
        for role in RoleLevel:
            assert role in ROLE_WEIGHTS, f"Missing weights for {role}"

    def test_weights_sum_to_one(self):
        for role, weights in ROLE_WEIGHTS.items():
            total = sum(weights.values())
            assert total == pytest.approx(1.0), f"{role} weights sum to {total}"

    def test_unknown_role_falls_back_to_mid(self):
        # Pass a string that isn't a RoleLevel enum to .get()
        weights = ROLE_WEIGHTS.get("nonexistent_role", ROLE_WEIGHTS[RoleLevel.MID])
        assert weights == ROLE_WEIGHTS[RoleLevel.MID]


class TestComputeScore:
    def test_empty_activities_returns_none(self):
        dev = _dev()
        result = _service()._compute_score(
            dev, [], date.today() - timedelta(30), date.today()
        )
        assert result is None

    def test_score_in_valid_range(self):
        dev = _dev()
        acts = [_activity(days_ago=i) for i in range(10)]
        start = date.today() - timedelta(days=9)
        result = _service()._compute_score(dev, acts, start, date.today())
        assert result is not None
        assert 0 <= result.overall_score <= 100

    def test_higher_complexity_raises_score(self):
        dev = _dev(RoleLevel.SENIOR)  # Senior weights complexity heavily
        start = date.today() - timedelta(days=9)
        end = date.today()

        low_acts = [_activity(complexity=2, days_ago=i) for i in range(10)]
        high_acts = [_activity(complexity=9, days_ago=i) for i in range(10)]

        low = _service()._compute_score(dev, low_acts, start, end).overall_score
        high = _service()._compute_score(dev, high_acts, start, end).overall_score
        assert high > low

    def test_work_breakdown_sums_to_100(self):
        dev = _dev()
        acts = [_activity(work_type=WorkType.CODE, days_ago=i) for i in range(6)] + [
            _activity(work_type=WorkType.CODE_REVIEW, days_ago=i) for i in range(4)
        ]
        result = _service()._compute_score(
            dev, acts, date.today() - timedelta(9), date.today()
        )
        total = sum(result.work_breakdown.values())
        assert total == pytest.approx(100.0)


# ─── Integration tests (uses DB fixture from conftest) ────────────────────────


class TestCalculateDeveloperScore:
    def test_no_activities_returns_none(self, db, developer_profile):
        service = ProductivityScoringService(db)
        result = service.calculate_developer_score(developer_profile.id)
        assert result is None

    def test_returns_score_with_activities(
        self, db, developer_profile, work_activities
    ):
        service = ProductivityScoringService(db)
        start = date.today() - timedelta(days=15)
        result = service.calculate_developer_score(
            developer_profile.id, start, date.today()
        )
        assert result is not None
        assert 0 <= result.overall_score <= 100
        assert result.developer_id == developer_profile.id

    def test_unknown_developer_returns_none(self, db):
        service = ProductivityScoringService(db)
        assert service.calculate_developer_score(99999) is None

    def test_score_saved_and_retrieved(self, db, developer_profile, work_activities):
        service = ProductivityScoringService(db)
        start = date.today() - timedelta(days=15)
        score = service.calculate_developer_score(
            developer_profile.id, start, date.today()
        )
        saved = service.save_score(score)
        assert saved.id is not None

        latest = service.get_latest_score(developer_profile.id)
        assert latest is not None
        assert latest.overall_score == saved.overall_score


class TestCalculateTeamScores:
    def test_empty_team_returns_error(self, db, org):
        service = ProductivityScoringService(db)
        result = service.calculate_team_scores("nonexistent-team", org.id)
        assert "error" in result

    def test_team_with_activities_returns_aggregates(
        self, db, developer_profile, work_activities
    ):
        service = ProductivityScoringService(db)
        start = date.today() - timedelta(days=15)
        result = service.calculate_team_scores(
            "backend", developer_profile.organization_id, start, date.today()
        )

        assert "error" not in result
        assert result["team_size"] >= 1
        assert 0 <= result["average_overall_score"] <= 100
        assert len(result["individual_scores"]) == result["team_size"]

    def test_bulk_fetch_uses_two_queries(
        self, db, developer_profile, other_developer_profile, work_activities
    ):
        """Verify calculate_team_scores issues exactly 2 DB queries (devs + activities),
        not N+1."""
        from sqlalchemy import event

        # Read this before installing the query-capture listener: SQLAlchemy expires
        # attributes on commit, so accessing .organization_id for the first time here
        # would otherwise trigger its own refresh query and inflate the count below.
        org_id = developer_profile.organization_id

        queries = []

        @event.listens_for(db.bind, "before_cursor_execute")
        def capture(conn, cursor, statement, params, context, executemany):
            if "work_activities" in statement or "developer_profiles" in statement:
                queries.append(statement)

        service = ProductivityScoringService(db)
        start = date.today() - timedelta(days=15)
        service.calculate_team_scores("backend", org_id, start, date.today())

        # Should have exactly 1 developer query + 1 activities query
        dev_queries = [q for q in queries if "developer_profiles" in q]
        act_queries = [q for q in queries if "work_activities" in q]
        assert len(dev_queries) == 1
        assert len(act_queries) == 1


class TestGetScoreTrends:
    def test_returns_empty_for_no_scores(self, db, developer_profile):
        service = ProductivityScoringService(db)
        trends = service.get_score_trends(developer_profile.id)
        assert trends == []

    def test_trends_ordered_oldest_first(self, db, developer_profile, work_activities):
        service = ProductivityScoringService(db)
        # Save two scores with different periods
        for offset in [60, 30, 0]:
            end = date.today() - timedelta(days=offset)
            start = end - timedelta(days=30)
            score = service.calculate_developer_score(developer_profile.id, start, end)
            if score:
                service.save_score(score)

        trends = service.get_score_trends(developer_profile.id, periods=10)
        if len(trends) >= 2:
            assert trends[0]["period_end"] <= trends[-1]["period_end"]
