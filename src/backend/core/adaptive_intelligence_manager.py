"""
Captain AI OS - Adaptive Intelligence & Skill Acquisition System (Volume 12 Part 12B)
Responsible for capability gap detection, modular skill discovery, functional & security validation,
capability versioning, compatibility matrix evaluation, and backward-compatible rollbacks.
"""

from typing import Dict, Any, List, Optional
from enum import Enum
import time
from pydantic import BaseModel, Field
from src.backend.core.permission_manager import PermissionManager, Permission


class SkillStatus(str, Enum):
    DISCOVERED = "DISCOVERED"
    VALIDATING = "VALIDATING"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    DEPRECATED = "DEPRECATED"
    ROLLED_BACK = "ROLLED_BACK"


class CapabilityGap(BaseModel):
    gap_id: str
    task_description: str
    frequency_count: int = 1
    recommended_skill_name: str
    timestamp: float = Field(default_factory=time.time)


class SkillVersionRecord(BaseModel):
    version: int
    template_payload: Dict[str, Any]
    accuracy_score: float
    created_at: float = Field(default_factory=time.time)


class SkillRecord(BaseModel):
    skill_id: str
    name: str
    current_version: int = 1
    status: SkillStatus = SkillStatus.DISCOVERED
    accuracy_score: float = 0.0
    success_rate: float = 0.0
    compatibility_matrix: List[str] = Field(default_factory=lambda: ["AgentRegistry", "ToolManager"])
    version_history: List[SkillVersionRecord] = Field(default_factory=list)
    created_at: float = Field(default_factory=time.time)


class CompatibilityManager:
    """Verifies dependency compatibility across agents, tools, APIs, and memory models."""

    @staticmethod
    def verify_compatibility(skill: SkillRecord, target_subsystems: List[str]) -> bool:
        return all(sub in skill.compatibility_matrix for sub in target_subsystems)


class CapabilityAnalyzer:
    """Evaluates skill performance, accuracy, and operational success rates."""

    @staticmethod
    def evaluate(accuracy_score: float, success_rate: float) -> tuple[float, bool]:
        score = round((accuracy_score * 0.6) + (success_rate * 0.4), 2)
        is_viable = score >= 0.75
        return score, is_viable


class AdaptiveIntelligenceManager:
    """Centralized Manager for Skill Acquisition, Versioning & Adaptive Intelligence."""

    def __init__(self, validation_threshold: float = 0.75):
        self.validation_threshold = validation_threshold
        self.skills: Dict[str, SkillRecord] = {}
        self.gaps: List[CapabilityGap] = []
        self.permission_manager = PermissionManager()
        self.analytics = {
            "gaps_detected": 0,
            "skills_proposed": 0,
            "skills_activated": 0,
            "rollbacks_executed": 0
        }

    def detect_capability_gaps(self, unhandled_tasks: List[str]) -> List[CapabilityGap]:
        """Analyzes unhandled or failed task logs to detect missing capabilities."""
        detected = []
        task_counts: Dict[str, int] = {}
        for t in unhandled_tasks:
            task_counts[t] = task_counts.get(t, 0) + 1

        for task, count in task_counts.items():
            gap = CapabilityGap(
                gap_id=f"gap_{hash(task) & 0xffffff}",
                task_description=task,
                frequency_count=count,
                recommended_skill_name=f"Skill_Auto_{task.replace(' ', '_')}"
            )
            detected.append(gap)
            self.gaps.append(gap)

        self.analytics["gaps_detected"] += len(detected)
        return detected

    def propose_skill(
        self,
        skill_id: str,
        name: str,
        template_payload: Dict[str, Any],
        compatibility_subsystems: Optional[List[str]] = None
    ) -> SkillRecord:
        """Proposes a new modular skill and stores initial version record."""
        subsystems = compatibility_subsystems or ["AgentRegistry", "ToolManager"]
        initial_ver = SkillVersionRecord(version=1, template_payload=template_payload, accuracy_score=0.0)

        record = SkillRecord(
            skill_id=skill_id,
            name=name,
            current_version=1,
            status=SkillStatus.DISCOVERED,
            compatibility_matrix=subsystems,
            version_history=[initial_ver]
        )
        self.skills[skill_id] = record
        self.analytics["skills_proposed"] += 1
        return record

    def validate_and_activate(
        self,
        skill_id: str,
        accuracy_score: float,
        success_rate: float,
        target_subsystems: Optional[List[str]] = None
    ) -> bool:
        """Validates accuracy, success rate, and compatibility before activating skill."""
        if skill_id not in self.skills:
            raise KeyError(f"Skill '{skill_id}' not found.")

        skill = self.skills[skill_id]
        score, is_viable = CapabilityAnalyzer.evaluate(accuracy_score, success_rate)

        if not is_viable or score < self.validation_threshold:
            skill.status = SkillStatus.DEPRECATED
            raise ValueError(f"Skill evaluation score ({score}) below validation threshold ({self.validation_threshold}).")

        subsystems = target_subsystems or ["AgentRegistry", "ToolManager"]
        if not CompatibilityManager.verify_compatibility(skill, subsystems):
            skill.status = SkillStatus.DEPRECATED
            raise RuntimeError(f"Skill '{skill_id}' failed subsystem compatibility check.")

        skill.accuracy_score = accuracy_score
        skill.success_rate = success_rate
        skill.status = SkillStatus.ACTIVE
        self.analytics["skills_activated"] += 1
        return True

    def upgrade_skill(self, skill_id: str, new_template_payload: Dict[str, Any], accuracy_score: float) -> int:
        """Upgrades an active skill to a new version with changelog tracking."""
        if skill_id not in self.skills:
            raise KeyError(f"Skill '{skill_id}' not found.")

        skill = self.skills[skill_id]
        new_version = skill.current_version + 1
        ver_record = SkillVersionRecord(
            version=new_version,
            template_payload=new_template_payload,
            accuracy_score=accuracy_score
        )
        skill.version_history.append(ver_record)
        skill.current_version = new_version
        skill.accuracy_score = accuracy_score
        return new_version

    def rollback_skill(self, skill_id: str, target_version: int) -> bool:
        """Rolls back skill execution payload to a previous stable version."""
        if skill_id not in self.skills:
            return False

        skill = self.skills[skill_id]
        matching_versions = [v for v in skill.version_history if v.version == target_version]
        if not matching_versions:
            return False

        target_ver = matching_versions[0]
        skill.current_version = target_ver.version
        skill.accuracy_score = target_ver.accuracy_score
        skill.status = SkillStatus.ROLLED_BACK
        self.analytics["rollbacks_executed"] += 1
        return True

    def get_adaptive_analytics(self) -> Dict[str, Any]:
        """Returns analytics summary for skill acquisition and evolution velocity."""
        return {
            "total_skills": len(self.skills),
            "active_skills_count": sum(1 for s in self.skills.values() if s.status == SkillStatus.ACTIVE),
            "total_gaps_detected": len(self.gaps),
            "analytics_summary": self.analytics
        }
