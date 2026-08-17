"""
Unit & Integration Tests for Volume 12 Part 12C Decision Intelligence Architecture.
Verifies goal decomposition, constraint solving, strategy evaluation,
dynamic replanning, and explainable decision traces.
"""

import pytest
from src.backend.core.decision_intelligence_manager import (
    DecisionIntelligenceManager,
    PlanningState
)


def test_plan_generation_constraint_solving_and_selection():
    dim = DecisionIntelligenceManager()

    constraints = {"max_budget": 50.0}
    plan = dim.create_and_select_plan(
        goal="Deploy Microservice Container",
        context={"environment": "production"},
        constraints=constraints
    )

    assert plan.plan_id.startswith("plan_")
    assert plan.state == PlanningState.APPROVED
    assert plan.constraint_evaluation["budget_check"] is True
    assert len(plan.explanation_trace) > 0


def test_constraint_rejection():
    dim = DecisionIntelligenceManager()

    # Set budget lower than candidate plan step costs
    constraints = {"max_budget": 0.5}

    with pytest.raises(ValueError, match="No candidate plan satisfied mandatory system constraints."):
        dim.create_and_select_plan("Expensive Task", {}, constraints)


def test_dynamic_replanning_and_explanation():
    dim = DecisionIntelligenceManager()

    plan = dim.create_and_select_plan("Database Migration", {}, {"max_budget": 100.0})
    plan_id = plan.plan_id

    # Replan after step_2 failure
    replanned = dim.replan(plan_id, failed_step_id="step_2", new_context={"error": "connection_timeout"})
    assert replanned.state == PlanningState.APPROVED
    assert len(replanned.steps) == 4
    assert dim.analytics["replanning_events"] == 1

    # Verify decision explanation trace
    explanation = dim.explain_decision(plan_id)
    assert explanation["plan_id"] == plan_id
    assert any("Replanning triggered" in t for t in explanation["explanation_trace"])
