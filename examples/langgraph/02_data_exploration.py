#!/usr/bin/env python3
"""
Data Exploration Workflow with State and Conditionals

Advanced workflow demonstrating:
- Conditional branching (DataStore vs CSV)
- State persistence across decisions
- Human-in-the-loop for resource selection
- SQL queries on DataStore resources

Run:
    python 02_data_exploration.py
"""

import asyncio
import json
import os
from typing import Annotated, Literal

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


# Configuration
CKAN_SERVER = "https://www.dati.gov.it/opendata"
MCP_SERVER_PATH = os.path.join(os.path.dirname(__file__), "../../dist/index.js")
SEARCH_ROWS = 5  # Markdown format handles truncation gracefully
    # Note: Some queries return very large metadata. Use specific queries like "trasporti"
# instead of generic ones like "CSV" or "popolazione" to avoid JSON truncation.


# State definition
class ExplorationState(dict):
    """State for data exploration workflow."""

    messages: Annotated[list, add_messages]
    query: str
    datasets: list[dict]
    selected_dataset: dict | None
    selected_resource: dict | None
    resource_type: Literal["datastore", "csv", "unknown"] | None
    analysis_result: dict | None
    error: str | None


# MCP Client
class CKANMCPClient:
    """Helper for CKAN MCP operations."""

    def __init__(self, session: ClientSession):
        self.session = session

    async def search_packages(self, query: str, rows: int = SEARCH_ROWS) -> dict:
        """Search packages."""
        result = await self.session.call_tool(
            "ckan_package_search",
            arguments={
                "server_url": CKAN_SERVER,
                "q": query,
                "rows": rows,
                "response_format": "json",
            },
        )
        for content in result.content:
            if content.type == "text":
                try:
                    text = content.text
                    if "[Response truncated" in text:
                        text = text.split("[Response truncated")[0].strip()
                    return json.loads(text)
                except json.JSONDecodeError as e:
                    return {"error": f"JSON parse error: {e}"}
        return {"error": "No content in response"}

    async def datastore_search(self, resource_id: str, limit: int = 3) -> dict:
        """Query DataStore."""
        result = await self.session.call_tool(
            "ckan_datastore_search",
            arguments={
                "server_url": CKAN_SERVER,
                "resource_id": resource_id,
                "limit": limit,
                "response_format": "json",
            },
        )
        for content in result.content:
            if content.type == "text":
                try:
                    text = content.text
                    if "[Response truncated" in text:
                        text = text.split("[Response truncated")[0].strip()
                    return json.loads(text)
                except json.JSONDecodeError as e:
                    return {"error": f"JSON parse error: {e}"}
        return {"error": "No content in response"}


# Workflow nodes
async def search_node(
    state: ExplorationState, mcp_client: CKANMCPClient
) -> ExplorationState:
    """Search for datasets."""
    print(f"\n[SEARCH] Query: '{state['query']}'")

    try:
        response = await mcp_client.search_packages(state["query"])

        if "error" in response:
            state["error"] = response["error"]
            print(f"   ✗ Error: {response['error']}")
            return state

        if "results" in response:
            datasets = response["results"]
            state["datasets"] = datasets
            print(
                f"   ✓ Found {response.get('count', len(datasets))} total, showing {len(datasets)}"
            )
        else:
            state["error"] = "Unexpected response structure"

    except Exception as e:
        state["error"] = str(e)
        print(f"   ✗ Error: {e}")

    return state


async def select_dataset_node(state: ExplorationState) -> ExplorationState:
    """Human-in-the-loop: select dataset."""
    print("\n[SELECT DATASET] Available datasets:")

    if state.get("error") or not state.get("datasets"):
        return state

    # Show top 3 datasets
    for i, ds in enumerate(state["datasets"][:3], 1):
        print(f"\n{i}. {ds['title']}")
        print(f"   Resources: {ds.get('num_resources', 0)}")
        print(f"   Org: {ds.get('organization', {}).get('title', 'N/A')}")

    # Simulate user selection (in real app, use input())
    selection = 0  # Select first
    state["selected_dataset"] = state["datasets"][selection]
    print(f"\n   → Selected: {state['selected_dataset']['title']}")

    return state


async def select_resource_node(state: ExplorationState) -> ExplorationState:
    """Select resource and detect type."""
    print("\n[SELECT RESOURCE]")

    if state.get("error") or not state.get("selected_dataset"):
        return state

    resources = state["selected_dataset"].get("resources", [])
    if not resources:
        state["error"] = "No resources available"
        return state

    print("Available resources:")
    for i, res in enumerate(resources[:3], 1):
        print(f"{i}. {res.get('name', 'Untitled')} ({res.get('format', 'N/A')})")

    # Select first resource
    selected = resources[0]
    state["selected_resource"] = selected

    # Detect type
    if selected.get("datastore_active"):
        state["resource_type"] = "datastore"
        print(f"\n   → Type: DataStore (SQL queries available)")
    elif selected.get("format", "").lower() == "csv":
        state["resource_type"] = "csv"
        print(f"\n   → Type: CSV (download required)")
    else:
        state["resource_type"] = "unknown"
        print(f"\n   → Type: Unknown format")

    return state


