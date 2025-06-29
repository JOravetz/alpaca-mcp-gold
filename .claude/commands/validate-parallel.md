# Validate Parallel Implementations for Alpaca MCP Gold Standard

## Variables
FEATURE_NAME: $ARGUMENTS
NUMBER_OF_PARALLEL_WORKTREES: $ARGUMENTS

## Validation Process

### Step 1: Collect Results
For each worktree, read and analyze:
- `trees/FEATURE_NAME-i/RESULTS.md`
- Test coverage reports
- Performance metrics
- Architecture compliance scores

### Step 2: Comparative Analysis

Create a comparison matrix across all implementations:

| Metric | Agent 1 | Agent 2 | Agent 3 | ... |
|--------|---------|---------|---------|-----|
| Test Coverage | X% | X% | X% | |
| Tests Passed | X/Y | X/Y | X/Y | |
| Avg Response Time | Xms | Xms | Xms | |
| Memory Usage | XMB | XMB | XMB | |
| Architecture Score | X/7 | X/7 | X/7 | |

### Step 3: Architecture Compliance Validation

For each implementation, verify:

#### Core Patterns (Must Have)
- [ ] **Adaptive Discovery**: Entity classification working correctly
- [ ] **Resource Mirror Pattern**: All 11 mirrors functioning
- [ ] **Context-Aware Prompts**: 4 prompts reference actual data
- [ ] **Safe Code Execution**: 4 subprocess tools with timeout
- [ ] **Consistent Error Handling**: All tools return standard format
- [ ] **State Management**: Memory tracking and cleanup working
- [ ] **Universal Analytics**: Dataset agnosticism patterns intact

#### Tool Categories (Must Maintain)
- [ ] Account Tools (4): get_account_info, get_positions, get_open_position, get_portfolio_summary
- [ ] Market Data Tools (4): get_stock_quote, get_stock_trade, get_stock_snapshot, get_historical_bars
- [ ] Order Management (5): place_market_order, place_limit_order, place_stop_loss_order, get_orders, cancel_order
- [ ] Custom Execution (3): execute_custom_trading_strategy, portfolio_optimization, risk_analysis
- [ ] Advanced Analysis (2): portfolio_health_assessment, market_correlation_analysis
- [ ] Universal Analytics (2): execute_custom_analytics_code, create_sample_dataset
- [ ] Resource Mirrors (11): All resource_*_tool functions

### Step 4: Performance Benchmarks

Compare against baseline metrics:
- Tool response time: < 100ms (average)
- Memory usage (idle): < 50MB
- Memory usage (loaded): < 200MB
- Subprocess execution: < 30s timeout
- Test coverage: > 80%

### Step 5: Innovation Assessment

Evaluate each implementation for:
1. **Code Quality Improvements**
   - Better error messages
   - Cleaner code organization
   - Enhanced documentation

2. **Performance Optimizations**
   - Faster response times
   - Lower memory usage
   - Better caching strategies

3. **Feature Enhancements**
   - New adaptive insights
   - Better prompt engineering
   - Enhanced analytics capabilities

4. **Testing Improvements**
   - Higher coverage
   - Better test organization
   - New edge case handling

### Step 6: Selection Criteria

Score each implementation (0-100):
- Functionality (40 points)
  - All tests passing: 20
  - Architecture compliance: 20
- Performance (30 points)
  - Response time: 15
  - Memory efficiency: 15
- Code Quality (20 points)
  - Maintainability: 10
  - Documentation: 10
- Innovation (10 points)
  - Novel improvements: 10

### Step 7: Final Recommendation

Create VALIDATION_REPORT.md with:

```markdown
# Parallel Implementation Validation Report

## Feature: FEATURE_NAME
## Date: [Current Date]
## Implementations Evaluated: NUMBER_OF_PARALLEL_WORKTREES

## Executive Summary
[Which implementation is recommended and why]

## Detailed Scores
| Implementation | Functionality | Performance | Quality | Innovation | Total |
|----------------|---------------|-------------|---------|------------|-------|
| Agent 1 | X/40 | X/30 | X/20 | X/10 | X/100 |
| Agent 2 | X/40 | X/30 | X/20 | X/10 | X/100 |

## Key Findings
1. [Most significant discovery]
2. [Performance insights]
3. [Architecture improvements]

## Implementation Differences
[Highlight key differences between approaches]

## Risks and Considerations
[Any concerns or issues to address]

## Merge Strategy
1. Primary implementation: Agent X
2. Cherry-pick from Agent Y: [specific improvements]
3. Testing requirements before merge
4. Documentation updates needed

## Lessons Learned
[Insights for future parallel development]
```

### Step 8: Merge Preparation

For the selected implementation:
1. Run full test suite one more time
2. Update documentation if needed
3. Create clean commit history
4. Prepare PR description with validation results
5. Tag other implementations for future reference