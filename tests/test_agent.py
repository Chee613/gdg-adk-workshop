from agent import root_agent


def test_agent_has_correct_name():
    assert root_agent.name == "email_assistant"


def test_agent_has_correct_model():
    assert root_agent.model == "gemini-2.5-flash"


def test_agent_has_all_tools():
    tool_names = [t.__name__ for t in root_agent.tools]
    assert "get_unread_emails" in tool_names
    assert "draft_reply" in tool_names
    assert "get_labels" in tool_names
    assert "create_label" in tool_names
    assert "apply_label" in tool_names
    assert "save_preference" in tool_names
    assert "load_preferences" in tool_names

def test_agent_instruction_is_not_empty():
    assert root_agent.instruction is not None
    assert len(root_agent.instruction.strip()) > 0


def test_agent_instruction_mentions_drafting():
    assert "draft" in root_agent.instruction.lower()