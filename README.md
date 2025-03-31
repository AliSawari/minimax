# MiniMax - Video Compression Bot 🤖 🎥

A Telegram bot that compresses videos using FFmpeg.

## Environment Variables

The bot can be configured using the following environment variables in a `.env` file:

### Bot Configuration
- `BOT_TOKEN` - Your Telegram bot token from BotFather

### Connection Pool Settings
- `CONN_POOL_SIZE` - Size of the connection pool (default: 8)
- `READ_TIMEOUT` - Read timeout in seconds (default: 200)
- `WRITE_TIMEOUT` - Write timeout in seconds (default: 200)
- `CONNECT_TIMEOUT` - Connection timeout in seconds (default: 200)
- `POOL_TIMEOUT` - Pool timeout in seconds (default: 200)

### FFmpeg Settings
- `FFMPEG_CODEC` - Video codec to use (default: libx265)
- `FFMPEG_AUDIO_BITRATE` - Audio bitrate (default: 64k)
- `FFMPEG_CRF` - Constant Rate Factor for quality (default: 35)
- `FFMPEG_BITRATE` - Target video bitrate (default: 1000k)
- `FFMPEG_MAXRATE` - Maximum video bitrate (default: 5000k)
- `FFMPEG_BUFSIZE` - Buffer size (default: 2000k)
- `FFMPEG_THREADS` - Number of threads to use for encoding (default: 8)
- `FFMPEG_PRESET` - Encoding preset (default: medium)
- `FFMPEG_RESIZE` - Output resolution (default: 720p)

## Features

- Compress videos sent directly to the bot
- Support for compression via `/compress` command when replying to videos
- Maintains reasonable quality while reducing file size
- Supports MP4, AVI, MOV, and MKV formats
- Shows compression statistics (original size, compressed size, reduction percentage)
- Works in private chats and in groups

## Requirements

- Python 3.7+
- FFmpeg
- Telegram Bot Token

## Installation

1. Install FFmpeg:
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install ffmpeg

   # CentOS/RHEL
   sudo yum install epel-release
   sudo yum install ffmpeg ffmpeg-devel
   ```

2. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/telegram-video-compression-bot.git
   cd telegram-video-compression-bot
   ```

3. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Create a `.env` file with your configuration:
   ```env
   BOT_TOKEN=your_telegram_bot_token
   CONN_POOL_SIZE=8
   READ_TIMEOUT=200
   WRITE_TIMEOUT=200
   CONNECT_TIMEOUT=200
   POOL_TIMEOUT=200
   FFMPEG_CODEC=libx265
   FFMPEG_AUDIO_BITRATE=64k
   FFMPEG_CRF=35
   FFMPEG_BITRATE=1000k
   FFMPEG_MAXRATE=5000k
   FFMPEG_BUFSIZE=2000k
   FFMPEG_THREADS=8
   FFMPEG_PRESET=medium
   FFMPEG_RESIZE=720p
   ```

## Usage

1. Start the bot:
   ```bash
   python minimax.py
   ```