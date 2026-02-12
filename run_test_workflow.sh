#!/bin/bash
# Script to run the workflow with a test question
cd /mnt/c/Users/xgranbolo/AICode/Workflow_demo
export PATH=$HOME/.local/bin:$PATH
echo "What are the key lessons learned from these projects?" | timeout 120 adk run agent_workflow_telemetry
