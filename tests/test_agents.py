import asyncio
import pytest
from backend.app.agents.graph import multi_agent_app
from backend.app.agents.state import AgentState

def test_multi_agent_chat_flow():
    initial_state: AgentState = {
        "user_id": "test_user_id",
        "conversation_id": "test_conv_id",
        "user_message": "Hello, what capabilities do you have for document generation?",
        "attached_doc_ids": [],
        "intent": "chat",
        "target_format": "none",
        "requires_research": False,
        "requires_rag": False,
        "document_structures": [],
        "rag_context": [],
        "research_results": [],
        "draft_content": {},
        "editing_instructions": {},
        "validation_result": {},
        "generated_doc_info": None,
        "final_response": "",
        "citations": [],
        "execution_logs": [],
        "errors": []
    }

    final_state = multi_agent_app.invoke(initial_state)
    assert len(final_state["final_response"]) > 0
    assert len(final_state["execution_logs"]) > 0
    agent_names = [log["agent"] for log in final_state["execution_logs"]]
    assert "Supervisor Agent" in agent_names
    assert "Response Agent" in agent_names

def test_multi_agent_generation_flow():
    initial_state: AgentState = {
        "user_id": "test_user_id",
        "conversation_id": "test_conv_id",
        "user_message": "Generate a new Word report for quarterly review",
        "attached_doc_ids": [],
        "intent": "document_generation",
        "target_format": "docx",
        "requires_research": False,
        "requires_rag": False,
        "document_structures": [],
        "rag_context": [],
        "research_results": [],
        "draft_content": {},
        "editing_instructions": {},
        "validation_result": {},
        "generated_doc_info": None,
        "final_response": "",
        "citations": [],
        "execution_logs": [],
        "errors": []
    }

    final_state = multi_agent_app.invoke(initial_state)
    assert final_state["generated_doc_info"] is not None
    assert final_state["generated_doc_info"]["file_type"] == "docx"

def test_multi_agent_rag_document_qa():
    initial_state: AgentState = {
        "user_id": "test_user_id",
        "conversation_id": "test_conv_id",
        "user_message": "What are the quarterly targets and achievement status mentioned in the document?",
        "attached_doc_ids": ["mock_attached_doc"],
        "intent": "chat",
        "target_format": "none",
        "requires_research": False,
        "requires_rag": False,
        "document_structures": [],
        "rag_context": [{"text": "Table: Division, Quarterly Target, Achievement Status | Autonomous Systems, $4.5M ARR, 112% Achieved | Document Intelligence, $3.2M ARR, 108% Achieved | Cloud Infrastructure, $6.1M ARR, 97% On Track"}],
        "research_results": [],
        "draft_content": {},
        "editing_instructions": {},
        "validation_result": {},
        "generated_doc_info": None,
        "final_response": "",
        "citations": [],
        "execution_logs": [],
        "errors": []
    }

    final_state = multi_agent_app.invoke(initial_state)
    assert final_state["intent"] == "rag"
    assert final_state["target_format"] == "none"
    assert final_state["generated_doc_info"] is None  # Must NOT generate a file!
    assert "Autonomous Systems" in final_state["final_response"]
    assert "$4.5M ARR" in final_state["final_response"]

if __name__ == "__main__":
    print("Testing test_multi_agent_rag_document_qa...")
    test_multi_agent_rag_document_qa()
    print("PASS: test_multi_agent_rag_document_qa")

    print("Testing test_multi_agent_chat_flow...")
    test_multi_agent_chat_flow()
    print("PASS: test_multi_agent_chat_flow")

    print("Testing test_multi_agent_generation_flow...")
    test_multi_agent_generation_flow()
    print("PASS: test_multi_agent_generation_flow")
    print("ALL AGENT TESTS PASSED!")
