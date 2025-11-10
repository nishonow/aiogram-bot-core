import random
from aiogram import types, Router, F
from aiogram.filters import CommandStart
from config import ADMINS
from aiogram import Bot
from core.db import add_user, user_exists, get_admins
from core.keyboards import start_keyboard
from utils.helpers import FUN_FACTS, check_channel_membership, send_channel_join_button

router = Router()

@router.message(CommandStart())
async def start_command(message: types.Message, bot: Bot):
    user_id = message.from_user.id
    name = message.from_user.full_name
    username = message.from_user.username

    if not await user_exists(user_id):
        await add_user(user_id, name, username)

    if not await check_channel_membership(bot, user_id):
        await send_channel_join_button(message, bot)
        return

    await message.answer("Welcome to the bot! Press the button below.", reply_markup=start_keyboard())


@router.message(F.text == "🎲 Random Fact")
async def random_fact_handler(message: types.Message, bot: Bot):
    if not await check_channel_membership(bot, message.from_user.id):
        await send_channel_join_button(message, bot)
        return

    fact = random.choice(FUN_FACTS)
    await message.answer(f"🧐 Did you know?\n\n{fact}")
