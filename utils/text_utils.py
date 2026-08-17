import re

def clean_think_tags(text: str) -> str:
    """
    Remove reasoning/thinking tags (e.g. <think>...</think>) from LLM outputs.
    Ensures clean text presentation for terminal, GUI, and audio TTS engines.
    """
    if not text:
        return ""
    cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
    if '<think>' in cleaned:
        cleaned = cleaned.split('<think>')[0].strip()
    if not cleaned:
        think_match = re.search(r'<think>(.*?)</think>', text, flags=re.DOTALL)
        if think_match:
            cleaned = think_match.group(1).strip()
        else:
            cleaned = text.replace("<think>", "").replace("</think>", "").strip()
    return cleaned
