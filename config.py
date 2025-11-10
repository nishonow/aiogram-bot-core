from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMINS = [int(admin_id) for admin_id in os.getenv("ADMINS").split(',')]
