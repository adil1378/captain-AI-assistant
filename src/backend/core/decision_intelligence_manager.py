"""
Captain AI OS - Decision Intelligence, Reasoning & Planning System (Volume 12 Part 12C)
Responsible for multi-step reasoning, goal decomposition, constraint solving, candidate strategy evaluation,
dynamic replanning, and explainable decision traces.
"""

from typing import Dict, Any, List, Optional
from enum import Enum
import time
from pydantic import BaseModel, Field
from src.backend.core.permission_manager import PermissionManager, Permission


class ReasoningType(str, Enum):
    LOGICAL = "LOGICAL"
    CONTEXTUAL = "CONTEXTUAL"
    GOAL_ORIENTED = "GOAL_ORIENTED"
    CONSTRAINT_BASED = "CONSTRAINT_BASED"
    RISK_BASED = "RISK_BASED"
    MULTI_AGENT = "MULTI_AGENT"
    KNOWLEDGE_BASED = "KNOWLEDGE_BASED"
    HYBRID = "HYBRID"


class PlanningState(str, Enum):
    CREATED = "CREATED"
    CANDIDATES_GENERATED = "CANDIDATES_GENERATED"
    EVALUATED = "EVALUATED"
    APPROVED = "APPROVED"
    EXECUTING = "EXECUTING"
    REPLANNING = "REPLANNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class PlanStep(BaseModel):
    step_id: str
    title: str
    action: str
    dependencies: List[str] = Field(default_factory=list)
    estimated_cost: float = 1.0
    is_completed: bool = False


class ExecutionPlan(BaseModel):
    plan_id: str
    goal: str
    steps: List[PlanStep] = Field(default_factory=list)
    constraint_evaluation: Dict[str, bool] = Field(default_factory=dict)
    confidence_score: float = 0.0  # 0.0 to 1.0
    risk_score: float = 0.0  # 0.0 (low) to 10.0 (high)
    state: PlanningState = PlanningState.CREATED
    explanation_trace: List[str] = Field(default_factory=list)
    created_at: float = Field(default_factory=time.time)


class ConstraintSolver:
    """Evaluates candidate execution plans against resource, permission, and security constraints."""

    @staticmethod
    def solve(plan: ExecutionPlan, constraints: Dict[str, Any]) -> tuple[Dict[str, bool], bool]:
        eval_result = {}
        all_passed = True

        max_budget = constraints.get("max_budget", 100.0)
        total_cost = sum(s.estimated_cost for s in plan.steps)
        eval_result["budget_check"] = total_cost <= max_budget
        if not eval_result["budget_check"]:
            all_passed = False

        required_permission = constraints.get("required_permission")
        if required_permission:
            user_permission = constraints.get("user_permission")
            eval_result["permission_check"] = user_permission == required_permission
            if not eval_result["permission_check"]:
                all_passed = False
        else:
            eval_result["permission_check"] = True

        return eval_result, all_passed


class DecisionEvaluator:
    """Evaluates candidate plans and scores expected success, risk, and resource efficiency."""

    @staticmethod
    def evaluate(plan: ExecutionPlan) -> float:
        total_steps = len(plan.steps)
        step_score = min(1.0, total_steps / 5.0) * 0.4
        risk_penalty = (plan.risk_score / 10.0) * 0.3
        final_score = round(max(0.0, min(1.0, (plan.confidence_score * 0.6) + step_score - risk_penalty)), 2)
        return final_score


