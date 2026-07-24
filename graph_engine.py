"""
Code Whisperer - Graph Engine
Builds and queries the dependency graph using NetworkX.
Reveals hidden connections between functions.
"""

import networkx as nx
from typing import List, Optional
from parser import ParseResult

class GraphEngine:
    """
    Wraps NetworkX to build and query function dependency graphs.
    """
    
    def build(self, parsed: ParseResult) -> nx.DiGraph:
        G = nx.DiGraph()
        
        for func in parsed.functions:
            G.add_node(func.name, complexity=func.complexity, line=func.line)
        
        for caller, callees in parsed.call_graph.items():
            if G.has_node(caller):
                for callee in callees:
                    if G.has_node(callee):
                        G.add_edge(caller, callee)
        
        return G
    
    def get_upstream(self, G: nx.DiGraph, node: str) -> List[str]:
        """Who depends on this function?"""
        if node not in G:
            return []
        return list(nx.ancestors(G, node))
    
    def get_downstream(self, G: nx.DiGraph, node: str) -> List[str]:
        """What does this function depend on?"""
        if node not in G:
            return []
        return list(nx.descendants(G, node))
    
    def get_direct_dependents(self, G: nx.DiGraph, node: str) -> List[str]:
        if node not in G:
            return []
        return list(G.predecessors(node))
    
    def get_centrality(self, G: nx.DiGraph) -> List[tuple]:
        """Returns functions ranked by importance (betweenness centrality)."""
        if G.number_of_nodes() == 0:
            return []
        centrality = nx.betweenness_centrality(G)
        return sorted(centrality.items(), key=lambda x: x[1], reverse=True)