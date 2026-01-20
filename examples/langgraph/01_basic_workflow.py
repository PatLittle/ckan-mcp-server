#!/usr/bin/env python3
"""
Basic LangGraph Workflow with CKAN MCP Server

Demonstrates simple sequential workflow:
1. Search datasets by keyword
2. Filter by metadata quality using scoring system
3. Extract CSV resources
4. Display results

Run:
    uvx --with langgraph --with mcp --with langchain-core python 01_basic_workflow.py
"""

import asyncio
import json
import os
from typing import Annotated, TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from metadata_quality import MetadataQualityScorer

# Configuration
CKAN_SERVER = "https://www.dati.gov.it/opendata"
MCP_SERVER_PATH = os.path.join(os.path.dirname(__file__), "../../dist/index.js")
QUALITY_THRESHOLD = 40  # Minimum quality score (0-100)
SEARCH_ROWS = 5  # Limit rows to avoid JSON truncation in MCP responses


# State definition
class WorkflowState(TypedDict):
    """State tracked through workflow."""

    messages: Annotated[list, add_messages]
    query: str
    datasets: list[dict]
    filtered_datasets: list[dict]
    csv_resources: list[dict]
    error: str | None


# MCP Client helper
class CKANMCPClient:
    """Helper for calling CKAN MCP Server tools."""

    def __init__(self, session: ClientSession):
        self.session = session

    async def search_packages(self, query: str, rows: int = SEARCH_ROWS) -> dict:
        """Search CKAN packages."""
        result = await self.session.call_tool(
            "ckan_package_search",
            arguments={
                "server_url": CKAN_SERVER,
                "q": query,
                "rows": rows,
                "response_format": "json",
            },
        )

        # Parse JSON from text content
        for content in result.content:
            if content.type == "text":
                try:
                    text = content.text
                    # Handle truncation marker if present
                    if "[Response truncated" in text:
                        text = text.split("[Response truncated")[0].strip()
                    return json.loads(text)
                except json.JSONDecodeError as e:
                    return {"error": f"JSON parse error: {e}"}

        return {"error": "No content in response"}


# Workflow nodes
async def search_datasets_node(
    state: WorkflowState, mcp_client: CKANMCPClient
) -> WorkflowState:
    """Node 1: Search datasets."""
    print(f"\n[1/3] Searching datasets for: '{state['query']}'")

    try:
        response = await mcp_client.search_packages(state["query"])

        if "error" in response:
            state["error"] = response["error"]
            print(f"   ✗ Error: {response['error']}")
            return state

        if "results" in response:
            datasets = response["results"]
            state["datasets"] = datasets
            state["messages"].append(
                {"role": "assistant", "content": f"Found {len(datasets)} datasets"}
            )
            print(
                f"   ✓ Found {response.get('count', len(datasets))} total, showing {len(datasets)}"
            )
        else:
            state["error"] = "Unexpected response structure"
            print(f"   ✗ Error: missing 'results' key")

    except Exception as e:
        state["error"] = str(e)
        print(f"   ✗ Error: {e}")

    return state


async def filter_quality_node(state: WorkflowState) -> WorkflowState:
    """Node 2: Filter by metadata quality using scoring system."""
    print("\n[2/3] Filtering by metadata quality")

    if state.get("error"):
        return state

    scorer = MetadataQualityScorer()
    filtered = []

    for ds in state["datasets"]:
        quality = scorer.score_dataset(ds)
        ds["_quality"] = quality  # Attach quality info to dataset

        if quality["score"] >= QUALITY_THRESHOLD:
            filtered.append(ds)
            print(
                f"   ✓ {ds['title'][:50]}: {quality['score']}/100 ({quality['level']})"
            )
        else:
            print(f"   ✗ {ds['title'][:50]}: {quality['score']}/100 (rejected)")

    state["filtered_datasets"] = filtered
    state["messages"].append(
        {
            "role": "assistant",
            "content": f"Filtered to {len(filtered)} quality datasets",
        }
    )
    print(
        f"\n   → {len(filtered)}/{len(state['datasets'])} datasets pass quality threshold ({QUALITY_THRESHOLD})"
    )

    return state

    # Filter: must have title, notes, and at least one resource
    filtered = [
        ds
        for ds in state["datasets"]
        if ds.get("title") and ds.get("notes") and ds.get("num_resources", 0) > 0
    ]

    state["filtered_datasets"] = filtered
    state["messages"].append(
        {
            "role": "assistant",
            "content": f"Filtered to {len(filtered)} quality datasets",
        }
    )
    print(f"   ✓ {len(filtered)} datasets with good metadata")

    return state


async def extract_csv_node(state: WorkflowState) -> WorkflowState:
    """Node 3: Extract CSV resources."""
    print("\n[3/3] Extracting CSV resources")

    if state.get("error"):
        return state

    csv_resources = []
    for dataset in state["filtered_datasets"][:5]:  # Limit to first 5
        for resource in dataset.get("resources", []):
            if resource.get("format", "").lower() == "csv":
                csv_resources.append(
                    {
                        "dataset_name": dataset["name"],
                        "dataset_title": dataset["title"],
                        "resource_name": resource.get("name", "Untitled"),
                        "url": resource.get("url"),
                    }
                )

    state["csv_resources"] = csv_resources
    state["messages"].append(
        {
            "role": "assistant",
            "content": f"Extracted {len(csv_resources)} CSV resources",
        }
    )
    print(f"   ✓ Found {len(csv_resources)} CSV resources")

    return state


# Build graph
async def build_workflow(mcp_client: CKANMCPClient) -> StateGraph:
    """Build LangGraph workflow."""
    graph = StateGraph(WorkflowState)

    # Add nodes - wrap async functions properly
    async def search_wrapper(state: WorkflowState) -> WorkflowState:
        return await search_datasets_node(state, mcp_client)

    graph.add_node("search", search_wrapper)
    graph.add_node("filter", filter_quality_node)
    graph.add_node("extract", extract_csv_node)

    # Define edges
    graph.add_edge(START, "search")
    graph.add_edge("search", "filter")
    graph.add_edge("filter", "extract")
    graph.add_edge("extract", END)

    return graph.compile()


async def main():
    """Run workflow."""
    print("=" * 60)
    print("LangGraph + CKAN MCP Server - Basic Workflow")
    print("=" * 60)

    # Connect to MCP server
    server_params = StdioServerParameters(command="node", args=[MCP_SERVER_PATH])

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("\n✓ Connected to CKAN MCP Server")

            # Build workflow
            mcp_client = CKANMCPClient(session)
            workflow = await build_workflow(mcp_client)

            # Execute workflow
            initial_state: WorkflowState = {
                "messages": [],
                "query": "mobilità urbana",
                "datasets": [],
                "filtered_datasets": [],
                "csv_resources": [],
                "error": None,
            }

            result = await workflow.ainvoke(initial_state)

            # Display results
            print("\n" + "=" * 60)
            print("RESULTS")
            print("=" * 60)

            if result["error"]:
                print(f"\n✗ Workflow failed: {result['error']}")
            else:
                print(f"\nQuery: {result['query']}")
                print(f"Total datasets found: {len(result['datasets'])}")
                print(f"Quality datasets: {len(result['filtered_datasets'])}")
                print(f"CSV resources: {len(result['csv_resources'])}")

                if result["csv_resources"]:
                    print("\nFirst 3 CSV resources:")
                    for i, res in enumerate(result["csv_resources"][:3], 1):
                        print(f"\n{i}. {res['resource_name']}")
                        print(f"   Dataset: {res['dataset_title']}")
                        print(f"   URL: {res['url']}")

            print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
