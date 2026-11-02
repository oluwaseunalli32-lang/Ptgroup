import os
import logging
from io import BytesIO

import qrcode
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Command Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the welcome message as defined in your prompt."""
    welcome_text = (
        "Welcome to PT Group!\n\n"
        "Your simple link management assistant.\n\n"
        "🔗 Generate shareable links\n"
        "✅ Check whether links are working\n"
        "📁 Save and organize your links\n"
        "📱 Generate QR codes instantly\n\n"
        "Everything you need to manage your links in one place.\n\n"
        "Start using PT Group today!"
    )
    await update.message.reply_text(welcome_text)

async def generate_qr(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generates a QR code for a URL provided after the command."""
    if not context.args:
        await update.message.reply_text("Usage: /qr <URL>")
        return

    url = context.args[0]
    # Create QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Save to a BytesIO object to send as a photo
    bio = BytesIO()
    bio.name = "qr.png"
    img.save(bio, "PNG")
    bio.seek(0)

    await update.message.reply_photo(photo=bio, caption=f"QR Code for: {url}")

# --- Placeholder for other features ---
# You would add handlers for /check, /save, /list, etc., following a similar pattern.

def main() -> None:
    """Start the bot."""
    # Get the token from an environment variable (best practice)
    TOKEN = os.environ.get("BOT_TOKEN")
    if not TOKEN:
        raise ValueError("No BOT_TOKEN environment variable set.")

    application = Application.builder().token(TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("qr", generate_qr))

    # Run the bot until the user presses Ctrl-C
    # For a Background Worker, this will run indefinitely
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
