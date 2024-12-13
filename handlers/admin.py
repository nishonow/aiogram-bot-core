from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery
from config import ADMINS
from loader import dp, bot
from app import BOT_START_TIME
from core.db import count_users, get_user_ids, count_new_users_last_24_hours, clear_db, get_admins, add_admin, \
    remove_admin, count_admins
from core.keyboards import adminKey, adminConfirm, backToSettings, settingsKey, statsKey, adminBack, adminConfirmDB, \
    adminCancelKey
import asyncio
import time


# MESSAGE HANDLERS ==================================================


@dp.message_handler(commands=["admin"])
async def count_command(message: Message):
    if message.from_user.id in get_admins():
        await message.answer(f"Choose what are you going to do?", reply_markup=adminKey)
    elif message.from_user.id in ADMINS:
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

@dp.message_handler(state='add_admin')
async def add_new_admin(message: Message, state: FSMContext):
    data = await state.get_data()
    message_id = data.get('msgID')
    try:
        new_admin = int(message.text)
        if new_admin in [admin_id for admin_id in get_admins()]:  # Check from the database
            await message.answer("⚠️ This user is already an admin.", reply_markup=backToSettings)
            await bot.delete_message(chat_id=message.chat.id, message_id=message_id)
        else:
            add_admin(new_admin)
            await message.answer(f"✅ User {new_admin} has been added as an admin.", reply_markup=settingsKey)
            await bot.delete_message(chat_id=message.chat.id, message_id=message_id)
    except ValueError:
        await message.answer("❌ Invalid Telegram ID. Please send a valid numeric ID.", reply_markup=backToSettings)
        await bot.delete_message(chat_id=message.chat.id, message_id=message_id)
    finally:
        await state.finish()

@dp.message_handler(state='remove_admin')
async def remove_old_admin(message: Message, state: FSMContext):
    data = await state.get_data()
    message_id = data.get('msgID')
    try:
        admin_to_remove = int(message.text)
        if admin_to_remove in [admin_id for admin_id in get_admins()]:  # Check from the database
            remove_admin(admin_to_remove)  # Remove from the database
            await message.answer(f"✅ User {admin_to_remove} has been removed as an admin.", reply_markup=settingsKey)
            await bot.delete_message(chat_id=message.chat.id, message_id=message_id)
        else:
            await message.answer("⚠️ This user is not an admin.", reply_markup=backToSettings)
            await bot.delete_message(chat_id=message.chat.id, message_id=message_id)
    except ValueError:
        await message.answer("❌ Invalid Telegram ID. Please send a valid numeric ID.", reply_markup=backToSettings)
        await bot.delete_message(chat_id=message.chat.id, message_id=message_id)
    finally:
        await state.finish()


# CALLBACK DATA HANDLERS ============================================


@dp.callback_query_handler(text='stats')
async def stats(call: CallbackQuery):
    total_users = count_users()
    new_users = count_new_users_last_24_hours()  # Count new users in the last 24 hours
    uptime_seconds = int(time.time() - BOT_START_TIME)
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime = f"{hours}h {minutes}m {seconds}s"
    total_admins = count_admins()
    await call.message.edit_text(
        f"📊 All users: {total_users}\n"
        f"👥 Admins: {total_admins}\n"
        f"🆕 New users (last 24h): {new_users}\n"
        f"🕒 Bot Uptime: {uptime}",
        reply_markup=statsKey
    )


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
    success = 0
    error = 0
    for id in get_user_ids():
        try:
            await bot.copy_message(chat_id=id, from_chat_id=call.message.chat.id, message_id=msgID)
            success += 1
        except Exception as e:
            error += 1
            pass
        await asyncio.sleep(0.04) # 25 messages per second (30 is limit)
    await call.message.answer(f"🆗 Message sent\nReceived: {success}\nBlocked: {error}", reply_markup=adminBack)
    await state.finish()

@dp.callback_query_handler(text='decline', state='getAction')
async def broadcast_decline(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.delete()
    await call.message.answer(f"Choose what are you going to do?", reply_markup=adminKey)


@dp.callback_query_handler(text='clear_db')
async def ask_clear_db(call: CallbackQuery):
    if call.from_user.id in get_admins() or call.from_user.id in ADMINS:
        await call.message.edit_text(
            "⚠️ Are you sure you want to clear the database? This action cannot be undone.",
            reply_markup=adminConfirmDB
        )
    else:
        pass

@dp.callback_query_handler(text='confirm_clear_db')
async def confirm_clear_db(call: CallbackQuery):
    if call.from_user.id in get_admins() or call.from_user.id in ADMINS:
        clear_db()
        await call.message.edit_text("🗑 Database has been cleared.", reply_markup=adminBack)
    else:
        pass

@dp.callback_query_handler(text='cancel_clear_db')
async def cancel_clear_db(call: CallbackQuery):
    await call.message.edit_text("✅ Database clear action has been canceled.", reply_markup=adminBack)


@dp.callback_query_handler(text='settings')
async def open_settings(call: CallbackQuery):
    await call.message.edit_text(
        "⚙️ Settings Menu:",
        reply_markup=settingsKey
    )

@dp.callback_query_handler(text='add_admin')
async def add_admin_prompt(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        "📝 Send the Telegram ID of the user you want to add as an admin.\n\nPress Cancel to go back.",
        reply_markup=adminCancelKey
    )
    await state.update_data(msgID=call.message.message_id)
    await state.set_state('add_admin')


@dp.callback_query_handler(text='remove_admin')
async def remove_admin_prompt(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        "📝 Send the Telegram ID of the admin you want to remove.\n\nPress Cancel to go back.",
        reply_markup=adminCancelKey
    )
    await state.update_data(msgID=call.message.message_id)
    await state.set_state('remove_admin')

@dp.callback_query_handler(text='cancel_add_admin', state='*')
async def cancel_remove_admin(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.edit_text(
        "⚙️ Settings Menu:",
        reply_markup=settingsKey
    )
