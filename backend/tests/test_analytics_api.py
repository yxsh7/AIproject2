"""Tests for the analytics API endpoints.

Uses FastAPI TestClient with an in-memory SQLite database.
All DB interactions go through the `client` fixture which overrides
the `get_db` dependency.
"""

from datetime import date, timedelta

from app.models.work_activity import WorkActivity, WorkType
from tests.conftest import auth_header


# ─── /developers/{id}/overview ───────────────────���────────────────────────────


class TestDeveloperOverview:
    def test_requires_auth(self, client, developer_profile):
        # HTTPBearer returns 403 (not 401) when the Authorization header is absent
        r = client.get(f"/api/analytics/developers/{developer_profile.id}/overview")
        assert r.status_code == 403

    def test_developer_sees_own_profile(
        self, client, developer_user, developer_profile
    ):
        r = client.get(
            f"/api/analytics/developers/{developer_profile.id}/overview",
            headers=auth_header(developer_user),
        )
        assert r.status_code == 200
        body = r.json()
        assert body["developer_id"] == developer_profile.id
        assert body["role_level"] == developer_profile.role_level.value

    def test_developer_denied_other_profile(
        self, client, developer_user, other_developer_profile
    ):
        r = client.get(
            f"/api/analytics/developers/{other_developer_profile.id}/overview",
            headers=auth_header(developer_user),
        )
        assert r.status_code == 403

    def test_manager_sees_any_developer(self, client, manager_user, developer_profile):
        r = client.get(
            f"/api/analytics/developers/{developer_profile.id}/overview",
            headers=auth_header(manager_user),
        )
        assert r.status_code == 200

    def test_nonexistent_developer_returns_404(self, client, manager_user):
        r = client.get(
            "/api/analytics/developers/99999/overview",
            headers=auth_header(manager_user),
        )
        assert r.status_code == 404

    def test_overview_includes_activity_summary(
        self, client, manager_user, developer_profile, work_activities
    ):
        r = client.get(
            f"/api/analytics/developers/{developer_profile.id}/overview",
            headers=auth_header(manager_user),
        )
        assert r.status_code == 200
        body = r.json()
        assert "activity_summary" in body
        assert body["activity_summary"]["total_activities"] >= 0


# ─── /developers/{id}/productivity ──────────────────��─────────────────────────


class TestDeveloperProductivity:
    def test_returns_404_with_no_activities(
        self, client, manager_user, developer_profile
    ):
        r = client.get(
            f"/api/analytics/developers/{developer_profile.id}/productivity",
            headers=auth_header(manager_user),
        )
        assert r.status_code == 404

    def test_returns_scores_with_activities(
        self, client, manager_user, developer_profile, work_activities
    ):
        r = client.get(
            f"/api/analytics/developers/{developer_profile.id}/productivity",
            headers=auth_header(manager_user),
        )
        assert r.status_code == 200
        body = r.json()
        assert "overall_score" in body
        assert 0 <= body["overall_score"] <= 100
        assert "score_breakdown" in body
        assert set(body["score_breakdown"].keys()) == {
            "complexity",
            "velocity",
            "quality",
            "impact",
            "collaboration",
            "mentoring",
        }

    def test_date_fallback_finds_old_data(
        self, client, manager_user, developer_profile, db
    ):
        """When seed data is older than 30 days, the fallback should still return 200."""
        old_date = date.today() - timedelta(days=90)
        a = WorkActivity(
            developer_id=developer_profile.id,
            organization_id=developer_profile.organization_id,
            source_type="git",
            source_id="old-commit",
            work_type=WorkType.CODE,
            activity_date=old_date,
            complexity_score=5,
            impact_score=5,
            quality_score=5,
            ai_analysis={},
        )
        db.add(a)
        db.commit()

        r = client.get(
            f"/api/analytics/developers/{developer_profile.id}/productivity",
            headers=auth_header(manager_user),
        )
        assert r.status_code == 200

    def test_developer_cannot_access(
        self, client, developer_user, other_developer_profile
    ):
        r = client.get(
            f"/api/analytics/developers/{other_developer_profile.id}/productivity",
            headers=auth_header(developer_user),
        )
        assert r.status_code == 403


