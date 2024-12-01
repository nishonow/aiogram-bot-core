from aiogram import types
from loader import dp
from config import ADMINS
from core.db import count_users


@dp.message_handler(commands=["count"])
async def count_command(message: types.Message):
    if message.from_user.id in ADMINS:
        total_users = count_users()
        await message.reply(f"📂 Total users: {total_users}")
    else:
        pass  # Do nothing if the user is not in ADMINS
