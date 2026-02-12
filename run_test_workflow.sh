#!/bin/bash
# Run the workflow with a test question.
# Run from project root or from SE_workflow_test (script cd's to parent for adk).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$(dirname "$SCRIPT_DIR")"
echo "What are the key lessons learned from these projects?" | timeout 120 adk run SE_workflow_test
