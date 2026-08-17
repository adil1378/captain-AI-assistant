import re
from typing import Dict, Any
from langchain_core.messages import AIMessage
from agents.state import AgentState
from tools.whatsapp_tool import send_whatsapp_message
from tools.email_tool import send_email
from tools.contacts import save_contact, get_contact_value
from loguru import logger


def comms_agent_node(state: AgentState) -> Dict[str, Any]:
    """Email, WhatsApp, and Contact Address Book Automation Agent Node."""
    user_query = state.get("user_query", "")
    scratchpad = state.get("scratchpad", {})
    q_lower = user_query.lower()

    # 1. Contact Save / Add Action
    if "save contact" in q_lower or "add contact" in q_lower:
        match = re.search(r'(?:save|add)\s+contact\s+([a-zA-Z0-9\s]+?)\s+(?:as|=|\:|\s+)\s*([\+\d\s\-\@\.]+)', user_query, re.IGNORECASE)
        if match:
            c_name = match.group(1).strip()
            c_val = match.group(2).strip()
            if save_contact(c_name, c_val):
                return {
                    "messages": [AIMessage(content=f"✅ Contact '{c_name}' saved successfully as '{c_val}'.")],
                    "current_agent": "comms_agent"
                }
            else:
                return {
                    "messages": [AIMessage(content=f"❌ Failed to save contact '{c_name}'. Check disk permissions.")],
                    "current_agent": "comms_agent"
                }

    # 2. WhatsApp Message Dispatch
    if "whatsapp" in q_lower or "message" in q_lower:
        recipient = get_contact_value(user_query)
        msg_match = re.search(r'(?:hello|hi|hey|say|send|tell|that|message)\s+(.*)', user_query, re.IGNORECASE)
        message_body = msg_match.group(1) if msg_match else user_query

        if not recipient:
            return {
                "messages": [AIMessage(content="❌ Could not resolve contact in address book. Please specify phone number or save contact first.")],
                "current_agent": "comms_agent"
            }

        res = send_whatsapp_message(recipient, message_body)
        return {
            "messages": [AIMessage(content=f"📬 WhatsApp Message Status: {res.get('status')}. Detail: {res.get('detail', res.get('error'))}")],
            "scratchpad": scratchpad,
            "current_agent": "comms_agent"
        }

    # 3. Email Dispatch
    if "email" in q_lower or "mail" in q_lower:
        recipient = get_contact_value(user_query)
        if not recipient or "@" not in recipient:
            return {
                "messages": [AIMessage(content="❌ Valid email recipient not found in request or address book.")],
                "current_agent": "comms_agent"
            }

        res = send_email(to_email=recipient, subject="Message from Captain AI", body=user_query)
        return {
            "messages": [AIMessage(content=f"📧 Email Status: {res.get('status')}. Detail: {res.get('detail', res.get('error'))}")],
            "scratchpad": scratchpad,
            "current_agent": "comms_agent"
        }

    return {
        "messages": [AIMessage(content="CommsAgent processing completed.")],
        "current_agent": "comms_agent"
    }
