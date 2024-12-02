# YouTube Channel Analytics

This Python application analyzes YouTube channels to find their most popular videos using the YouTube Data API.

## Setup

1. Create a Google Cloud Project and enable the YouTube Data API v3
2. Create API credentials (API Key) from the Google Cloud Console
3. Create a `.env` file in the project root and add your API key:
   ```
   YOUTUBE_API_KEY=your_api_key_here
   ```

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Run the main script with a YouTube channel ID:
```bash
python youtube_analyzer.py --channel-id CHANNEL_ID
```

Note: You can find a channel ID by going to the channel's page and looking in the URL, or using a channel ID finder tool.

## Features
- Fetches and displays the most popular videos from a YouTube channel
- Sorts videos by view count
- Shows key metrics like views, likes, and comments
