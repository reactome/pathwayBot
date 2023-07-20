import pytest
from src.chatbot_ui import ChatbotUI

def test_get_user_query():
    chatbot_ui = ChatbotUI()
    query = chatbot_ui.get_user_query()
    assert isinstance(query, str)
    assert len(query) > 0

def test_display_summary():
    chatbot_ui = ChatbotUI()
    summary = 'This is a test summary.'
    assert chatbot_ui.display_summary(summary) == None
