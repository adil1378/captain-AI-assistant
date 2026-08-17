import re
from typing import Dict, Any
from langchain_core.messages import AIMessage
from src.agents.state import AgentState
from src.agents.base_agent import BaseAgent, AgentMetadata
from tools.whatsapp_tool import send_whatsapp_message
from tools.email_tool import send_email
from tools.contacts import save_contact, get_contact_value, get_contact_details
from loguru import logger


class CommsAgent(BaseAgent):
    """Production Email, WhatsApp & Contact Management Agent."""

    @property
    def metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="comms_agent",
            description="Email, WhatsApp, and Contact Book Automation Agent",
            version="2.0.0",
            capabilities=["email", "whatsapp", "contact_management"]
        )

    def _extract_message_body(self, query: str) -> str:
        """Extract the message body from natural language."""
        match = re.search(
            r'(?:say|send|tell|message|write|that)\s+["\']?(.+?)["\']?$',
            query, re.IGNORECASE
        )
        return match.group(1).strip() if match else query

    def _extract_contact_info(self, query: str):
        """Extract name and value from a save/add contact command."""
        match = re.search(
            r'(?:save|add)\s+contact\s+([a-zA-Z0-9\s]+?)\s+(?:as|=|:|phone|email|number)?\s*([\+\d\s\-\@\.]+)',
            query, re.IGNORECASE
        )
        if match:
            return match.group(1).strip(), match.group(2).strip()
        return None, None

    async def execute(self, state: AgentState) -> Dict[str, Any]:
        user_query = state.get("user_query", "")
        scratchpad = state.get("scratchpad", {})
        q_lower = user_query.lower()

        # --- 1. Save / Add Contact ---
        if "save contact" in q_lower or "add contact" in q_lower:
            name, value = self._extract_contact_info(user_query)
            if name and value:
                success = save_contact(name, value)
                msg = (
                    f"✅ Contact **{name}** saved as `{value}`."
                    if success
                    else f"❌ Failed to save contact **{name}**. Check disk permissions."
                )
                logger.info(f"CommsAgent: save_contact('{name}', '{value}') → {success}")
            else:
                msg = (
                    "❌ Could not parse contact details. "
                    "Try: *save contact John as +923001234567*"
                )
            return {
                "messages": [AIMessage(content=msg)],
                "scratchpad": scratchpad,
                "current_agent": self.metadata.name,
                "next_agent": "END",
            }

        # --- 2. WhatsApp ---
        if "whatsapp" in q_lower or ("message" in q_lower and "email" not in q_lower):
            contact_name, recipient = get_contact_details(user_query)
            target = recipient or contact_name
            if not target:
                return {
                    "messages": [AIMessage(content=(
                        "❌ Could not find recipient in query or address book. "
                        "Try: *send whatsapp to Arfat saying hello* or *save contact Arfat as +91XXXXXXXXXX*"
                    ))],
                    "current_agent": self.metadata.name,
                    "next_agent": "END",
                }

            body = self._extract_message_body(user_query)
            result = send_whatsapp_message(target=target, message=body, contact_name=contact_name)
            
            display_name = contact_name or target
            phone_info = f" ({recipient})" if recipient and recipient != target else ""
            msg = f"📬 WhatsApp → **{display_name}**{phone_info}: Message dispatches successfully! Message: *\"{body}\"*"
            
            logger.info(f"CommsAgent: send_whatsapp('{display_name}', '{target}') → success")
            return {
                "messages": [AIMessage(content=msg)],
                "scratchpad": scratchpad,
                "current_agent": self.metadata.name,
                "next_agent": "END",
            }

        # --- 3. Email ---
        if "email" in q_lower or "mail" in q_lower:
            contact_name, recipient = get_contact_details(user_query)
            if not recipient or "@" not in recipient:
                return {
                    "messages": [AIMessage(content=(
                        "❌ Valid email recipient not found. "
                        "Please include an email address or save a contact with an email using *save contact John as john@example.com*"
                    ))],
                    "current_agent": self.metadata.name,
                    "next_agent": "END",
                }

            body = self._extract_message_body(user_query)
            result = send_email(to_email=recipient, subject="Message from Captain AI", body=body)
            status = result.get("status", "success")
            display_name = contact_name or recipient
            msg = f"📧 Email → **{display_name}** (`{recipient}`): {status}. Message: *\"{body}\"*"
            logger.info(f"CommsAgent: send_email('{display_name}') → {status}")
            return {
                "messages": [AIMessage(content=msg)],
                "scratchpad": scratchpad,
                "current_agent": self.metadata.name,
                "next_agent": "END",
            }

        # --- Fallback ---
        return {
            "messages": [AIMessage(content=(
                "I can help with email, WhatsApp messages, and contact management. "
                "Try: *send email to john@example.com saying hello* "
                "or *send whatsapp to John saying hi*."
            ))],
            "current_agent": self.metadata.name,
            "next_agent": "END",
        }
