import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest
import ffmpeg
from pathlib import Path
import httpx
import dotenv


dotenv.load_dotenv()


# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Replace with your bot token
TOKEN = os.getenv("BOT_TOKEN")

# Custom request handler with increased timeout
class CustomRequest(HTTPXRequest):
    def __init__(self):
        super().__init__(
            connection_pool_size=int(os.getenv("CONN_POOL_SIZE", 8)),
            read_timeout=float(os.getenv("READ_TIMEOUT", 20)),
            write_timeout=float(os.getenv("WRITE_TIMEOUT", 20)),
            connect_timeout=float(os.getenv("CONNECT_TIMEOUT", 20)),
            pool_timeout=float(os.getenv("POOL_TIMEOUT", 20)),
        )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        "👋 Hi! I'm a video compression bot.\n"
        "Send me any video file and I'll compress it while maintaining good quality."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        "Just send me a video file and I'll compress it for you!\n"
        "Supported formats: MP4, AVI, MOV, MKV"
    )

async def compress_video(input_path: str, output_path: str):
    """Compress the video using ffmpeg with more aggressive compression settings."""
    try:
        # FFmpeg compression settings for better size reduction
        stream = ffmpeg.input(input_path)
        stream = ffmpeg.output(stream, output_path,
            vcodec='libx264',        # Video codec
            acodec='aac',            # Audio codec
            video_bitrate=str(os.getenv("FFMPEG_BITRATE", "1000k")),    # Reduced video bitrate
            audio_bitrate=str(os.getenv("FFMPEG_AUDIO_BITRATE", "128k")),     # Reduced audio bitrate
            preset='slower',         # Slower preset for better compression
            crf=int(os.getenv("FFMPEG_CRF", 28)),                  # Increased CRF (23-28 range, higher = more compression)
            movflags='+faststart',   # Enable fast start for web playback
            # Additional compression parameters
            maxrate=str(os.getenv("FFMPEG_MAXRATE", "1500k")),         # Maximum bitrate cap
            bufsize=str(os.getenv("FFMPEG_BUFSIZE", "2000k")),         # Buffer size
            threads=int(os.getenv("FFMPEG_THREADS", 0))                # Use all available CPU threads
        )
        
        ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)
        return True
    except ffmpeg.Error as e:
        logger.error(f"FFmpeg error: {e.stderr.decode()}")
        return False

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle video messages."""
    try:
        # Send initial status message
        status_message = await update.message.reply_text("📥 Downloading video...")
        
        # Get video file from telegram with increased chunk size
        video = await context.bot.get_file(update.message.video.file_id)
        
        # Create directories if they don't exist
        input_path = Path("downloads")
        output_path = Path("compressed")
        input_path.mkdir(exist_ok=True)
        output_path.mkdir(exist_ok=True)
        
        # Generate file paths
        input_file = input_path / f"input_{update.message.video.file_id}.mp4"
        output_file = output_path / f"compressed_{update.message.video.file_id}.mp4"
        
        # Download video in chunks
        async with httpx.AsyncClient(timeout=30.0) as client:
            async with client.stream('GET', video.file_path) as response:
                with open(input_file, 'wb') as f:
                    async for chunk in response.aiter_bytes(chunk_size=8192):
                        f.write(chunk)
        
        # Get original file size
        original_size = os.path.getsize(input_file)
        original_size_mb = original_size / (1024 * 1024)  # Convert to MB
        
        await status_message.edit_text("⚙️ Compressing video... This may take a while.")
        
        # Compress video
        success = await compress_video(str(input_file), str(output_file))
        
        if not success:
            await status_message.edit_text("❌ Sorry, there was an error compressing your video.")
            return
        
        # Get compressed file size
        compressed_size = os.path.getsize(output_file)
        compressed_size_mb = compressed_size / (1024 * 1024)  # Convert to MB
        
        # Calculate compression percentage
        compression_percent = ((original_size - compressed_size) / original_size) * 100
        
        # Upload compressed video
        await status_message.edit_text("📤 Uploading compressed video...")
        
        # Upload in chunks with progress updates
        try:
            with open(output_file, 'rb') as video_file:
                await update.message.reply_video(
                    video=video_file,
                    caption=f"🎥 Here's your compressed video!\n\n"
                            f"Original size: {original_size_mb:.2f} MB\n"
                            f"Compressed size: {compressed_size_mb:.2f} MB\n"
                            f"Reduced by: {compression_percent:.1f}%",
                    read_timeout=30,
                    write_timeout=30,
                    connect_timeout=30,
                    pool_timeout=30
                )
        except Exception as upload_error:
            logger.error(f"Upload error: {str(upload_error)}")
            await status_message.edit_text("❌ Upload timed out. The file might be too large for Telegram.")
            return
        
        # # Clean up files
        input_file.unlink(missing_ok=True)
        output_file.unlink(missing_ok=True)
        
        await status_message.edit_text("✅ Video compression complete!")
        
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        await update.message.reply_text("❌ Sorry, something went wrong while processing your video.")

async def compress_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /compress command when replying to a video."""
    try:
        # Check if the command is a reply to a message
        if not update.message.reply_to_message:
            await update.message.reply_text(
                "❌ Please reply to a video message with /compress"
            )
            return
        
        # Check if the replied message contains a video
        replied_msg = update.message.reply_to_message
        if not replied_msg.video:
            await update.message.reply_text(
                "❌ The replied message is not a video!"
            )
            return
            
        # Send initial status message
        status_message = await update.message.reply_text("📥 Downloading video...")
        
        # Get video file from telegram with increased chunk size
        video = await context.bot.get_file(replied_msg.video.file_id)
        
        # Create directories if they don't exist
        input_path = Path("downloads")
        output_path = Path("compressed")
        input_path.mkdir(exist_ok=True)
        output_path.mkdir(exist_ok=True)
        
        # Generate file paths
        input_file = input_path / f"input_{replied_msg.video.file_id}.mp4"
        output_file = output_path / f"compressed_{replied_msg.video.file_id}.mp4"
        
        # Download video in chunks
        async with httpx.AsyncClient(timeout=30.0) as client:
            async with client.stream('GET', video.file_path) as response:
                with open(input_file, 'wb') as f:
                    async for chunk in response.aiter_bytes(chunk_size=8192):
                        f.write(chunk)
        
        # Get original file size
        original_size = os.path.getsize(input_file)
        original_size_mb = original_size / (1024 * 1024)  # Convert to MB
        
        await status_message.edit_text("⚙️ Compressing video... This may take a while.")
        
        # Compress video
        success = await compress_video(str(input_file), str(output_file))
        
        if not success:
            await status_message.edit_text("❌ Sorry, there was an error compressing your video.")
            return
        
        # Get compressed file size
        compressed_size = os.path.getsize(output_file)
        compressed_size_mb = compressed_size / (1024 * 1024)  # Convert to MB
        
        # Calculate compression percentage
        compression_percent = ((original_size - compressed_size) / original_size) * 100
        
        # Upload compressed video
        await status_message.edit_text("📤 Uploading compressed video...")
        
        # Upload in chunks with progress updates
        try:
            with open(output_file, 'rb') as video_file:
                await update.message.reply_video(
                    video=video_file,
                    caption=f"🎥 Here's your compressed video!\n\n"
                            f"Original size: {original_size_mb:.2f} MB\n"
                            f"Compressed size: {compressed_size_mb:.2f} MB\n"
                            f"Reduced by: {compression_percent:.1f}%",
                    read_timeout=30,
                    write_timeout=30,
                    connect_timeout=30,
                    pool_timeout=30
                )
        except Exception as upload_error:
            logger.error(f"Upload error: {str(upload_error)}")
            await status_message.edit_text("❌ Upload timed out. The file might be too large for Telegram.")
            return
        
        # # Clean up files
        input_file.unlink(missing_ok=True)
        output_file.unlink(missing_ok=True)
        
        await status_message.edit_text("✅ Video compression complete!")
        
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        await update.message.reply_text("❌ Sorry, something went wrong while processing your video.")

def main():
    """Start the bot."""
    # Create the Application with custom request handler
    application = (
        Application.builder()
        .token(TOKEN)
        .request(CustomRequest())     # Only set the custom request handler
        .build()
    )

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("compress", compress_command))  # Add compress command handler
    
    # Only handle direct videos in private chats, ignore videos in groups
    private_video_handler = MessageHandler(
        filters.VIDEO & filters.ChatType.PRIVATE,
        handle_video
    )
    application.add_handler(private_video_handler)

    # Run the bot with simplified settings
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
    )

if __name__ == '__main__':
    main()
