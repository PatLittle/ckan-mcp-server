#!/usr/bin/env python3
"""
Quick test to verify LangGraph + MCP setup

Run:
    uvx --with langgraph --with mcp --with langchain-core python test_setup.py
"""

import sys


def test_imports():
    """Test that all required packages are available."""
    print("Testing imports...")
    errors = []

    try:
        import langgraph  # noqa: F401

        print("✓ langgraph")
    except ImportError as e:
        errors.append(f"✗ langgraph: {e}")

    try:
        import mcp  # noqa: F401

        print("✓ mcp")
    except ImportError as e:
        errors.append(f"✗ mcp: {e}")

    try:
        import langchain_core  # noqa: F401

        print("✓ langchain_core")
    except ImportError as e:
        errors.append(f"✗ langchain_core: {e}")

    return errors


def test_mcp_server():
    """Test that MCP server file exists."""
    import os

    print("\nTesting MCP server...")
    server_path = os.path.join(os.path.dirname(__file__), "../../dist/index.js")

    if os.path.exists(server_path):
        print(f"✓ MCP server found: {server_path}")
        return []
    else:
        return [
            f"✗ MCP server not found: {server_path}",
            "  Run: cd ../.. && npm run build",
        ]


def test_node():
    """Test that Node.js is available."""
    import subprocess

    print("\nTesting Node.js...")
    try:
        result = subprocess.run(
            ["node", "--version"], capture_output=True, text=True, check=True
        )
        version = result.stdout.strip()
        print(f"✓ Node.js {version}")
        return []
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ["✗ Node.js not found or not in PATH"]


def main():
    """Run all tests."""
    print("=" * 60)
    print("LangGraph + CKAN MCP Setup Test")
    print("=" * 60)

    all_errors = []

    # Run tests
    all_errors.extend(test_imports())
    all_errors.extend(test_node())
    all_errors.extend(test_mcp_server())

    # Summary
    print("\n" + "=" * 60)
    if all_errors:
        print("SETUP INCOMPLETE")
        print("=" * 60)
        for error in all_errors:
            print(error)
        print("\nSee README.md for setup instructions")
        sys.exit(1)
    else:
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        print("\nYou can now run:")
        print("  python 01_basic_workflow.py")
        print("  python 02_data_exploration.py")
        sys.exit(0)


if __name__ == "__main__":
    main()