async def analyze_datastore_node(
    state: ExplorationState, mcp_client: CKANMCPClient
) -> ExplorationState:
    """Analyze DataStore resource."""
    print("\n[ANALYZE DATASTORE]")

    if state.get("error"):
        return state

    try:
        resource_id = state["selected_resource"]["id"]
        result = await mcp_client.datastore_search(resource_id, limit=3)

        if "error" in result:
            state["error"] = result["error"]
            print(f"   ✗ Error: {result['error']}")
            return state

        if "records" in result:
            records = result["records"]
            fields = result.get("fields", [])

            state["analysis_result"] = {
                "type": "datastore",
                "record_count": len(records),
                "fields": [f["id"] for f in fields if isinstance(f, dict)],
                "sample_records": records,
            }

            print(f"   ✓ Fields: {', '.join(state['analysis_result']['fields'][:5])}")
            print(f"   ✓ Sample: {len(records)} records")
        else:
            state["error"] = "DataStore query failed"

    except Exception as e:
        state["error"] = str(e)
        print(f"   ✗ Error: {e}")

    return state


async def analyze_csv_node(state: ExplorationState) -> ExplorationState:
    """Analyze CSV resource (placeholder)."""
    print("\n[ANALYZE CSV]")

    if state.get("error"):
        return state

    # In real app: download and analyze with pandas/duckdb
    state["analysis_result"] = {
        "type": "csv",
        "url": state["selected_resource"].get("url"),
        "format": state["selected_resource"].get("format"),
    }

    print(f"   → URL: {state['analysis_result']['url']}")
    print("   (Download and analyze with DuckDB/pandas)")

    return state


async def skip_analysis_node(state: ExplorationState) -> ExplorationState:
    """Skip analysis for unknown formats."""
    print("\n[SKIP ANALYSIS] Unknown format, cannot analyze")
    state["analysis_result"] = {"type": "unknown", "skipped": True}
    return state


# Routing function
def route_by_resource_type(state: ExplorationState) -> str:
    """Route based on resource type."""
    if state.get("error"):
        return "end"

    resource_type = state.get("resource_type")
    if resource_type == "datastore":
        return "analyze_datastore"
    elif resource_type == "csv":
        return "analyze_csv"
    else:
        return "skip_analysis"


# Build workflow
async def build_workflow(mcp_client: CKANMCPClient) -> StateGraph:
    """Build exploration workflow with conditional branching."""
    graph = StateGraph(ExplorationState)

    # Add nodes with async wrappers
    async def search_wrapper(state: ExplorationState) -> ExplorationState:
        return await search_node(state, mcp_client)

    async def analyze_wrapper(state: ExplorationState) -> ExplorationState:
        return await analyze_datastore_node(state, mcp_client)

    graph.add_node("search", search_wrapper)
    graph.add_node("select_dataset", select_dataset_node)
    graph.add_node("select_resource", select_resource_node)
    graph.add_node("analyze_datastore", analyze_wrapper)
    graph.add_node("analyze_csv", analyze_csv_node)
    graph.add_node("skip_analysis", skip_analysis_node)

    # Define edges
    graph.add_edge(START, "search")
    graph.add_edge("search", "select_dataset")
    graph.add_edge("select_dataset", "select_resource")

    # Conditional routing based on resource type
    graph.add_conditional_edges(
        "select_resource",
        route_by_resource_type,
        {
            "analyze_datastore": "analyze_datastore",
            "analyze_csv": "analyze_csv",
            "skip_analysis": "skip_analysis",
            "end": END,
        },
    )

    # All analysis paths lead to END
    graph.add_edge("analyze_datastore", END)
    graph.add_edge("analyze_csv", END)
    graph.add_edge("skip_analysis", END)

    return graph.compile()


async def main():
    """Run exploration workflow."""
    print("=" * 60)
    print("LangGraph + CKAN MCP - Data Exploration Workflow")
    print("=" * 60)

    server_params = StdioServerParameters(command="node", args=[MCP_SERVER_PATH])

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("\n✓ Connected to CKAN MCP Server")

            mcp_client = CKANMCPClient(session)
            workflow = await build_workflow(mcp_client)

            # Execute workflow
            initial_state: ExplorationState = {
                "messages": [],
                "query": "trasporti",  # Query that returns manageable datasets
                "datasets": [],
                "selected_dataset": None,
                "selected_resource": None,
                "resource_type": None,
                "analysis_result": None,
                "error": None,
            }

            result = await workflow.ainvoke(initial_state)

            # Display results
            print("\n" + "=" * 60)
            print("WORKFLOW RESULT")
            print("=" * 60)

            if result.get("error"):
                print(f"\n✗ Error: {result['error']}")
            elif result.get("analysis_result"):
                analysis = result["analysis_result"]
                print(f"\nAnalysis Type: {analysis['type']}")

                if analysis["type"] == "datastore":
                    print(f"Fields: {', '.join(analysis['fields'][:5])}")
                    print(f"Records sampled: {analysis['record_count']}")
                elif analysis["type"] == "csv":
                    print(f"URL: {analysis['url']}")
                else:
                    print("Skipped (unknown format)")

            print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
