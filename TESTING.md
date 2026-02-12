# Agent Workflow Testing Guide

## Overview
This document provides comprehensive information about testing the agent workflow telemetry system.

## Test Documents Created

### 1. Cloud Migration Lessons (`cloud_migration_lessons.md`)
**Purpose**: Test workflow's ability to extract lessons learned from a complex technical project.

**Content Includes**:
- Executive summary
- Technical architecture details
- Key lessons learned (successes and challenges)
- Risk mitigation strategies
- Success metrics and KPIs
- Recommendations for future projects
- Team structure and timeline
- Budget breakdown

**Test Scenarios**:
- Extracting key challenges from project documentation
- Identifying success factors
- Summarizing technical decisions
- Generating recommendations

### 2. Data Pipeline Project (`data_pipeline_project.md`)
**Purpose**: Test workflow's ability to process technical specifications and architectural decisions.

**Content Includes**:
- Technical architecture components
- Key technical decisions with rationale
- Performance improvements with metrics
- Challenges with resolutions
- Best practices established
- Team insights and recommendations

**Test Scenarios**:
- Understanding technical trade-offs
- Extracting performance metrics
- Identifying best practices
- Summarizing architectural patterns

## Test Suite Structure

### Unit Tests (`tests/test_workflow.py`)

#### TestBootstrapAgent
Tests the initialization and configuration of the bootstrap agent.

**Key Tests**:
- `test_bootstrap_agent_initialization`: Verifies agent creation
- `test_bootstrap_agent_with_custom_dir`: Tests custom directory handling

#### TestDocumentReaderAgent
Tests document reading functionality across multiple formats.

**Key Tests**:
- `test_reader_agent_initialization`: Verifies reader setup
- `test_reader_finds_markdown_files`: Tests markdown file discovery
- `test_reader_finds_text_files`: Tests text file discovery

#### TestConfiguration
Tests configuration loading and environment variable handling.

**Key Tests**:
- `test_load_config`: Verifies configuration loads correctly
- `test_config_defaults`: Tests default values
- `test_config_respects_env_vars`: Tests environment variable override

#### TestWorkflowIntegration
Integration tests for the complete workflow.

**Key Tests**:
- `test_workflow_builds_successfully`: Verifies workflow construction
- `test_workflow_has_correct_agents`: Validates agent count and structure
- `test_workflow_session_state_structure`: Tests expected state format

#### TestDocumentFormats
Tests handling of various document formats.

**Key Tests**:
- `test_reader_handles_multiple_formats`: Tests MD, TXT, JSON, YAML support

#### TestErrorHandling
Tests error scenarios and edge cases.

**Key Tests**:
- `test_reader_with_nonexistent_directory`: Tests graceful handling of missing dirs
- `test_reader_with_empty_directory`: Tests empty directory handling

#### TestPerformance
Performance-related tests.

**Key Tests**:
- `test_large_document_handling`: Tests document size limits and truncation

### End-to-End Test (`tests/test_e2e.py`)

**Purpose**: Validate complete workflow execution with real documents.

**Test Phases**:
1. **Environment Setup**: Configure test environment and logging
2. **Document Validation**: Verify test documents exist
3. **Workflow Execution**: Run through all workflow phases
4. **Results Validation**: Check outputs and trace logs

**Execution Steps**:
```bash
# Run from project root
wsl bash -c "cd /mnt/c/Users/xgranbolo/AICode/Workflow_demo/agent_workflow_telemetry && python3 tests/test_e2e.py"
```

## Running Tests

### Prerequisites
```bash
# Install test dependencies
wsl bash -c "cd /mnt/c/Users/xgranbolo/AICode/Workflow_demo/agent_workflow_telemetry && python3 -m pip install pytest pytest-asyncio"
```

### Run All Unit Tests
```bash
wsl bash -c "cd /mnt/c/Users/xgranbolo/AICode/Workflow_demo/agent_workflow_telemetry && python3 -m pytest tests/test_workflow.py -v"
```

### Run Specific Test Class
```bash
wsl bash -c "cd /mnt/c/Users/xgranbolo/AICode/Workflow_demo/agent_workflow_telemetry && python3 -m pytest tests/test_workflow.py::TestDocumentReaderAgent -v"
```

### Run End-to-End Test
```bash
wsl bash -c "cd /mnt/c/Users/xgranbolo/AICode/Workflow_demo/agent_workflow_telemetry && python3 tests/test_e2e.py"
```

### Run with Coverage
```bash
# Install coverage tool
wsl bash -c "python3 -m pip install pytest-cov"

# Run with coverage
wsl bash -c "cd /mnt/c/Users/xgranbolo/AICode/Workflow_demo/agent_workflow_telemetry && python3 -m pytest tests/test_workflow.py --cov=. --cov-report=html"
```

## Test Scenarios

