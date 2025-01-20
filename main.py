import os
import argparse
from waitress import serve
from api.youtube_analyzer import YouTubeAnalyzer
from api.app import app
from api.logger import logger

# Load environment variables
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('YOUTUBE_API_KEY')
if not api_key:
    raise ValueError("Please set YOUTUBE_API_KEY in your .env file")

def main():
    parser = argparse.ArgumentParser(description='Analyze YouTube channel videos')
    parser.add_argument('--server', default=True, required=False, action='store_true', help='Start the flask server')
    parser.add_argument('--channel-id', required=False, help='YouTube channel ID')
    parser.add_argument('--max-results', type=int, default=10, help='Maximum number of videos to display')
    args = parser.parse_args()

    if args.server and not args.channel_id:
        port = os.getenv('PORT', 5000)
        #logger.info(f"Starting server on http://0.0.0.0:{port}")
        serve(app, host='0.0.0.0', port=port)
        return

    try:
        analyzer = YouTubeAnalyzer(api_key)
        channel_id = analyzer.get_channel_id(args.channel_id)
        total_videos, videos = analyzer.get_channel_videos(channel_id, args.max_results)
        analyzer.print_video_stats(total_videos, videos)
    except Exception as e:
        logger.error(f"An error occurred while trying to analyze the channel's videos: {str(e)}")

if __name__ == '__main__':
    main()