import sys
import re
from youtube_transcript_api import YouTubeTranscriptApi

def get_video_id(youtube_url):
    """Extract the video ID from a YouTube URL."""
    youtube_regex = r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
    match = re.search(youtube_regex, youtube_url)
    
    if match:
        return match.group(1)
    else:
        sys.exit(1)

def get_transcript(youtube_url):
    try:
        video_id = get_video_id(youtube_url)
        
        # Get list of available transcripts
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Preference for auto-generated transcripts
        auto_transcript = None
        any_transcript = None
        
        # Find auto-generated transcript
        for transcript in transcript_list:
            if transcript.is_generated:
                auto_transcript = transcript
                break
            if not any_transcript:
                any_transcript = transcript
        
        # Use auto-generated if available, otherwise use any transcript
        chosen_transcript = auto_transcript or any_transcript
        
        # Get transcript data
        transcript_data = chosen_transcript.fetch()
        transcript_text = ' '.join([item['text'] for item in transcript_data])
        
        return transcript_text
        
    except Exception:
        sys.exit(1)

def main():
    if len(sys.argv) > 1:
        youtube_url = sys.argv[1]
    else:
        youtube_url = input()
    
    transcript = get_transcript(youtube_url)
    print(transcript)

if __name__ == "__main__":
    main()