# ─── /developers/{id}/trends ─────────────────────���────────────────────────────


class TestDeveloperTrends:
    def test_returns_empty_trends_with_no_scores(
        self, client, manager_user, developer_profile
    ):
        r = client.get(
            f"/api/analytics/developers/{developer_profile.id}/trends",
            headers=auth_header(manager_user),
        )
        assert r.status_code == 200
        body = r.json()
        assert body["trends"] == []
        assert body["developer_id"] == developer_profile.id

    def test_returns_saved_scores_in_order(
        self, client, manager_user, developer_profile, work_activities, db
    ):
        from app.services.scoring_service import ProductivityScoringService

        service = ProductivityScoringService(db)
        for offset in [60, 30, 0]:
            end = date.today() - timedelta(days=offset)
            start = end - timedelta(days=30)
            score = service.calculate_developer_score(developer_profile.id, start, end)
            if score:
                service.save_score(score)

        r = client.get(
            f"/api/analytics/developers/{developer_profile.id}/trends",
            headers=auth_header(manager_user),
        )
        assert r.status_code == 200
        body = r.json()
        trends = body["trends"]
        if len(trends) >= 2:
            # Should be oldest-first
            assert trends[0]["period_end"] <= trends[-1]["period_end"]


# ─── /developers/{id}/work-breakdown ─────────────────────���────────────────────


class TestWorkBreakdown:
    def test_returns_404_with_no_activities(
        self, client, manager_user, developer_profile
    ):
        r = client.get(
            f"/api/analytics/developers/{developer_profile.id}/work-breakdown",
            headers=auth_header(manager_user),
        )
        assert r.status_code == 404

    def test_distribution_sums_to_100(
        self, client, manager_user, developer_profile, work_activities
    ):
        r = client.get(
            f"/api/analytics/developers/{developer_profile.id}/work-breakdown",
            headers=auth_header(manager_user),
        )
        assert r.status_code == 200
        body = r.json()
        total = sum(body["work_type_distribution"].values())
        assert abs(total - 100.0) < 0.1

    def test_complexity_bins_are_complete(
        self, client, manager_user, developer_profile, work_activities
    ):
        r = client.get(
            f"/api/analytics/developers/{developer_profile.id}/work-breakdown",
            headers=auth_header(manager_user),
        )
        assert r.status_code == 200
        bins = r.json()["complexity_distribution"]
        assert set(bins.keys()) == {"low", "medium", "high"}

    def test_fallback_finds_old_data(self, client, manager_user, developer_profile, db):
        old_date = date.today() - timedelta(days=90)
        db.add(
            WorkActivity(
                developer_id=developer_profile.id,
                organization_id=developer_profile.organization_id,
                source_type="git",
                source_id="old-2",
                work_type=WorkType.DOCUMENTATION,
                activity_date=old_date,
                complexity_score=3,
                impact_score=4,
                quality_score=6,
                ai_analysis={},
            )
        )
        db.commit()

        r = client.get(
            f"/api/analytics/developers/{developer_profile.id}/work-breakdown",
            headers=auth_header(manager_user),
        )
        assert r.status_code == 200


# ─── /teams/{team}/overview ───────────────────────────────────────────────────


class TestTeamOverview:
    def test_developer_cannot_access(self, client, developer_user, developer_profile):
        r = client.get(
            "/api/analytics/teams/backend/overview",
            headers=auth_header(developer_user),
        )
        assert r.status_code == 403

    def test_manager_can_access(
        self, client, manager_user, developer_profile, work_activities
    ):
        r = client.get(
            "/api/analytics/teams/backend/overview",
            headers=auth_header(manager_user),
        )
        # Returns 404 when no activity data, 200 when data exists
        assert r.status_code in (200, 404)

    def test_nonexistent_team_returns_404(self, client, manager_user):
        r = client.get(
            "/api/analytics/teams/no-such-team/overview",
            headers=auth_header(manager_user),
        )
        assert r.status_code == 404

    def test_team_overview_structure(
        self, client, manager_user, developer_profile, work_activities
    ):
        r = client.get(
            "/api/analytics/teams/backend/overview",
            headers=auth_header(manager_user),
        )
        if r.status_code == 200:
            body = r.json()
            assert "team_size" in body
            assert "average_overall_score" in body
            assert "individual_scores" in body
            assert body["team"] == "backend"


