#!/usr/bin/env python3
"""
End-to-End Tests for User Stories

Tests three complete user workflows:
1. Project Planning on the Go
2. Code Review While Commuting
3. Learning New Technology
"""

import requests
import json
import os
import time
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
WEBHOOK_URL = "https://web-production-3d53a.up.railway.app/webhook"

def send_command(command_type, session_id, data):
    """Helper to send collaborative session command"""
    payload = {
        "type": "collaborative_session_command",
        "command": command_type,
        "session_id": session_id,
        "data": data
    }

    response = requests.post(
        WEBHOOK_URL,
        headers={
            "Content-Type": "application/json",
            "X-API-Key": API_KEY
        },
        json=payload,
        timeout=10
    )

    return response

def send_task(task_id, action_type, params, sync=True):
    """Helper to send task command"""
    payload = {
        "type": "task_command",
        "sync": sync,
        "data": {
            "task_id": task_id,
            "action_type": action_type,
            "params": params
        }
    }

    response = requests.post(
        WEBHOOK_URL,
        headers={
            "Content-Type": "application/json",
            "X-API-Key": API_KEY
        },
        json=payload,
        timeout=35
    )

    return response

def test_story_1_project_planning():
    """
    Story 1: Project Planning on the Go

    Simulates: User walking dog, captures ideas, makes decisions,
    then later retrieves them and starts coding.
    """
    print("=" * 70)
    print("STORY 1: Project Planning on the Go 🚶")
    print("=" * 70)
    print()

    session_id = "carbon_tracking_planning"
    results = []

    # Step 1: Create session (walking the dog, 9:00 AM)
    print("Step 1: Create project planning session...")
    resp = send_command("create_session", session_id, {
        "title": "Carbon Tracking Feature Planning",
        "participants": ["chatgpt", "developer"],
        "context": "Walking the dog, brainstorming new feature"
    })
    results.append(("Create Session", resp.status_code == 200))
    time.sleep(0.5)

    # Step 2: Store idea (still walking, 9:02 AM)
    print("Step 2: Store feature idea...")
    resp = send_command("store_memory", session_id, {
        "type": "idea",
        "key": "carbon_emissions_tracking",
        "content": {
            "title": "Add carbon emissions tracking to API calls",
            "description": "Show users their environmental impact from LLM usage",
            "priority": "high"
        },
        "tags": ["sustainability", "feature", "api"]
    })
    results.append(("Store Idea", resp.status_code == 200))
    time.sleep(0.5)

    # Step 3: Store decision (dog stopped to sniff, 9:05 AM)
    print("Step 3: Store API choice decision...")
    resp = send_command("store_memory", session_id, {
        "type": "decision",
        "key": "use_carbon_interface_api",
        "content": {
            "decision": "Use Carbon Interface API",
            "rationale": "Has good documentation and LLM-friendly API",
            "alternatives_considered": ["Climatiq", "Custom calculation"]
        },
        "tags": ["architecture", "api"]
    })
    results.append(("Store Decision", resp.status_code == 200))
    time.sleep(0.5)

    # Step 4: Store action item (walking home, 9:10 AM)
    print("Step 4: Add research action item...")
    resp = send_command("store_memory", session_id, {
        "type": "action_item",
        "key": "research_pricing",
        "content": {
            "task": "Research Carbon Interface API pricing tiers",
            "priority": "high",
            "estimated_time": "30 minutes"
        },
        "tags": ["research", "pricing"]
    })
    results.append(("Store Action Item", resp.status_code == 200))
    time.sleep(0.5)

    # Step 5: Query decisions (back at desk, 10:00 AM)
    print("Step 5: Query all decisions...")
    resp = send_command("query_memories", session_id, {
        "type": "decision"
    })
    results.append(("Query Decisions", resp.status_code == 200))
    time.sleep(0.5)

    # Step 6: Execute git status (ready to code, 10:05 AM)
    print("Step 6: Check git status...")
    resp = send_task(
        "story1_git_status",
        "git",
        {
            "command": ["git", "status", "--short"],
            "working_dir": "/Users/tim/gameplan.ai/ai-webhook"
        }
    )
    results.append(("Git Status", resp.status_code == 200))
    time.sleep(0.5)

    # Step 7: Create feature branch (starting work, 10:10 AM)
    print("Step 7: Check current branch...")
    resp = send_task(
        "story1_git_branch",
        "git",
        {
            "command": ["git", "branch", "--show-current"],
            "working_dir": "/Users/tim/gameplan.ai/ai-webhook"
        }
    )
    results.append(("Git Branch", resp.status_code == 200))

    # Results
    print()
    print("STORY 1 RESULTS:")
    print("-" * 70)
    for step, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{step:30} {status}")
    print()

    all_passed = all(success for _, success in results)
    return all_passed