### Scenario 1: Basic Workflow Execution
**Question**: "What are the main challenges mentioned in the documentation?"

**Expected Output**:
- List of challenges from both documents
- Impact statements
- Resolution strategies
- Categorized by project

### Scenario 2: Lessons Learned Extraction
**Question**: "What lessons were learned from these projects?"

**Expected Output**:
- Success factors
- Challenges encountered
- Best practices established
- Recommendations for future projects

### Scenario 3: Technical Details
**Question**: "What technical decisions were made and why?"

**Expected Output**:
- Technology choices
- Rationale for decisions
- Trade-offs considered
- Performance metrics

### Scenario 4: Team and Budget Analysis
**Question**: "Summarize the team structure, timeline, and budget for these projects."

**Expected Output**:
- Team size and composition
- Project duration and phases
- Budget breakdown
- Resource allocation

### Scenario 5: Recommendations Summary
**Question**: "What are the key recommendations for future similar projects?"

**Expected Output**:
- Consolidated recommendations
- Prioritized best practices
- Common themes across projects
- Actionable insights

## Expected Test Results

### Successful Test Indicators
- ✅ All agents initialize without errors
- ✅ Documents are found and loaded
- ✅ Session state is properly structured
- ✅ Configuration values are correct
- ✅ Workflow builds successfully with 5 sub-agents

### Workflow Phase Validation

#### Phase 1: Bootstrap
- User question is loaded into session state
- Documents directory is validated
- Initial state is prepared

#### Phase 2: Clarification
- Question is analyzed for ambiguities
- Clarification prompts generated if needed
- Clarified question stored in state

#### Phase 3: Document Reading
- All markdown and text files are discovered
- File contents are read (up to max_file_chars limit)
- Documents stored in session state as JSON

#### Phase 4: Summarization
- Each document is processed individually
- Key points extracted from each document
- Summaries stored in session state

#### Phase 5: Synthesis
- Executive summary created
- Detailed answer compiled
- Document references included
- Final answer stored in session state

## Trace Validation

### Databricks Traces
Check traces at: https://adb-957977613266276.16.azuredatabricks.net/ml/experiments/3078644569850998/traces

**Expected Trace Elements**:
- Service name: `SE_workflow_test`
- Spans for each agent execution
- Timing information for each phase
- Error traces (if any issues occurred)

### Local Logs (if using LOG_DEST=local)
Check logs in: `./logs/` directory

**Expected Log Files**:
- `session_{session_id}.md` files
- Event logs for each agent action
- Timestamps and session metadata

## Troubleshooting

### Test Failures

#### Documents Not Found
**Symptom**: `No documents found in: ./input_files`
**Solution**: Ensure test documents are present in the input_files directory

#### Configuration Errors
**Symptom**: Configuration values are None or incorrect
**Solution**: Check `.env` file exists and is properly formatted

#### Import Errors
**Symptom**: `ModuleNotFoundError`
**Solution**: Ensure you're running tests from the correct directory with proper Python path

#### Agent Initialization Failures
**Symptom**: Agents fail to initialize
**Solution**: Check all required dependencies are installed

### Performance Issues

#### Slow Test Execution
- Reduce `max_file_chars` for faster testing
- Use smaller test documents
- Check system resources

#### Memory Issues
- Monitor document sizes
- Adjust max_file_chars limit
- Use document previews for large files

## Best Practices

### Test Development
1. Write tests for new features before implementation
2. Keep tests independent and isolated
3. Use fixtures for common setup
4. Mock external dependencies where appropriate
5. Test both success and failure scenarios

### Test Maintenance
1. Update tests when workflow changes
2. Review test coverage regularly
3. Remove obsolete tests
4. Keep test documentation current
5. Run tests before committing changes

### Continuous Integration
Consider setting up automated testing:
- Run tests on every commit
- Generate coverage reports
- Alert on test failures
- Track test execution time

## Test Metrics

### Coverage Goals
- **Unit Test Coverage**: >80%
- **Integration Test Coverage**: >60%
- **Critical Path Coverage**: 100%

### Performance Benchmarks
- Unit tests should complete in <5 seconds
- Integration tests should complete in <30 seconds
- End-to-end test should complete in <2 minutes

## Future Test Enhancements

1. **Automated Test Generation**: Generate test cases from document templates
2. **Performance Benchmarking**: Add automated performance regression tests
3. **Trace Validation**: Automated validation of Databricks traces
4. **Load Testing**: Test with large document sets (100+ documents)
5. **Chaos Testing**: Test failure scenarios and recovery
6. **UI Testing**: If web interface is added, include UI tests
7. **API Testing**: If API endpoints are exposed, add API tests

## Conclusion

This test suite provides comprehensive coverage of the agent workflow system, from unit tests of individual components to end-to-end validation of the complete workflow. Regular execution of these tests ensures system reliability and helps catch regressions early in development.
