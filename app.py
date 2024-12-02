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
    - channel_id: The YouTube channel ID (required)
    - max_results: Maximum number of top videos to return (optional, default: 10)
    
    Returns:
    JSON response containing:
    - total_videos: Total number of videos analyzed
    - top_videos: List of top videos sorted by view count
    """
    channel_id = request.args.get('channel_id')
    max_results = request.args.get('max_results', default=10, type=int)
    print(request.args)
    
    if not channel_id:
        return jsonify({
            'error': 'Missing channel_id parameter'
        }), 400
    
    try:
        total_videos, videos = analyzer.get_channel_videos(channel_id, max_results)
        
        return jsonify({
            'total_videos_analyzed': total_videos,
            'top_videos': videos
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

if __name__ == '__main__':
    from waitress import serve
    port = os.getenv('PORT', 5000)
    print(f"Starting server on http://localhost:{port}")
    serve(app, host='0.0.0.0', port=port)
