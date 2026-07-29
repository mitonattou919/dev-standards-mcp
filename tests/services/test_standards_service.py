import pytest

from src.services.standards_service import StandardsService


def test_search_standards_delegates_to_search_backend(standards_service: StandardsService) -> None:
    results = standards_service.search_standards("共通ルール")

    assert [result.id for result in results] == ["standard-all-python"]
    assert isinstance(results[0].score, float)


def test_get_standard_returns_body(standards_service: StandardsService) -> None:
    body = standards_service.get_standard("standard-all-python")

    assert body == "Pythonプロジェクト全体に適用する共通ルールを定める。"


def test_get_standard_raises_when_missing(standards_service: StandardsService) -> None:
    with pytest.raises(ValueError, match="standard not found: does-not-exist"):
        standards_service.get_standard("does-not-exist")


def test_get_applicable_standards_infers_technology_from_files(
    standards_service: StandardsService,
) -> None:
    result = standards_service.get_applicable_standards(project="backend", files=["app.py"], task="")

    assert [s.id for s in result.must] == ["standard-all-python"]
    assert result.should == []
    assert [s.id for s in result.reference] == ["standard-general-reference"]


def test_get_applicable_standards_infers_technology_from_task(
    standards_service: StandardsService,
) -> None:
    result = standards_service.get_applicable_standards(
        project="backend", files=[], task="azureのリソースを作成する仕事です"
    )

    assert result.must == []
    assert [s.id for s in result.should] == ["standard-backend-azure"]
    assert [s.id for s in result.reference] == ["standard-general-reference"]


def test_get_applicable_standards_without_technology_signal_skips_tech_filter(
    standards_service: StandardsService,
) -> None:
    result = standards_service.get_applicable_standards(project="backend", files=[], task="")

    assert [s.id for s in result.must] == ["standard-all-python"]
    assert [s.id for s in result.should] == ["standard-backend-azure"]
    assert [s.id for s in result.reference] == ["standard-general-reference"]


def test_get_applicable_standards_filters_by_project(standards_service: StandardsService) -> None:
    result = standards_service.get_applicable_standards(project="mobile", files=[], task="")

    assert [s.id for s in result.must] == ["standard-all-python"]
    assert result.should == []
    assert [s.id for s in result.reference] == ["standard-general-reference"]


def test_get_applicable_standards_excludes_may_and_inactive(
    standards_service: StandardsService,
) -> None:
    result = standards_service.get_applicable_standards(project="all-projects", files=["app.py"], task="")

    all_ids = {s.id for s in result.must + result.should + result.reference}
    assert "standard-optional-python" not in all_ids
    assert "standard-inactive" not in all_ids


def test_get_review_checklist_returns_only_checklist_documents(
    standards_service: StandardsService,
) -> None:
    checklist = standards_service.get_review_checklist()

    assert [item.id for item in checklist] == ["checklist-service-test"]
    assert checklist[0].body == "- [ ] チェック項目1\n- [ ] チェック項目2"
