# Parallel Task Version Execution

## Variables
PLAN_TO_EXECUTE: $ARGUMENTS
NUMBER_OF_PARALLEL_WORKTREES: $ARGUMENTS

## Run these commands top to bottom
RUN `eza . --tree`
READ: PLAN_TO_EXECUTE

## Instructions

We're going to create NUMBER_OF_PARALLEL_WORKTREES new subagents that use the Task tool to create N versions of the same feature in parallel.

This enables use to concurrently build the same feature in parallel so we can test and validate each subagent's changes in isolation then pick the best changes.

The first agent will run in trees/<predefined_feature_name>-1/
The second agent will run in trees/<predefined_feature_name>-2/
...
The last agent will run in trees/<predefined_feature_name>-<NUMBER_OF_PARALLEL_WORKTREES>/

The code in trees/<predefined_feature_name>-<i>/ will be identical to the code in the current branch. It will be setup and ready for you to build the feature end to end.

Each agent will independently implement the engineering plan detailed in PLAN_TO_EXECUTE in their respective workspace.

When the subagent completes it's work, have the subagent to report their final changes made in a comprehensive `RESULTS.md` file at the root of their respective workspace.

Each subagent should validate their changes with proper tests: `uv run pytest tests/` in their respective workspaces.

## Alpaca MCP Gold Standard Validation Requirements

Each subagent must perform comprehensive validation:

### Testing Coverage
- Run full test suite: `uv run pytest tests/ -v --cov=src --cov-report=term-missing`
- Validate resource-mirror consistency: `uv run pytest tests/test_resource_mirrors.py -v`
- Test state management: `uv run pytest tests/test_state_management.py -v`
- Integration tests: `uv run pytest tests/test_integration.py -v`

### Performance Validation
- Measure tool response times for all 50+ tools
- Check memory usage: `uv run python -c "from src.mcp_server.models.schemas import StateManager; print(StateManager.get_memory_usage())"`
- Validate subprocess execution timeout (30 seconds)
- Test adaptive discovery patterns

### Architecture Compliance Checklist
- [ ] All 50+ tools maintain consistent error handling format
- [ ] Adaptive discovery patterns (entity role classification)
- [ ] Resource mirror pattern (11 mirror tools)
- [ ] Context-aware prompts (4 prompts reference actual data)
- [ ] Safe code execution (4 subprocess isolation tools)
- [ ] Universal dataset agnosticism patterns
- [ ] State management with memory tracking

### RESULTS.md Template

Each subagent should create a RESULTS.md with this structure:

```markdown
# Implementation Results - Subagent <NUMBER>

## Overview
[Brief description of implementation approach and key decisions]

## Test Results
- Total tests passed: X/Y
- Code coverage: X%
- Resource-mirror consistency: ✅/❌
- State management tests: ✅/❌
- Integration tests: ✅/❌

## Performance Metrics
- Average tool response time: Xms
- Memory usage (idle): XMB
- Memory usage (with portfolio loaded): XMB
- Subprocess execution time: Xs
- Adaptive discovery accuracy: X%

## Architecture Compliance
- ✅ Adaptive discovery patterns
- ✅ Resource mirror pattern (11 mirrors)
- ✅ Context-aware prompts (4 prompts)
- ✅ Safe code execution (4 subprocess tools)
- ✅ Universal dataset agnosticism
- ✅ Consistent error handling

## Key Innovations
[List any improvements or novel approaches discovered]

## Implementation Highlights
[Code snippets or design patterns worth sharing]

## Known Issues
[List any problems or limitations encountered]

## Recommendation
[Should this implementation be considered for merge? Why?]
```