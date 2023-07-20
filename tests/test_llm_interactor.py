import pytest
from src.llm_interactor import LLMInteractor

def test_llmInteractor():
    llmI = LLMInteractor()
    llm = llmI.get_llm()
    assert llm.temperature == 0.1
    assert llm.model_name == "gpt-4"