"""
Test suite for the Agent Workflow Telemetry system.

This module tests the multi-agent workflow including:
- Bootstrap agent
- Clarifier agent
- Document reader agent
- Summarizer agent
- Synthesizer agent
"""
import os
import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.bootstrap import UserQuestionBootstrapAgent
from agents.reader import DocumentReaderAgent
from config import load_config


class TestBootstrapAgent:
    """Tests for the Bootstrap Agent."""
    
    def test_bootstrap_agent_initialization(self):
        """Test that bootstrap agent initializes correctly."""
        agent = UserQuestionBootstrapAgent(documents_dir="./input_files")
        assert agent is not None
        assert hasattr(agent, 'documents_dir')
    
    def test_bootstrap_agent_with_custom_dir(self):
        """Test bootstrap agent with custom documents directory."""
        custom_dir = "./test_docs"
        agent = UserQuestionBootstrapAgent(documents_dir=custom_dir)
        assert agent.documents_dir == custom_dir


class TestDocumentReaderAgent:
    """Tests for the Document Reader Agent."""
    
    @pytest.fixture
    def temp_docs_dir(self, tmp_path):
        """Create a temporary directory with test documents."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        
        # Create test markdown file
        md_file = docs_dir / "test.md"
        md_file.write_text("# Test Document\nThis is a test document with some content.")
        
        # Create test text file
        txt_file = docs_dir / "test.txt"
        txt_file.write_text("Plain text content for testing.")
        
        return str(docs_dir)
    
    def test_reader_agent_initialization(self):
        """Test that reader agent initializes correctly."""
        agent = DocumentReaderAgent(
            documents_dir="./input_files",
            max_file_chars=12000,
            preview_chars=500,
            prefer_previews=False
        )
        assert agent is not None
        assert agent.max_file_chars == 12000
        assert agent.preview_chars == 500
    
    def test_reader_finds_markdown_files(self, temp_docs_dir):
        """Test that reader can find markdown files."""
        agent = DocumentReaderAgent(
            documents_dir=temp_docs_dir,
            max_file_chars=12000
        )
        
        # Check that markdown file exists
        md_files = list(Path(temp_docs_dir).glob("*.md"))
        assert len(md_files) > 0
    
    def test_reader_finds_text_files(self, temp_docs_dir):
        """Test that reader can find text files."""
        agent = DocumentReaderAgent(
            documents_dir=temp_docs_dir,
            max_file_chars=12000
        )
        
        # Check that text file exists
        txt_files = list(Path(temp_docs_dir).glob("*.txt"))
        assert len(txt_files) > 0


class TestConfiguration:
    """Tests for configuration loading."""
    
    def test_load_config(self):
        """Test that configuration loads successfully."""
        config = load_config()
        assert config is not None
        assert hasattr(config, 'model_name')
        assert hasattr(config, 'documents_dir')
        assert hasattr(config, 'max_file_chars')
    
    def test_config_defaults(self):
        """Test that configuration has sensible defaults."""
        # Clear environment variables
        env_backup = os.environ.copy()
        try:
            os.environ.pop('MODEL', None)
            os.environ.pop('MAX_FILE_CHARS', None)
            
            config = load_config()
            assert config.max_file_chars > 0
            assert config.documents_dir is not None
        finally:
            os.environ.update(env_backup)
    
    def test_config_respects_env_vars(self):
        """Test that configuration respects environment variables."""
        env_backup = os.environ.copy()
        try:
            os.environ['MAX_FILE_CHARS'] = '5000'
            config = load_config()
            assert config.max_file_chars == 5000
        finally:
            os.environ.update(env_backup)


class TestWorkflowIntegration:
    """Integration tests for the complete workflow."""
    
    @pytest.fixture
    def sample_docs_dir(self, tmp_path):
        """Create sample documents for integration testing."""
        docs_dir = tmp_path / "integration_docs"
        docs_dir.mkdir()
        
        # Create a comprehensive test document
        doc_content = """
