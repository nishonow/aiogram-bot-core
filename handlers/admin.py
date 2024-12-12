from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from loader import dp, bot
from config import ADMINS
from core.db import count_users, get_user_ids

adminKey = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📊 Statistics", callback_data="stats")],
        [InlineKeyboardButton(text="📤 Broadcast", callback_data='broadcast')]
    ]
)

adminBack = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back", callback_data="goback")]
    ]
)

adminConfirm = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✅ Confirm", callback_data="confirm")],
        [InlineKeyboardButton(text="🚫 Decline", callback_data="decline")]
    ]
)

# MESSAGE HANDLERS ==================================================
@dp.message_handler(commands=["admin"])
async def count_command(message: Message):
    if message.from_user.id in ADMINS:
        await message.answer(f"Choose what are you going to do?", reply_markup=adminKey)
    else:
        pass  # Do nothing if the user is not in ADMINS

@dp.message_handler(content_types='any', state='getMessage')
async def get_message(message: Message, state: FSMContext):
    messageID = message.message_id
    await state.update_data(msgID=messageID)
    await bot.copy_message(message.from_user.id, message.from_user.id, messageID)
    await message.answer("👆 Press confirm if message above is correct.", reply_markup=adminConfirm)
    await state.set_state('getAction')


# CALLBACK DATA HANDLERS ============================================

@dp.callback_query_handler(text='stats')
async def stats(call: CallbackQuery):
    total_users = count_users()
    await call.message.edit_text(f"🗂 All users: {total_users}", reply_markup=adminBack)

@dp.callback_query_handler(text='goback', state='*')
async def goback(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(f"Choose what are you going to do?", reply_markup=adminKey)
    await state.finish()

@dp.callback_query_handler(text='broadcast')
async def broadcast(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("✍️ Send your message: ", reply_markup=adminBack)
    await state.set_state('getMessage')

@dp.callback_query_handler(text='confirm', state='getAction')
async def broadcast_confirm(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    msgID = data.get('msgID')
    await call.message.delete()
    for id in get_user_ids():
        await bot.copy_message(chat_id=id,
                               from_chat_id=call.message.chat.id,
                               message_id=msgID)
    await call.message.answer("🆗 Message sent", reply_markup=adminBack)
    await state.finish()

@dp.callback_query_handler(text='decline', state='getAction')
async def broadcast_decline(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.delete()
    await call.message.answer("❌ Declined", reply_markup=adminBack)