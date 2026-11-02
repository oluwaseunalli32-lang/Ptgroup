import os
import logging
import requests
from io import BytesIO

import qrcode
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# A simple in-memory dictionary to store links per user
# Format: { chat_id: { "nickname": "url" } }
user_links = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the welcome message."""
    welcome_text = (
        "Welcome to PT Group!\n\n"
        "Your simple link management assistant.\n\n"
        "🔗 Generate shareable links\n"
        "✅ Check whether links are working\n"
        "📁 Save and organize your links\n"
        "📱 Generate QR codes instantly\n\n"
        "Everything you need to manage your links in one place.\n\n"
        "Start using PT Group today!\n\n"
        "Commands:\n"
        "/qr <url> - Generate a QR code\n"
        "/check <url> - Check if a link works\n"
        "/save <name> <url> - Save a link\n"
        "/list - View your saved links"
    )
    await update.message.reply_text(welcome_text)

async def generate_qr(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generates a QR code for a URL."""
    if not context.args:
        await update.message.reply_text("Usage: /qr <URL>")
        return

    url = context.args[0]
    if not url.startswith("http"):
        url = "https://" + url

    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    bio = BytesIO()
    bio.name = "qr.png"
    img.save(bio, "PNG")
    bio.seek(0)

    await update.message.reply_photo(photo=bio, caption=f"QR Code for: {url}")

async def check_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Checks if a URL is working."""
    if not context.args:
        await update.message.reply_text("Usage: /check <URL>")
        return

    url = context.args[0]
    if not url.startswith("http"):
        url = "https://" + url

    msg = await update.message.reply_text(f"Checking {url}...")
    
    try:
        # Send a HEAD request to check status without downloading the whole page
        response = requests.head(url, timeout=10, allow_redirects=True)
        if response.status_code == 200:
            await msg.edit_text(f"✅ The link is working!\nStatus Code: {response.status_code}")
        else:
            await msg.edit_text(f"⚠️ The link responded, but with an error.\nStatus Code: {response.status_code}")
    except requests.RequestException as e:
        await msg.edit_text(f"❌ The link seems to be broken or unreachable.\nError: {str(e)}")

async def save_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Saves a link with a nickname."""
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /save <name> <URL>")
        return

    name = context.args[0]
    url = context.args[1]
    if not url.startswith("http"):
        url = "https://" + url

    chat_id = update.effective_chat.id
    if chat_id not in user_links:
        user_links[chat_id] = {}

    user_links[chat_id][name] = url
    await update.message.reply_text(f"📁 Saved! '{name}' is now linked to {url}")

async def list_links(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Lists all saved links."""
    chat_id = update.effective_chat.id
    links = user_links.get(chat_id, {})

    if not links:
        await update.message.reply_text("You don't have any saved links yet. Use /save to add one.")
        return

    response = "📁 Your Saved Links:\n\n"
    for name, url in links.items():
        response += f"🔗 {name}: {url}\n"

    await update.message.reply_text(response)

def main() -> None:
    """Start the bot."""
    TOKEN = os.environ.get("BOT_TOKEN")
    if not TOKEN:
        raise ValueError("No BOT_TOKEN environment variable set.")

    application = Application.builder().token(TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("qr", generate_qr))
    application.add_handler(CommandHandler("check", check_link))
    application.add_handler(CommandHandler("save", save_link))
    application.add_handler(CommandHandler("list", list_links))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
