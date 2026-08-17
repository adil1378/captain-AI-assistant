import re
from typing import Dict, Any
from loguru import logger
from youtube_transcript_api import YouTubeTranscriptApi


def extract_youtube_video_id(url: str) -> str:
    """Extract YouTube Video ID from various URL formats."""
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",
        r"youtu\.be\/([0-9A-Za-z_-]{11})",
        r"youtube\.com\/embed\/([0-9A-Za-z_-]{11})"
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return url if len(url) == 11 else ""


def get_youtube_transcript(url_or_id: str) -> Dict[str, Any]:
    """Fetch video transcript from a YouTube video URL or Video ID."""
    video_id = extract_youtube_video_id(url_or_id)
    if not video_id:
        return {"status": "error", "error": f"Invalid YouTube URL or Video ID: {url_or_id}"}

    try:
        api = YouTubeTranscriptApi()
        transcript_list = api.list_transcripts(video_id)

        # Try to find English, or fallback to any available transcript
        try:
            transcript = transcript_list.find_transcript(['en', 'en-US', 'en-GB'])
        except Exception:
            transcript = next(iter(transcript_list))

        fetched_data = transcript.fetch()
        full_text = " ".join([item.get('text', '') for item in fetched_data])

        logger.info(f"Successfully retrieved YouTube transcript for Video ID: {video_id} ({len(full_text)} chars)")
        return {
            "status": "success",
            "video_id": video_id,
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "transcript_text": full_text,
            "segments_count": len(fetched_data)
        }
    except Exception as e:
        logger.error(f"Error fetching YouTube transcript for {video_id}: {e}")
        return {"status": "error", "error": f"Could not retrieve transcript for YouTube video ({video_id}): {e}"}
