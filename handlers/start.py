import random
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from core.db import add_user, user_exists
from core.keyboards import start
from core.utils import FUN_FACTS
from loader import dp, bot


@dp.message_handler(CommandStart())
async def start_command(message: types.Message):
    user_id = message.from_user.id
    name = message.from_user.full_name
    username = message.from_user.username

    # Check if the user exists and add if necessary
    if not user_exists(user_id):
        add_user(user_id, name, username)

    await message.answer(
        "Welcome to the bot! You are now registered.", reply_markup=start
    )



@dp.message_handler(text="🎲 Random Fact")
async def random_fact_handler(message: types.Message):
    # Pick a random fact
    fact = random.choice(FUN_FACTS)
    # Send the fact as a reply
    await message.answer(f"🧐 Did you know?\n\n{fact}")