class DecisionIntelligenceManager:
    """Centralized Decision Intelligence, Reasoning & Planning Manager."""

    def __init__(self):
        self.plans: Dict[str, ExecutionPlan] = {}
        self.permission_manager = PermissionManager()
        self.analytics = {
            "plans_created": 0,
            "replanning_events": 0,
            "successful_plans": 0,
            "failed_plans": 0
        }

    def generate_candidate_plans(self, goal: str, context: Dict[str, Any]) -> List[ExecutionPlan]:
        """Decomposes goal into multi-step candidate execution plans."""
        p1 = ExecutionPlan(
            plan_id=f"plan_direct_{int(time.time() * 1000)}",
            goal=goal,
            steps=[
                PlanStep(step_id="step_1", title="Analyze Input", action="analyze"),
                PlanStep(step_id="step_2", title="Execute Core Logic", action="execute", dependencies=["step_1"])
            ],
            confidence_score=0.9,
            risk_score=2.0,
            explanation_trace=["Strategy 1: Direct 2-step execution path."]
        )

        p2 = ExecutionPlan(
            plan_id=f"plan_robust_{int(time.time() * 1000)}",
            goal=goal,
            steps=[
                PlanStep(step_id="step_1", title="Analyze Input", action="analyze"),
                PlanStep(step_id="step_2", title="Validate Subsystems", action="validate", dependencies=["step_1"]),
                PlanStep(step_id="step_3", title="Execute Core Logic with Verification", action="execute_verify", dependencies=["step_2"])
            ],
            confidence_score=0.95,
            risk_score=1.0,
            explanation_trace=["Strategy 2: Robust 3-step path with validation."]
        )

        return [p1, p2]

    def create_and_select_plan(self, goal: str, context: Dict[str, Any], constraints: Dict[str, Any]) -> ExecutionPlan:
        """Generates, solves constraints, evaluates, and selects optimal plan."""
        candidates = self.generate_candidate_plans(goal, context)
        valid_plans = []

        for plan in candidates:
            eval_map, passed = ConstraintSolver.solve(plan, constraints)
            plan.constraint_evaluation = eval_map
            if passed:
                valid_plans.append(plan)

        if not valid_plans:
            raise ValueError("No candidate plan satisfied mandatory system constraints.")

        # Select candidate with highest evaluation score
        best_plan = max(valid_plans, key=lambda p: DecisionEvaluator.evaluate(p))
        best_plan.state = PlanningState.APPROVED
        self.plans[best_plan.plan_id] = best_plan
        self.analytics["plans_created"] += 1
        return best_plan

    def replan(self, plan_id: str, failed_step_id: str, new_context: Dict[str, Any]) -> ExecutionPlan:
        """Dynamically replans execution while preserving completed steps."""
        if plan_id not in self.plans:
            raise KeyError(f"Execution plan '{plan_id}' not found.")

        plan = self.plans[plan_id]
        plan.state = PlanningState.REPLANNING
        plan.explanation_trace.append(f"Replanning triggered due to failure at '{failed_step_id}'.")

        # Mark completed steps
        for step in plan.steps:
            if step.step_id != failed_step_id:
                step.is_completed = True

        # Append recovery step
        recovery_step = PlanStep(
            step_id=f"rec_{failed_step_id}",
            title=f"Fallback Recovery for {failed_step_id}",
            action="fallback_execute"
        )
        plan.steps.append(recovery_step)
        plan.state = PlanningState.APPROVED
        self.analytics["replanning_events"] += 1
        return plan

    def explain_decision(self, plan_id: str) -> Dict[str, Any]:
        """Provides transparent explanation trace and constraint audit for a plan."""
        if plan_id not in self.plans:
            raise KeyError(f"Execution plan '{plan_id}' not found.")

        plan = self.plans[plan_id]
        return {
            "plan_id": plan.plan_id,
            "goal": plan.goal,
            "confidence_score": plan.confidence_score,
            "risk_score": plan.risk_score,
            "constraint_evaluation": plan.constraint_evaluation,
            "explanation_trace": plan.explanation_trace,
            "steps_count": len(plan.steps)
        }

    def get_decision_analytics(self) -> Dict[str, Any]:
        """Returns analytics summary for planning velocity and success rates."""
        return {
            "total_plans_managed": len(self.plans),
            "analytics_summary": self.analytics
        }
