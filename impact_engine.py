"""
Code Whisperer - Impact Engine
Answers the question: "What happens if I change X?"
"""

from dataclasses import dataclass
from typing import List
import networkx as nx

@dataclass
class ImpactReport:
    function_name: str
    risk_level: str          # LOW, MEDIUM, HIGH, ORPHAN
    direct_dependents: List[str]
    all_dependents: List[str]
    dependencies: List[str]
    summary: str
    
    @classmethod
    def create(cls, G: nx.DiGraph, target: str, get_upstream, get_downstream, get_direct):
        if target not in G:
            return cls(
                function_name=target,
                risk_level="UNKNOWN",
                direct_dependents=[],
                all_dependents=[],
                dependencies=[],
                summary=f"Function '{target}' not found in codebase."
            )
        
        direct = get_direct(G, target)
        all_deps = get_upstream(G, target)
        downstream = get_downstream(G, target)
        
        risk = "LOW"
        if len(all_deps) > 5:
            risk = "HIGH"
        elif len(direct) > 0:
            risk = "MEDIUM"
        elif len(downstream) == 0 and len(direct) == 0:
            risk = "ORPHAN"
        
        summary = cls._build_summary(target, risk, direct, all_deps, downstream)
        
        return cls(
            function_name=target,
            risk_level=risk,
            direct_dependents=direct,
            all_dependents=all_deps,
            dependencies=downstream,
            summary=summary,
        )
    
    @staticmethod
    def _build_summary(name, risk, direct, all_deps, downstream):
        if risk == "ORPHAN":
            return f"{name} is unused. Safe to remove."
        elif risk == "HIGH":
            return f"⚠️ HIGH RISK: {name} affects {len(all_deps)} functions. Change with caution."
        elif risk == "MEDIUM":
            return f"⚡ MEDIUM RISK: {name} is called by {len(direct)} function(s)."
        else:
            if not downstream and not direct:
                return f"✅ {name} is an entry point. Safe to modify."
            return f"✅ LOW RISK: {name} has minimal dependencies."