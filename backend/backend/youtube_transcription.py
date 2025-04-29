import re
from youtube_transcript_api import YouTubeTranscriptApi
import logging

logger = logging.getLogger('context-backend')

def get_video_id(youtube_url):
    """Extract the video ID from a YouTube URL."""
    youtube_regex = r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
    match = re.search(youtube_regex, youtube_url)
    
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid YouTube URL")

def get_transcript(youtube_url):
    """Get transcript from a YouTube video URL."""
    try:
        video_id = get_video_id(youtube_url)
        
        # List available transcripts for the video
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Prefer auto-generated transcripts if available
        auto_transcript = None
        any_transcript = None
        
        # Find the first auto-generated transcript
        for transcript in transcript_list:
            if transcript.is_generated:
                auto_transcript = transcript
                break
            if not any_transcript:
                any_transcript = transcript
        
        # Use auto-generated transcript if found, else use any available transcript
        chosen_transcript = auto_transcript or any_transcript
        
        if not chosen_transcript:
            raise ValueError("No transcript available for this video")
        
        # Fetch transcript data
        transcript_data = chosen_transcript.fetch()
        
        # Handle transcript entries as dicts or objects (for compatibility with different library versions)

        processed_fragments = []
        for entry in transcript_data:
            try:
                if isinstance(entry, dict):
                    processed_fragments.append(entry.get('text', ''))
                elif hasattr(entry, 'text'):
                    processed_fragments.append(getattr(entry, 'text', ''))
                else:
                    processed_fragments.append(str(entry))
            except Exception as ex:
                logger.error(f"Failed to parse transcript entry {entry}: {ex}")
        transcript_text = ' '.join(processed_fragments)
        
        return transcript_text
        
    except Exception as e:
        logger.error(f"Error getting YouTube transcript: {str(e)}")
        raise 