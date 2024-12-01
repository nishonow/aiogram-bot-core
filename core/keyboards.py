from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

start = ReplyKeyboardMarkup(resize_keyboard=True)
start.add(KeyboardButton(text="🎲 Random Fact"))