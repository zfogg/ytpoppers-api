import os
import argparse
from typing import List, Dict
from googleapiclient.discovery import build
from dotenv import load_dotenv

class YouTubeAnalyzer:
    def __init__(self, api_key: str):
        """Initialize the YouTube API client."""
        self.youtube = build('youtube', 'v3', developerKey=api_key)
        self.total_videos = 0

    def get_channel_videos(self, channel_id: str, max_results: int = 50) -> List[Dict]:
        """
        Fetch ALL videos from a channel and return the top ones sorted by view count.
        
        Args:
            channel_id: The YouTube channel ID
            max_results: Maximum number of videos to return in final results (default: 50)
            
        Returns:
            List of video information dictionaries sorted by view count
        """
        # First, get the channel's uploaded videos playlist ID
        channel_response = self.youtube.channels().list(
            part='contentDetails',
            id=channel_id
        ).execute()

        if not channel_response['items']:
            raise ValueError(f"No channel found with ID: {channel_id}")

        uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        # Get videos from the uploads playlist
        videos = []
        next_page_token = None

        while True:
            playlist_response = self.youtube.playlistItems().list(
                part='snippet',
                playlistId=uploads_playlist_id,
                maxResults=50,  # This is the max allowed by the API per request
                pageToken=next_page_token
            ).execute()

            video_ids = [item['snippet']['resourceId']['videoId'] 
                        for item in playlist_response['items']]

            # Get video statistics
            video_response = self.youtube.videos().list(
                part='statistics,snippet',
                id=','.join(video_ids)
            ).execute()

            for video in video_response['items']:
                video_info = {
                    'title': video['snippet']['title'],
                    'video_id': video['id'],
                    'view_count': int(video['statistics'].get('viewCount', 0)),
                    'like_count': int(video['statistics'].get('likeCount', 0)),
                    'comment_count': int(video['statistics'].get('commentCount', 0)),
                    'url': f"https://youtube.com/watch?v={video['id']}"
                }
                videos.append(video_info)
                self.total_videos += 1

            next_page_token = playlist_response.get('nextPageToken')
            print(f"Fetched {self.total_videos} videos so far...")
            
            if not next_page_token:
                break

        print(f"\nFinished fetching all {self.total_videos} videos from the channel")
        # Sort all videos by view count and return the top max_results
        return sorted(videos, key=lambda x: x['view_count'], reverse=True)[:max_results]

    def print_video_stats(self, videos: List[Dict]) -> None:
        """Print formatted video statistics."""
        print(f"\nExamined {self.total_videos} total videos")
        print("\nTop Most Popular Videos:")
        print("-" * 100)
        
        for i, video in enumerate(videos, 1):
            print(f"{i}. {video['title']}")
            print(f"   Views: {video['view_count']:,}")
            print(f"   Likes: {video['like_count']:,}")
            print(f"   Comments: {video['comment_count']:,}")
            print(f"   URL: {video['url']}")
            print("-" * 100)

def main():
    parser = argparse.ArgumentParser(description='Analyze YouTube channel videos')
    parser.add_argument('--channel-id', required=True, help='YouTube channel ID')
    parser.add_argument('--max-results', type=int, default=10, help='Maximum number of videos to display')
    args = parser.parse_args()

    # Load environment variables
    load_dotenv()
    api_key = os.getenv('YOUTUBE_API_KEY')
    
    if not api_key:
        raise ValueError("Please set YOUTUBE_API_KEY in your .env file")

    try:
        analyzer = YouTubeAnalyzer(api_key)
        videos = analyzer.get_channel_videos(args.channel_id, args.max_results)
        analyzer.print_video_stats(videos)
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == '__main__':
    main()
