# Quick Test Guide

## 🚀 Quick Start

### Run the Workflow with Test Documents
```bash
wsl bash -c "cd /mnt/c/Users/xgranbolo/AICode/Workflow_demo && /home/xgranbolo/.local/bin/adk run agent_workflow_telemetry"
```

### Test Questions to Ask

**Question 1: Lessons Learned**
```
What are the key lessons learned from these projects?
```

**Question 2: Challenges**
```
What were the main challenges encountered and how were they resolved?
```

**Question 3: Recommendations**
```
What recommendations are provided for future similar projects?
```

**Question 4: Performance**
```
Compare the performance improvements achieved in both projects.
```

**Question 5: Costs**
```
What were the main cost factors and optimization strategies?
```

## 📁 Test Files Created

- ✅ `input_files/cloud_migration_lessons.md` (5.9 KB)
- ✅ `input_files/data_pipeline_project.md` (4.2 KB)
- ✅ `input_files/sample_doc.md` (916 bytes)
- ✅ `tests/test_workflow.py` (unit tests)
- ✅ `tests/test_e2e.py` (end-to-end test)
- ✅ `TESTING.md` (comprehensive guide)
- ✅ `TEST_SUMMARY.md` (full summary)

## ✅ E2E Test Status

```
✅ END-TO-END TEST PASSED (2026-02-10 13:29:44)

All workflow components validated:
  ✓ Configuration loaded
  ✓ Test documents available (3 documents)
  ✓ Workflow structure validated
  ✓ All agents initialized
```

## 🔗 Check Traces

**Databricks:**
https://adb-957977613266276.16.azuredatabricks.net/ml/experiments/3078644569850998/traces

**Local Logs:**
`./test_logs/` or `./logs/` directory

## 📚 Documentation

- **TESTING.md** - Detailed testing guide
- **TEST_SUMMARY.md** - Complete test summary
- **README.md** - Project overview

## 🎯 Expected Results

The workflow should:
1. Load and analyze 3 test documents
2. Extract lessons learned and challenges
3. Identify technical decisions and metrics
4. Synthesize recommendations
5. Generate comprehensive summary with references

Happy Testing! 🎉
