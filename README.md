# Telegram Video Compression Bot

A Telegram bot that compresses video files while maintaining good quality. The bot uses FFmpeg for video compression and supports multiple video formats.

## Features

- Compress videos sent directly to the bot
- Support for compression via `/compress` command when replying to videos
- Maintains reasonable quality while reducing file size
- Supports MP4, AVI, MOV, and MKV formats
- Shows compression statistics (original size, compressed size, reduction percentage)
- Works in private chats only

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
   READ_TIMEOUT=20
   WRITE_TIMEOUT=20
   CONNECT_TIMEOUT=20
   POOL_TIMEOUT=20
   FFMPEG_BITRATE=1000k
   FFMPEG_AUDIO_BITRATE=128k
   FFMPEG_CRF=28
   FFMPEG_MAXRATE=1500k
   FFMPEG_BUFSIZE=2000k
   FFMPEG_THREADS=0
   ```

## Usage

1. Start the bot:
   ```bash
   python minimax.py
   ```

2. In Telegram:
   - Send a video directly to the bot
   - Or reply to a video with `/compress` command
   - Wait for the compressed version

## Commands

- `/start` - Start the bot and get welcome message
- `/help` - Show help message with supported formats
- `/compress` - Compress a video (when used as a reply to a video message)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 