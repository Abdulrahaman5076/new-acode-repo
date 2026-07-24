Purpose: This is the only file that talks to the outside world. It handles failure gracefully, caches aggressively, and never crashes the application. The prompt is engineered for clarity, not technical showmanship.

---

### FILE 12: `ui_components.py`

```python
"""
Code Whisperer - UI Components
All Streamlit UI rendering functions live here.
Keeps app.py clean and focused on orchestration.
"""

import streamlit as st
import networkx as nx
import plotly.graph_objects as go
from typing import Dict
from parser import ParseResult
from graph_engine import GraphEngine
from impact_engine import ImpactReport
from security_engine import SecurityReport

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
def render_sidebar() -> str:
    with st.sidebar:
        st.header("⚙️ Settings")
        api_key = st.text_input(
            "Gemini API Key",
            type="password",
            help="Get a free key at aistudio.google.com",
            placeholder="Enter your Gemini API key..."
        )
        st.caption("Your key is never stored on our servers.")
        st.divider()
        st.header("📊 Stats")
        st.caption("Session analysis count: Coming soon")
        st.divider()
        st.caption("Code Whisperer v1.0")
    return api_key

# ---------------------------------------------------------------------------
# Code Input
# ---------------------------------------------------------------------------
def render_code_input() -> str:
    return st.text_area(
        "Paste your AI-generated code:",
        height=300,
        placeholder="# Paste your Python or JavaScript code here...\n\ndef main():\n    print('Hello World')\n",
        help="Supports Python, JavaScript, and TypeScript."
    )

# ---------------------------------------------------------------------------
# Results Tabs
# ---------------------------------------------------------------------------
def render_results(
    parsed: ParseResult,
    G: nx.DiGraph,
    engine: GraphEngine,
):
    st.success(f"✅ Parsed successfully: {len(parsed.functions)} functions, {len(parsed.classes)} classes, {parsed.total_lines} lines")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Overview",
        "🔗 Dependency Graph",
        "💥 Impact Simulator",
        "🔒 Security Report",
    ])
    
    with tab1:
        _render_overview(parsed, G, engine)
    
    with tab2:
        _render_graph(G)
    
    with tab3:
        _render_impact(parsed, G, engine)
    
    with tab4:
        _render_security(parsed)

def _render_overview(parsed: ParseResult, G: nx.DiGraph, engine: GraphEngine):
    col1, col2, col3 = st.columns(3)
    col1.metric("Functions", len(parsed.functions))
    col2.metric("Classes", len(parsed.classes))
    col3.metric("Lines of Code", parsed.total_lines)
    
    st.divider()
    
    if parsed.entry_points:
        st.subheader("🚪 Entry Points (Start Here)")
        for ep in parsed.entry_points:
            st.markdown(f"- `{ep}()`")
    
    if parsed.orphans:
        st.subheader("👻 Orphan Functions (Possibly Unused)")
        for orphan in parsed.orphans:
            st.markdown(f"- `{orphan}()`")
    
    # Most important functions
    centrality = engine.get_centrality(G)
    if centrality:
        st.subheader("⭐ Most Connected Functions")
        for func, score in centrality[:5]:
            st.markdown(f"- `{func}()` — centrality: {score:.3f}")

def _render_graph(G: nx.DiGraph):
    if G.number_of_nodes() == 0:
        st.info("No function calls detected to visualize.")
        return
    
    # Create Plotly network graph
    pos = nx.spring_layout(G, seed=42)
    
    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='#888'),
        hoverinfo='none',
        mode='lines'
    )
    
    node_x, node_y, node_text = [], [], []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_text,
        textposition="top center",
        hoverinfo='text',
        marker=dict(size=20, color='#1f77b4', line=dict(width=2, color='#333')),
        textfont=dict(size=10),
    )
    
    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20, l=5, r=5, t=40),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    ))
    
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Interactive graph: Functions are nodes, calls are edges. Zoom and pan to explore.")

def _render_impact(parsed: ParseResult, G: nx.DiGraph, engine: GraphEngine):
    if not parsed.functions:
        st.info("No functions to analyze.")
        return
    
    target = st.selectbox(
        "What happens if I change this function?",
        [f.name for f in parsed.functions],
        key="impact_select"
    )
    
    if target:
        report = ImpactReport.create(G, target, engine.get_upstream, engine.get_downstream, engine.get_direct_dependents)
        
        st.markdown(f"### {report.summary}")
        
        col1, col2 = st.columns(2)
        with col1:
            if report.direct_dependents:
                st.warning(f"**Directly depends on this ({len(report.direct_dependents)}):**")
                for dep in report.direct_dependents:
                    st.markdown(f"- `{dep}()`")
            else:
                st.success("No functions directly depend on this.")
        
        with col2:
            if report.dependencies:
                st.info(f"**This depends on ({len(report.dependencies)}):**")
                for dep in report.dependencies[:10]:
                    st.markdown(f"- `{dep}()`")
                if len(report.dependencies) > 10:
                    st.caption(f"...and {len(report.dependencies) - 10} more")
            else:
                st.success("This function calls nothing else.")

def _render_security(parsed: ParseResult):
    from security_engine import SecurityScanner
    scanner = SecurityScanner()
    report = scanner.scan(parsed.raw_code) if hasattr(parsed, 'raw_code') else SecurityReport()
    
    if report.is_clean:
        st.success("✅ No security issues detected.")
    else:
        st.error(f"Found {len(report.issues)} potential security issue(s)")
        
        for issue in report.issues:
            severity_color = {
                "CRITICAL": "red",
                "HIGH": "orange",
                "MEDIUM": "yellow",
                "LOW": "blue",
            }.get(issue.severity, "gray")
            
            with st.expander(f"{issue.severity}: {issue.category} (Line {issue.line})"):
                st.markdown(f"**Issue:** {issue.description}")
                st.markdown(f"**Fix:** {issue.suggestion}")