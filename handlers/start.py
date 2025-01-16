import random
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from core.db import add_user, user_exists, get_channel_ids
from core.keyboards import start
from core.utils import FUN_FACTS, check_channel_membership
from loader import dp, bot


async def get_channel_username(channel_id):
    chat = await bot.get_chat(channel_id)
    return chat.username


async def send_channel_join_button(user_id):
    channel_ids = get_channel_ids()

    if not channel_ids:
        return True

    if not await check_channel_membership(user_id):
        for channel_id in channel_ids:
            channel_username = await get_channel_username(channel_id)
            button = InlineKeyboardButton(
                text="Join Channel",
                url=f"https://t.me/{channel_username}"
            )
            markup = InlineKeyboardMarkup().add(button)
            await bot.send_message(user_id, "Please join the required channels to use the bot!", reply_markup=markup)
        return False

    return True


@dp.message_handler(CommandStart())
async def start_command(message: types.Message):
    user_id = message.from_user.id
    name = message.from_user.full_name
    username = message.from_user.username

    if not user_exists(user_id):
        add_user(user_id, name, username)

    if not await check_channel_membership(user_id):
        await send_channel_join_button(user_id)
        return

    await message.answer("Welcome to the bot! Press the button below.", reply_markup=start)


@dp.message_handler(text="🎲 Random Fact")
async def random_fact_handler(message: types.Message):
    user_id = message.from_user.id

    if not await check_channel_membership(user_id):
        await send_channel_join_button(user_id)
        return

    fact = random.choice(FUN_FACTS)
    await message.answer(f"🧐 Did you know?\n\n{fact}")


@dp.message_handler()
async def fact_add(message: types.Message):
    user_id = message.from_user.id

    if not await check_channel_membership(user_id):
        await send_channel_join_button(user_id)
        return

    text = message.text
    FUN_FACTS.append(text)
    await message.reply("Fact added successfully!")
