import httpx
from bs4 import BeautifulSoup
from typing import Dict, Any
from loguru import logger


def scrape_webpage(url: str, max_chars: int = 4000) -> Dict[str, Any]:
    """Scrape web page text content from given URL."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        with httpx.Client(timeout=15.0, follow_redirects=True, headers=headers) as client:
            resp = client.get(url)
            resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        # Remove script, style, nav, footer tags
        for tag in soup(["script", "style", "nav", "footer", "header", "noscript", "svg"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)
        # Trim multiple blank lines
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        cleaned_text = "\n".join(lines)[:max_chars]

        title = soup.title.string.strip() if soup.title else url
        logger.info(f"Successfully scraped webpage: {url} (Title: {title})")

        return {
            "status": "success",
            "url": url,
            "title": title,
            "content": cleaned_text
        }
    except Exception as e:
        logger.error(f"Error scraping webpage {url}: {e}")
        return {"status": "error", "error": str(e)}