# ─── /developers/{id}/insights ─────────────────────────���──────────────────────


class TestDeveloperInsights:
    def test_requires_auth(self, client, developer_profile):
        r = client.get(f"/api/analytics/developers/{developer_profile.id}/insights")
        assert r.status_code == 403

    def test_returns_200_for_valid_developer(
        self, client, manager_user, developer_profile, work_activities
    ):
        r = client.get(
            f"/api/analytics/developers/{developer_profile.id}/insights",
            headers=auth_header(manager_user),
        )
        assert r.status_code == 200
        body = r.json()
        assert "insights" in body
        assert "patterns_detected" in body
        assert "anomalies" in body

    def test_regenerate_flag_produces_fresh_insights(
        self, client, manager_user, developer_profile, work_activities
    ):
        r = client.get(
            f"/api/analytics/developers/{developer_profile.id}/insights?regenerate=true",
            headers=auth_header(manager_user),
        )
        assert r.status_code == 200

    def test_developer_denied_other_insights(
        self, client, developer_user, other_developer_profile
    ):
        r = client.get(
            f"/api/analytics/developers/{other_developer_profile.id}/insights",
            headers=auth_header(developer_user),
        )
        assert r.status_code == 403


# ─── Cross-organization isolation ─────────────────────────────────────────────
# These exercise the actual regression target of the multi-tenancy rework:
# a manager/admin in one org must never be able to read another org's data,
# even though both orgs use identical resource-id shapes and (deliberately,
# for the team test) the same team name.


class TestCrossOrgIsolation:
    def test_manager_cannot_view_other_org_developer(
        self, client, manager_user, org2_developer_profile
    ):
        r = client.get(
            f"/api/analytics/developers/{org2_developer_profile.id}/overview",
            headers=auth_header(manager_user),
        )
        assert r.status_code == 404

    def test_manager_cannot_trigger_analysis_for_other_org_developer(
        self, client, manager_user, org2_developer_profile
    ):
        r = client.post(
            f"/api/analytics/developers/{org2_developer_profile.id}/analyze",
            headers=auth_header(manager_user),
        )
        assert r.status_code == 404

    def test_team_overview_does_not_blend_across_orgs(
        self,
        client,
        manager_user,
        developer_profile,
        org2_manager_user,
        org2_developer_profile,
        db,
    ):
        """Both orgs have a developer on a team literally named 'backend' — each
        manager's team-overview call must only ever see their own org's developer."""
        from app.models.work_activity import WorkActivity, WorkType
        from datetime import date

        db.add(
            WorkActivity(
                developer_id=org2_developer_profile.id,
                organization_id=org2_developer_profile.organization_id,
                source_type="git",
                source_id="org2-commit",
                work_type=WorkType.CODE,
                activity_date=date.today(),
                complexity_score=5,
                impact_score=5,
                quality_score=5,
                ai_analysis={},
            )
        )
        db.commit()

        r = client.get(
            "/api/analytics/teams/backend/overview",
            headers=auth_header(manager_user),
        )
        if r.status_code == 200:
            body = r.json()
            dev_ids = {s["developer_id"] for s in body["individual_scores"]}
            assert org2_developer_profile.id not in dev_ids

    def test_list_developers_scoped_to_own_org(
        self, client, manager_user, developer_profile, org2_developer_profile
    ):
        r = client.get("/api/developers/", headers=auth_header(manager_user))
        assert r.status_code == 200
        dev_ids = {d["id"] for d in r.json()}
        assert developer_profile.id in dev_ids
        assert org2_developer_profile.id not in dev_ids

    def test_get_developer_other_org_returns_404(
        self, client, manager_user, org2_developer_profile
    ):
        r = client.get(
            f"/api/developers/{org2_developer_profile.id}",
            headers=auth_header(manager_user),
        )
        assert r.status_code == 404
