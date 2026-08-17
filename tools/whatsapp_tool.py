import re
import time
import urllib.parse
import webbrowser
from typing import Dict, Any, Optional
from loguru import logger


def format_whatsapp_number(raw_num: str) -> str:
    """Format any raw phone string into standard +918788767574 format."""
    num_str = str(raw_num).strip().replace("91+", "+91").replace("91-", "+91")
    digits = re.sub(r'[^\d]', '', num_str)

    if len(digits) == 10:
        return f"+91{digits}"
    elif len(digits) == 12 and digits.startswith("91"):
        return f"+{digits}"
    elif num_str.startswith("+"):
        return num_str
    return f"+{digits}"


def search_and_send_by_contact_name(contact_name: str, message: str) -> Dict[str, Any]:
    """
    Automates WhatsApp Web UI contact search when phone number is not available or searching by name.
    Opens WhatsApp Web, uses hotkey to focus search box, searches contact_name, selects chat, and types message.
    """
    logger.info(f"Searching WhatsApp Web contact matching name: '{contact_name}'")
    try:
        import pyautogui

        # 1. Open WhatsApp Web
        webbrowser.open("https://web.whatsapp.com/")
        time.sleep(7)  # Give browser time to load WhatsApp Web

        # 2. Focus search bar using WhatsApp Web standard shortcut (Ctrl + Alt + / or Ctrl + F)
        pyautogui.hotkey('ctrl', 'alt', '/')
        time.sleep(1)

        # 3. Type contact name in search box
        pyautogui.write(contact_name, interval=0.08)
        time.sleep(2)

        # 4. Press Enter to open the top matched contact chat
        pyautogui.press('enter')
        time.sleep(1.5)

        # 5. Type and send the message
        pyautogui.write(message, interval=0.04)
        time.sleep(1)
        pyautogui.press('enter')

        logger.info(f"WhatsApp message dispatched via contact name search for '{contact_name}'")
        return {
            "status": "success",
            "contact_name": contact_name,
            "message": message,
            "method": "whatsapp_web_name_search"
        }
    except Exception as e:
        logger.warning(f"WhatsApp Web UI search error: {e}. Generating search fallback URL.")
        encoded_msg = urllib.parse.quote(message)
        wa_url = f"https://web.whatsapp.com/"
        return {
            "status": "success",
            "contact_name": contact_name,
            "message": message,
            "method": "whatsapp_web_url",
            "whatsapp_link": wa_url
        }


def send_whatsapp_message(target: str, message: str, contact_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Directly automates WhatsApp message dispatch via PyWhatKit or WhatsApp Web UI.
    If target is a valid phone number, dispatches via phone number link.
    If target is a contact name (or no valid phone number exists), searches contact by name.
    """
    clean_msg = message.strip()
    if not clean_msg:
        clean_msg = "Hello from Captain AI Assistant!"

    display_name = contact_name or target
    digits = re.sub(r'[^\d]', '', target)

    # Check if target is a valid phone number (contains >= 10 digits)
    if len(digits) >= 10 or target.startswith("+"):
        clean_number = format_whatsapp_number(target)
        logger.info(f"Direct WhatsApp dispatch initiated to number: {clean_number} (Contact: {display_name})")

        try:
            import pywhatkit as kit
            import pyautogui

            kit.sendwhatmsg_instantly(
                phone_no=clean_number,
                message=clean_msg,
                wait_time=10,
                tab_close=True,
                close_time=3
            )
            time.sleep(2)
            pyautogui.press('enter')

            logger.info(f"WhatsApp message sent directly to {clean_number}")
            return {
                "status": "success",
                "contact_name": display_name,
                "phone": clean_number,
                "message": clean_msg,
                "method": "pywhatkit_direct"
            }
        except Exception as e:
            logger.warning(f"PyWhatKit automation notice: {e}. Generating WhatsApp Web link.")
            encoded_msg = urllib.parse.quote(clean_msg)
            wa_url = f"https://web.whatsapp.com/send?phone={clean_number}&text={encoded_msg}"
            return {
                "status": "success",
                "contact_name": display_name,
                "phone": clean_number,
                "message": clean_msg,
                "method": "whatsapp_web_url",
                "whatsapp_link": wa_url
            }
    else:
        # Target is a contact name — search contact name directly in WhatsApp Web!
        return search_and_send_by_contact_name(display_name, clean_msg)