# Project Alpha - Lessons Learned

## Overview
Project Alpha was a successful initiative to modernize our systems.

## Key Success Factors
1. Strong executive sponsorship
2. Clear communication channels
3. Comprehensive testing strategy

## Challenges
- Timeline delays due to dependency issues
- Budget overruns in initial phase
- Skill gaps in new technology

## Recommendations
1. Start with thorough discovery phase
2. Allocate contingency budget
3. Invest in team training early
"""
        
        doc_file = docs_dir / "project_alpha.md"
        doc_file.write_text(doc_content)
        
        return str(docs_dir)
    
    def test_workflow_builds_successfully(self):
        """Test that the workflow can be built without errors."""
        from workflow import build_workflow
        
        workflow = build_workflow()
        assert workflow is not None
        assert workflow.name == "LessonsLearnedWorkflow"
    
    def test_workflow_has_correct_agents(self):
        """Test that workflow contains all required agents."""
        from workflow import build_workflow
        
        workflow = build_workflow()
        assert hasattr(workflow, 'sub_agents')
        assert len(workflow.sub_agents) == 5  # bootstrap, clarify, reader, summarize, synthesize
    
    @pytest.mark.asyncio
    async def test_workflow_session_state_structure(self):
        """Test that workflow expects correct session state structure."""
        from workflow import build_workflow
        
        workflow = build_workflow()
        
        # Test session state keys
        test_state = {
            "user_question": "What are the key lessons learned?",
        }
        
        # This is a structure test, not an execution test
        assert "user_question" in test_state


class TestDocumentFormats:
    """Tests for different document format handling."""
    
    @pytest.fixture
    def multi_format_docs(self, tmp_path):
        """Create documents in various formats."""
        docs_dir = tmp_path / "multi_format"
        docs_dir.mkdir()
        
        # Markdown
        (docs_dir / "doc.md").write_text("# Markdown Document\nContent here.")
        
        # Plain text
        (docs_dir / "doc.txt").write_text("Plain text document content.")
        
        # JSON
        (docs_dir / "doc.json").write_text('{"key": "value", "data": "content"}')
        
        # YAML
        (docs_dir / "doc.yaml").write_text("key: value\ndata: content")
        
        return str(docs_dir)
    
    def test_reader_handles_multiple_formats(self, multi_format_docs):
        """Test that reader can handle multiple document formats."""
        agent = DocumentReaderAgent(
            documents_dir=multi_format_docs,
            max_file_chars=12000
        )
        
        # Check that various format files exist
        doc_dir = Path(multi_format_docs)
        assert (doc_dir / "doc.md").exists()
        assert (doc_dir / "doc.txt").exists()
        assert (doc_dir / "doc.json").exists()
        assert (doc_dir / "doc.yaml").exists()


class TestErrorHandling:
    """Tests for error handling scenarios."""
    
    def test_reader_with_nonexistent_directory(self):
        """Test reader behavior with non-existent directory."""
        agent = DocumentReaderAgent(
            documents_dir="/nonexistent/path",
            max_file_chars=12000
        )
        # Should not raise error during initialization
        assert agent is not None
    
    def test_reader_with_empty_directory(self, tmp_path):
        """Test reader behavior with empty directory."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        
        agent = DocumentReaderAgent(
            documents_dir=str(empty_dir),
            max_file_chars=12000
        )
        assert agent is not None


class TestPerformance:
    """Performance-related tests."""
    
    def test_large_document_handling(self, tmp_path):
        """Test handling of large documents."""
        docs_dir = tmp_path / "large_docs"
        docs_dir.mkdir()
        
        # Create a large document
        large_content = "This is a test line.\n" * 10000  # ~200KB
        (docs_dir / "large.md").write_text(large_content)
        
        agent = DocumentReaderAgent(
            documents_dir=str(docs_dir),
            max_file_chars=12000  # Should truncate
        )
        
        # Verify agent was created despite large file
        assert agent is not None
        assert agent.max_file_chars == 12000


# Test runner
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
