import pytest
from src.summary_generator import SummaryGenerator

def test_summarize():
    summarizer = SummaryGenerator()
    summary = summarizer.summarize('This is a test content.')
    assert isinstance(summary, str)
    assert len(summary) > 0
