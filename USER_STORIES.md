# User Stories - Collaborative Sessions

## Story 1: Project Planning on the Go 🚶

**Scenario**: You're walking your dog and think of a new feature idea. You want to capture it and make decisions before you forget.

**User Journey**:
1. **Walking the dog, 9:00 AM**: "Hey ChatGPT, create a new project planning session called 'carbon-tracking-feature'"
2. **Still walking, 9:02 AM**: "Store this idea: We should add carbon emissions tracking to all our API calls so users can see their environmental impact"
3. **Dog stops to sniff, 9:05 AM**: "I've decided we'll use the Carbon Interface API for this. Store that decision with the rationale that it has good LLM documentation"
4. **Walking home, 9:10 AM**: "Add an action item: Research Carbon Interface API pricing tiers"
5. **Back at desk, 10:00 AM**: "What decisions did we make about the carbon tracking feature?"
6. **Ready to code, 10:05 AM**: "Show me the git status of my ai-webhook project"
7. **Starting work, 10:10 AM**: "Create a new branch for this feature"

**Expected Outcomes**:
- ✅ Session created with ideas, decisions, and action items all stored
- ✅ Can query and retrieve specific memory types
- ✅ Can execute git commands alongside session management
- ✅ Memory persists across conversations (9 AM conversation, 10 AM retrieval)

**Value Proposition**: Never lose a good idea. Make decisions in the moment and have them available when you're ready to code.

---

## Story 2: Code Review While Commuting 🚗

**Scenario**: You get a PR notification while commuting. You want to review the code and leave feedback, but you're not at your computer.

**User Journey**:
1. **In car, 8:30 AM**: "Create a code review session for PR #42 - authentication refactor"
2. **Waiting at stoplight, 8:32 AM**: "Check git status on my ai-webhook repo"
3. **Parking, 8:35 AM**: "Show me the git log for the last 5 commits"
4. **Walking to office, 8:40 AM**: "Store this as a question: Does the new auth system support OAuth2 device flow for CLI tools?"
5. **Elevator, 8:42 AM**: "Store this decision: We need to add rate limiting to the new auth endpoints. Rationale: prevent brute force attacks"
6. **At desk, 9:00 AM**: "Show me all questions I had about PR #42"
7. **Reviewing code, 9:05 AM**: "List all decisions we made about the PR"
8. **Ready to comment, 9:10 AM**: "Add action item: Write up security considerations in PR comment"

**Expected Outcomes**:
- ✅ Can interleave git commands with session management
- ✅ Questions stored for later research
- ✅ Decisions captured with context
- ✅ Action items created from review insights
- ✅ Can query by memory type (all questions, all decisions)

**Value Proposition**: Review code effectively even when away from computer. Capture thoughts in the moment, act on them later.

---

## Story 3: Learning New Technology 📚

**Scenario**: You're learning about MCP (Model Context Protocol) and want to track your progress, questions, and resources.

**User Journey**:
1. **Starting to learn, 2:00 PM**: "Create a learning session called 'mcp-protocol-study'"
2. **Reading docs, 2:10 PM**: "Store this fact: MCP uses JSON-RPC 2.0 for client-server communication"
3. **Reading more, 2:15 PM**: "Store this fact: MCP servers expose tools, resources, and prompts"
4. **Confused, 2:20 PM**: "Store this question: What's the difference between a tool and a resource in MCP?"
5. **Found answer, 2:25 PM**: "Store this fact: Tools are functions that perform actions, resources are data that can be read"
6. **Taking notes, 2:30 PM**: "Store this note: The MCP specification is at modelcontextprotocol.io/specification"
7. **Planning next steps, 2:35 PM**: "Add action item: Build a simple MCP server that exposes a calculator tool"
8. **Next day, 3:00 PM**: "What facts do I know about MCP?"
9. **Continuing learning, 3:05 PM**: "Show me all questions I had"
10. **Planning project, 3:10 PM**: "List all action items for my MCP learning"

**Expected Outcomes**:
- ✅ Different memory types used appropriately (facts, questions, notes, action items)
- ✅ Memory persists across days
- ✅ Can query by type to review what you've learned
- ✅ Structured knowledge building over time

**Value Proposition**: Build a personal knowledge base. Track learning progress. Never lose important insights.

---

## Cross-Story Features

### Memory Types Used:
- **idea**: Feature proposals, improvement suggestions
- **decision**: Architectural choices with rationale
- **question**: Things to research or clarify
- **action_item**: TODOs and next steps
- **fact**: Verified knowledge
- **note**: General observations

### Commands Tested:
- `create_session` - Initialize tracking
- `store_memory` - Capture knowledge
- `query_memories` - Filter by type/tags
- `list_memories` - See all stored items
- Task execution (git commands) - Interleaved with sessions

### Integration Points:
- Session management + Task execution (git commands)
- Memory storage + Memory retrieval
- Persistence across time/conversations
- Natural language → Structured data

---

## Success Criteria

For each story to be considered "working":
1. ✅ All commands execute without errors
2. ✅ Data persists correctly to disk
3. ✅ Can retrieve stored information accurately
4. ✅ Memory queries return expected results
5. ✅ Git commands work alongside session management
6. ✅ Session metadata updates correctly (counts, timestamps)
7. ✅ Workflow feels natural and useful

---

## Next Steps

1. Build automated tests for each story
2. Create webhook payloads for each step
3. Run end-to-end validation
4. Document any gaps or missing features
5. Create LLM prompt that enables these workflows
