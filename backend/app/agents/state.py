from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):
    # Context & Session
    user_id: str
    conversation_id: str
    user_message: str
    attached_doc_ids: List[str]
    
    # Classification & Routing
    intent: str  # 'chat', 'rag', 'research', 'document_generation', 'document_editing'
    target_format: str  # 'docx', 'pptx', 'xlsx', 'none'
    requires_research: bool
    requires_rag: bool
    
    # Agent Artifacts
    document_structures: List[Dict[str, Any]]
    rag_context: List[Dict[str, Any]]
    research_results: List[Dict[str, Any]]
    draft_content: Dict[str, Any]
    editing_instructions: Dict[str, Any]
    validation_result: Dict[str, Any]
    generated_doc_info: Optional[Dict[str, Any]]
    
    # Final Output
    final_response: str
    citations: List[Dict[str, Any]]
    execution_logs: List[Dict[str, Any]]
    errors: List[str]
