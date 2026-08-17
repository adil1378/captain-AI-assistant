"""
Captain AI OS — Telegram Bot Tool
Pattern ported from: ge-ai-apps/telegrambot/tele.py
Uses modern Telegram Bot API via requests (no deprecated telepot).
Bugs from original (bot_gpt.sendMessage typo, hardcoded key) are fixed here.
"""

import requests
from typing import Dict, Any, Optional
from loguru import logger
from config import settings


def _get_bot_token() -> Optional[str]:
    """Return the Telegram bot token from config/env."""
    return settings.telegram_bot_token


def _telegram_api(method: str, payload: Dict) -> Dict[str, Any]:
    """
    Generic Telegram Bot API caller.
    Endpoint: https://api.telegram.org/bot<TOKEN>/<method>
    """
    token = _get_bot_token()
    if not token:
        return {"ok": False, "description": "TELEGRAM_BOT_TOKEN not configured in .env"}

    url = f"https://api.telegram.org/bot{token}/{method}"
    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.Timeout:
        return {"ok": False, "description": "Telegram API request timed out"}
    except Exception as e:
        return {"ok": False, "description": str(e)}


def send_telegram_message(chat_id: str, text: str) -> Dict[str, Any]:
    """
    Send a text message to a Telegram chat.
    Fix of original tele.py bug: used bot_gpt.sendMessage (wrong ref) → now uses API directly.

    Args:
        chat_id: Telegram user/group chat ID (as string or int)
        text:    Message body to send

    Returns:
        Dict with status, message_id, chat_id
    """
    if not text.strip():
        text = "Hello from Captain AI!"

    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }

    logger.info(f"TelegramTool: Sending message to chat_id={chat_id}")
    result = _telegram_api("sendMessage", payload)

    if result.get("ok"):
        msg = result.get("result", {})
        logger.info(f"TelegramTool: Message sent — message_id={msg.get('message_id')}")
        return {
            "status": "success",
            "chat_id": chat_id,
            "message_id": msg.get("message_id"),
            "text": text,
        }
    else:
        error = result.get("description", "Unknown Telegram API error")
        logger.error(f"TelegramTool: Send failed — {error}")
        return {
            "status": "error",
            "chat_id": chat_id,
            "error": error,
        }


def get_telegram_bot_info() -> Dict[str, Any]:
    """
    Call getMe to validate the bot token and return bot metadata.
    Returns bot username, id, and display name.
    """
    result = _telegram_api("getMe", {})
    if result.get("ok"):
        bot = result.get("result", {})
        return {
            "status": "success",
            "bot_id": bot.get("id"),
            "username": bot.get("username"),
            "first_name": bot.get("first_name"),
        }
    return {
        "status": "error",
        "error": result.get("description", "Failed to get bot info"),
    }


def get_telegram_updates(offset: int = 0, limit: int = 10) -> Dict[str, Any]:
    """
    Poll for the latest messages sent to the bot.
    Useful for reading what users said without a webhook.

    Args:
        offset: Update ID to start from (for pagination)
        limit:  Max updates to fetch

    Returns:
        Dict with status and list of updates
    """
    result = _telegram_api("getUpdates", {"offset": offset, "limit": limit, "timeout": 5})
    if result.get("ok"):
        updates = result.get("result", [])
        messages = []
        for upd in updates:
            msg = upd.get("message", {})
            messages.append({
                "update_id": upd.get("update_id"),
                "chat_id": msg.get("chat", {}).get("id"),
                "from": msg.get("from", {}).get("first_name", "Unknown"),
                "text": msg.get("text", ""),
            })
        return {"status": "success", "updates": messages}
    return {"status": "error", "error": result.get("description", "Failed to get updates")}
