import os
import argparse
from dotenv import load_dotenv
from waitress import serve
from api.youtube_analyzer import YouTubeAnalyzer
from api.app import app

def main():
    parser = argparse.ArgumentParser(description='Analyze YouTube channel videos')
    parser.add_argument('--server', required=False, default=True, help='Start the flask server')
    parser.add_argument('--channel-id', required=False, help='YouTube channel ID')
    parser.add_argument('--max-results', type=int, default=10, help='Maximum number of videos to display')
    args = parser.parse_args()

    if args.server:
        port = os.getenv('PORT', 5000)
        print(f"Starting server on http://0.0.0.0:{port}")
        serve(app, host='0.0.0.0', port=port)
        return

    # Load environment variables
    load_dotenv()
    api_key = os.getenv('YOUTUBE_API_KEY')

    if not api_key:
        raise ValueError("Please set YOUTUBE_API_KEY in your .env file")

    try:
        analyzer = YouTubeAnalyzer(api_key)
        channel_id = analyzer.get_channel_id(args.channel_id)
        total_videos, videos = analyzer.get_channel_videos(channel_id, args.max_results)
        analyzer.print_video_stats(total_videos, videos)
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == '__main__':
    main()