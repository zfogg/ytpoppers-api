from flask import Flask, jsonify, request
from youtube_analyzer import YouTubeAnalyzer
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
api_key = os.getenv('YOUTUBE_API_KEY')

if not api_key:
    raise ValueError("Please set YOUTUBE_API_KEY in your .env file")

app = Flask(__name__)
analyzer = YouTubeAnalyzer(api_key)

@app.route('/analyze', methods=['GET'])
def analyze_channel():
    """
    Endpoint to analyze a YouTube channel's videos.
    
    Query Parameters:
    - channel: The YouTube channel identifier (required) - can be:
        - Channel ID (e.g., UC...)
        - Channel URL (e.g., https://www.youtube.com/channel/UC...)
        - Custom URL (e.g., https://www.youtube.com/c/channelname)
        - Legacy username URL (e.g., https://www.youtube.com/user/username)
        - Handle URL (e.g., https://www.youtube.com/@handle)
        - Plain username or handle
    - max_results: Maximum number of top videos to return (optional, default: 10)
    
    Returns:
    JSON response containing:
    - channel_id: The YouTube channel ID
    - total_videos: Total number of videos analyzed
    - top_videos: List of top videos sorted by view count
    """
    channel_input = request.args.get('channel')
    max_results = request.args.get('max_results', default=10, type=int)
    
    if not channel_input:
        return jsonify({
            'error': 'Missing channel parameter'
        }), 400
    
    try:
        # First get the channel ID from the input
        channel_id = analyzer.get_channel_id(channel_input)
        
        # Then get the videos using the channel ID
        total_videos, videos = analyzer.get_channel_videos(channel_id, max_results)
        
        return jsonify({
            'channel_id': channel_id,
            'total_videos_analyzed': total_videos,
            'top_videos': videos
        })
    
    except ValueError as e:
        return jsonify({
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

if __name__ == '__main__':
    from waitress import serve
    port = os.getenv('PORT', 5000)
    print(f"Starting server on http://0.0.0.0:{port}")
    serve(app, host='0.0.0.0', port=port)