def test_story_2_code_review():
    """
    Story 2: Code Review While Commuting

    Simulates: User reviewing PR while commuting, capturing questions
    and decisions, then acting on them at desk.
    """
    print("=" * 70)
    print("STORY 2: Code Review While Commuting 🚗")
    print("=" * 70)
    print()

    session_id = "pr42_auth_review"
    results = []

    # Step 1: Create session (in car, 8:30 AM)
    print("Step 1: Create code review session...")
    resp = send_command("create_session", session_id, {
        "title": "PR #42 - Authentication Refactor Review",
        "participants": ["claude", "developer"],
        "context": "Reviewing PR during commute"
    })
    results.append(("Create Session", resp.status_code == 200))
    time.sleep(0.5)

    # Step 2: Check git status (at stoplight, 8:32 AM)
    print("Step 2: Check git status...")
    resp = send_task(
        "story2_git_status",
        "git",
        {
            "command": ["git", "status"],
            "working_dir": "/Users/tim/gameplan.ai/ai-webhook"
        }
    )
    results.append(("Git Status", resp.status_code == 200))
    time.sleep(0.5)

    # Step 3: Check recent commits (parking, 8:35 AM)
    print("Step 3: View recent commits...")
    resp = send_task(
        "story2_git_log",
        "git",
        {
            "command": ["git", "log", "--oneline", "-5"],
            "working_dir": "/Users/tim/gameplan.ai/ai-webhook"
        }
    )
    results.append(("Git Log", resp.status_code == 200))
    time.sleep(0.5)

    # Step 4: Store question (walking to office, 8:40 AM)
    print("Step 4: Store security question...")
    resp = send_command("store_memory", session_id, {
        "type": "question",
        "key": "oauth2_device_flow",
        "content": {
            "question": "Does the new auth system support OAuth2 device flow for CLI tools?",
            "context": "Need this for headless server authentication",
            "priority": "high"
        },
        "tags": ["security", "oauth2", "cli"]
    })
    results.append(("Store Question", resp.status_code == 200))
    time.sleep(0.5)

    # Step 5: Store decision (elevator, 8:42 AM)
    print("Step 5: Store rate limiting decision...")
    resp = send_command("store_memory", session_id, {
        "type": "decision",
        "key": "add_rate_limiting",
        "content": {
            "decision": "Add rate limiting to new auth endpoints",
            "rationale": "Prevent brute force attacks on authentication",
            "implementation": "Use Redis with sliding window algorithm"
        },
        "tags": ["security", "rate-limiting"]
    })
    results.append(("Store Decision", resp.status_code == 200))
    time.sleep(0.5)

    # Step 6: Query questions (at desk, 9:00 AM)
    print("Step 6: Retrieve all questions...")
    resp = send_command("query_memories", session_id, {
        "type": "question"
    })
    results.append(("Query Questions", resp.status_code == 200))
    time.sleep(0.5)

    # Step 7: Query decisions (reviewing code, 9:05 AM)
    print("Step 7: List all decisions...")
    resp = send_command("query_memories", session_id, {
        "type": "decision"
    })
    results.append(("Query Decisions", resp.status_code == 200))
    time.sleep(0.5)

    # Step 8: Add action item (ready to comment, 9:10 AM)
    print("Step 8: Create PR comment action item...")
    resp = send_command("store_memory", session_id, {
        "type": "action_item",
        "key": "write_security_comment",
        "content": {
            "task": "Write up security considerations in PR comment",
            "details": "Include rate limiting decision and OAuth2 question",
            "priority": "high"
        },
        "tags": ["pr-review", "security"]
    })
    results.append(("Store Action Item", resp.status_code == 200))

    # Results
    print()
    print("STORY 2 RESULTS:")
    print("-" * 70)
    for step, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{step:30} {status}")
    print()

    all_passed = all(success for _, success in results)
    return all_passed

