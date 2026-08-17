"""
Captain AI OS - Knowledge Base & Semantic Graph Memory (Volume 9 Part 9C)
Responsible for maintaining the 9 semantic relationship types (Parent, Child, Dependency,
Ownership, Temporal, Spatial, Causal, Similarity, Reference) across knowledge nodes.
"""

from typing import Dict, Any, List, Optional, Set
from enum import Enum
from pydantic import BaseModel, Field
import time


class RelationshipType(str, Enum):
    PARENT = "PARENT"
    CHILD = "CHILD"
    DEPENDENCY = "DEPENDENCY"
    OWNERSHIP = "OWNERSHIP"
    TEMPORAL = "TEMPORAL"
    SPATIAL = "SPATIAL"
    CAUSAL = "CAUSAL"
    SIMILARITY = "SIMILARITY"
    REFERENCE = "REFERENCE"


class KnowledgeNode(BaseModel):
    node_id: str
    label: str
    category: str
    properties: Dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=time.time)


class KnowledgeEdge(BaseModel):
    source_id: str
    target_id: str
    relation: RelationshipType
    weight: float = 1.0


class GraphMemory:
    """In-Memory & NetworkX graph engine for semantic entity-relationship traversal."""

    def __init__(self):
        self.nodes: Dict[str, KnowledgeNode] = {}
        self.edges: List[KnowledgeEdge] = []

    def add_node(self, node: KnowledgeNode) -> bool:
        """Adds a new entity node to the knowledge graph."""
        self.nodes[node.node_id] = node
        return True

    def add_edge(self, source_id: str, target_id: str, relation: RelationshipType, weight: float = 1.0) -> bool:
        """Connects two nodes with a semantic relationship edge."""
        if source_id not in self.nodes or target_id not in self.nodes:
            return False

        edge = KnowledgeEdge(source_id=source_id, target_id=target_id, relation=relation, weight=weight)
        self.edges.append(edge)
        return True

    def get_related_nodes(self, node_id: str, relation: Optional[RelationshipType] = None) -> List[KnowledgeNode]:
        """Finds all nodes directly connected to the specified node."""
        connected_ids = set()
        for edge in self.edges:
            if edge.source_id == node_id and (relation is None or edge.relation == relation):
                connected_ids.add(edge.target_id)
            elif edge.target_id == node_id and (relation is None or edge.relation == relation):
                connected_ids.add(edge.source_id)

        return [self.nodes[nid] for nid in connected_ids if nid in self.nodes]

    def traverse_path(self, start_id: str, depth: int = 2) -> List[str]:
        """Traverses the graph up to a maximum search depth."""
        visited: Set[str] = set()
        queue = [(start_id, 0)]

        while queue:
            curr_id, curr_depth = queue.pop(0)
            if curr_id in visited or curr_depth > depth:
                continue
            visited.add(curr_id)

            for edge in self.edges:
                if edge.source_id == curr_id and edge.target_id not in visited:
                    queue.append((edge.target_id, curr_depth + 1))
                elif edge.target_id == curr_id and edge.source_id not in visited:
                    queue.append((edge.source_id, curr_depth + 1))

        return list(visited)