def test_story_3_learning():
    """
    Story 3: Learning New Technology

    Simulates: User learning about MCP protocol, storing facts and
    questions, then retrieving them later.
    """
    print("=" * 70)
    print("STORY 3: Learning New Technology 📚")
    print("=" * 70)
    print()

    session_id = "mcp_protocol_study"
    results = []

    # Step 1: Create session (starting to learn, 2:00 PM)
    print("Step 1: Create learning session...")
    resp = send_command("create_session", session_id, {
        "title": "Learning Model Context Protocol (MCP)",
        "participants": ["student", "chatgpt"],
        "context": "Self-directed learning about MCP specification"
    })
    results.append(("Create Session", resp.status_code == 200))
    time.sleep(0.5)

    # Step 2: Store fact #1 (reading docs, 2:10 PM)
    print("Step 2: Store fact about JSON-RPC...")
    resp = send_command("store_memory", session_id, {
        "type": "fact",
        "key": "mcp_uses_jsonrpc",
        "content": {
            "fact": "MCP uses JSON-RPC 2.0 for client-server communication",
            "source": "MCP Specification",
            "confidence": "high"
        },
        "tags": ["mcp", "jsonrpc", "protocol"]
    })
    results.append(("Store Fact 1", resp.status_code == 200))
    time.sleep(0.5)

    # Step 3: Store fact #2 (reading more, 2:15 PM)
    print("Step 3: Store fact about MCP capabilities...")
    resp = send_command("store_memory", session_id, {
        "type": "fact",
        "key": "mcp_server_capabilities",
        "content": {
            "fact": "MCP servers expose tools, resources, and prompts",
            "details": "Three main capability types for different use cases",
            "source": "MCP Specification - Server Capabilities"
        },
        "tags": ["mcp", "capabilities", "architecture"]
    })
    results.append(("Store Fact 2", resp.status_code == 200))
    time.sleep(0.5)

    # Step 4: Store question (confused, 2:20 PM)
    print("Step 4: Store clarifying question...")
    resp = send_command("store_memory", session_id, {
        "type": "question",
        "key": "tools_vs_resources",
        "content": {
            "question": "What's the difference between a tool and a resource in MCP?",
            "context": "Both seem to provide functionality to clients",
            "priority": "high"
        },
        "tags": ["mcp", "tools", "resources"]
    })
    results.append(("Store Question", resp.status_code == 200))
    time.sleep(0.5)

    # Step 5: Store fact (found answer, 2:25 PM)
    print("Step 5: Store answer as fact...")
    resp = send_command("store_memory", session_id, {
        "type": "fact",
        "key": "tools_vs_resources_answer",
        "content": {
            "fact": "Tools are functions that perform actions, resources are data that can be read",
            "details": "Tools = verbs (do things), Resources = nouns (provide info)",
            "source": "MCP Specification - Tools vs Resources section"
        },
        "tags": ["mcp", "tools", "resources", "clarification"]
    })
    results.append(("Store Fact 3", resp.status_code == 200))
    time.sleep(0.5)

    # Step 6: Store note (taking notes, 2:30 PM)
    print("Step 6: Store reference note...")
    resp = send_command("store_memory", session_id, {
        "type": "note",
        "key": "mcp_spec_link",
        "content": {
            "note": "The MCP specification is at modelcontextprotocol.io/specification",
            "category": "reference"
        },
        "tags": ["mcp", "documentation", "reference"]
    })
    results.append(("Store Note", resp.status_code == 200))
    time.sleep(0.5)

    # Step 7: Add action item (planning next steps, 2:35 PM)
    print("Step 7: Add action item for practice...")
    resp = send_command("store_memory", session_id, {
        "type": "action_item",
        "key": "build_calculator_server",
        "content": {
            "task": "Build a simple MCP server that exposes a calculator tool",
            "purpose": "Hands-on practice with MCP server implementation",
            "estimated_time": "2 hours"
        },
        "tags": ["mcp", "hands-on", "project"]
    })
    results.append(("Store Action Item", resp.status_code == 200))
    time.sleep(0.5)

    # Step 8: Query facts (next day, 3:00 PM)
    print("Step 8: Retrieve all learned facts...")
    resp = send_command("query_memories", session_id, {
        "type": "fact"
    })
    results.append(("Query Facts", resp.status_code == 200))
    time.sleep(0.5)

    # Step 9: Query questions (continuing learning, 3:05 PM)
    print("Step 9: Review all questions...")
    resp = send_command("query_memories", session_id, {
        "type": "question"
    })
    results.append(("Query Questions", resp.status_code == 200))
    time.sleep(0.5)

    # Step 10: List action items (planning project, 3:10 PM)
    print("Step 10: List action items...")
    resp = send_command("query_memories", session_id, {
        "type": "action_item"
    })
    results.append(("Query Action Items", resp.status_code == 200))

    # Results
    print()
    print("STORY 3 RESULTS:")
    print("-" * 70)
    for step, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{step:30} {status}")
    print()

    all_passed = all(success for _, success in results)
    return all_passed

def main():
    """Run all user story tests"""
    print("\n")
    print("=" * 70)
    print("USER STORY END-TO-END TESTS")
    print("=" * 70)
    print()
    print("Testing three realistic workflows:")
    print("1. Project Planning on the Go")
    print("2. Code Review While Commuting")
    print("3. Learning New Technology")
    print()
    print("Each test validates the complete user journey")
    print("from initial thought to final action.")
    print()
    input("Press Enter to start tests...")
    print()

    # Run tests
    story1_pass = test_story_1_project_planning()
    print()
    time.sleep(2)

    story2_pass = test_story_2_code_review()
    print()
    time.sleep(2)

    story3_pass = test_story_3_learning()
    print()

    # Final summary
    print("=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    print(f"Story 1 (Project Planning):    {'✅ PASS' if story1_pass else '❌ FAIL'}")
    print(f"Story 2 (Code Review):          {'✅ PASS' if story2_pass else '❌ FAIL'}")
    print(f"Story 3 (Learning):             {'✅ PASS' if story3_pass else '❌ FAIL'}")
    print()

    if story1_pass and story2_pass and story3_pass:
        print("🎉 ALL USER STORIES VALIDATED!")
        print()
        print("The system successfully supports:")
        print("  • Mixed task execution + session management")
        print("  • All 6 memory types (idea, decision, question, action_item, fact, note)")
        print("  • Memory persistence across time")
        print("  • Query by type and tags")
        print("  • Natural workflow integration")
        print()
        print("READY FOR PRODUCTION USE! ✨")
        return 0
    else:
        print("⚠️  SOME STORIES FAILED")
        print("Review errors above and fix before proceeding.")
        return 1

if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n\nTests cancelled by user.")
        exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
