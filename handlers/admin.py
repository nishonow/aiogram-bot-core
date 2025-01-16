# ===================================================================
# IMPORTS ============================================================
# ===================================================================

from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery
from config import ADMINS
from loader import dp, bot
from app import BOT_START_TIME
from core.db import count_users, get_user_ids, count_new_users_last_24_hours, clear_db, get_admins, add_admin, \
    remove_admin, count_admins, get_admin_details, get_channel_ids, remove_channel, add_channel
from core.keyboards import adminKey, ConfirmBroadcast, backToSettings, settingsKey, statsKey, adminBack, adminConfirmDB, \
    adminCancelKey, dbBack
import asyncio
import time


# ===================================================================
# MESSAGE HANDLERS ===================================================
# ===================================================================

# Handle the /admin command for Admins
@dp.message_handler(commands=["admin"])
async def count_command(message: Message):
    if message.from_user.id in get_admins():
        await message.answer(f"Choose what are you going to do?", reply_markup=adminKey)
    elif message.from_user.id in ADMINS:
        await message.answer(f"Choose what are you going to do?", reply_markup=adminKey)
    else:
        pass  # Do nothing if the user is not in ADMINS


# ===================================================================
# BROADCAST SECTION =================================================
# ===================================================================

# Broadcast Command - Prompt the admin to send a message
@dp.callback_query_handler(text='broadcast')
async def broadcast(call: CallbackQuery, state: FSMContext):
    msg = await call.message.edit_text("✍️ Send your message: ", reply_markup=adminBack)
    await state.set_state('getMessage')
    await state.update_data(id=msg.message_id)

# Handle getting a message to broadcast
@dp.message_handler(content_types='any', state='getMessage')
async def get_message(message: Message, state: FSMContext):
    messageID = message.message_id
    await state.update_data(msgID=messageID)
    data = await state.get_data()
    id = data.get('id')
    await bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=id)
    await bot.copy_message(message.from_user.id, message.from_user.id, messageID)
    await message.answer("👆 Press confirm if message above is correct.", reply_markup=ConfirmBroadcast)
    await state.set_state('getAction')

# Handle broadcast confirmation
@dp.callback_query_handler(text='confirm', state='getAction')
async def broadcast_confirm(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    msgID = data.get('msgID')
    await call.message.edit_reply_markup()
    success = 0
    error = 0
    for id in get_user_ids():
        try:
            await bot.copy_message(chat_id=id, from_chat_id=call.message.chat.id, message_id=msgID)
            success += 1
        except Exception as e:
            error += 1
            pass
        await asyncio.sleep(0.04)  # 25 messages per second (30 is limit)
    await call.message.answer(f"🆗 Message sent\nReceived: {success}\nBlocked: {error}", reply_markup=adminBack)
    await state.finish()

# Handle broadcast decline
@dp.callback_query_handler(text='decline', state='getAction')
async def broadcast_decline(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.delete()
    await call.message.answer(f"Choose what are you going to do?", reply_markup=adminKey)


# ===================================================================
# ADMIN MANAGEMENT ===================================================
# ===================================================================

# Add new admin
@dp.callback_query_handler(text='add_admin')
async def add_admin_prompt(call: CallbackQuery, state: FSMContext):
    admins_details = get_admin_details()
    admins_text = ""
    for admin in admins_details:
        admin_id = admin[0]
        admin_name = admin[1] if admin[1] else "Name not found"
        # Create a clickable link for each admin's Telegram ID
        admin_link = f"[{admin_id}](tg://user?id={admin_id})"
        admins_text += f"{admin_link} | {admin_name}\n"

    all_admins_ids = get_admins()
    missing_admins = set(all_admins_ids) - {admin[0] for admin in admins_details}
    for missing_admin in missing_admins:
        admins_text += f"{missing_admin} | None\n"
    await call.message.edit_text(
        f"📝 Send the Telegram ID of the user you want to add as an admin.\n\nAdmins:\n{admins_text}",
        reply_markup=adminCancelKey,
        parse_mode='Markdown'
    )
    await state.update_data(msgID=call.message.message_id)
    await state.set_state('add_admin')

# Handle adding an admin
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
            await message.answer(f"✅ User {new_admin} has been added as an admin.", reply_markup=backToSettings)
            await bot.delete_message(chat_id=message.chat.id, message_id=message_id)
    except ValueError:
        await message.answer("❌ Invalid Telegram ID. Please send a valid numeric ID.", reply_markup=backToSettings)
        await bot.delete_message(chat_id=message.chat.id, message_id=message_id)
    finally:
        await state.finish()

# Remove an admin
@dp.callback_query_handler(text='remove_admin')
async def remove_admin_prompt(call: CallbackQuery, state: FSMContext):
    admins_details = get_admin_details()
    admins_text = ""
    for admin in admins_details:
        admin_id = admin[0]
        admin_name = admin[1] if admin[1] else "Name not found"
        # Create a clickable link for each admin's Telegram ID
        admin_link = f"[{admin_id}](tg://user?id={admin_id})"
        admins_text += f"{admin_link} | {admin_name}\n"

    all_admins_ids = get_admins()
    missing_admins = set(all_admins_ids) - {admin[0] for admin in admins_details}
    for missing_admin in missing_admins:
        admins_text += f"{missing_admin} | None\n"
    await call.message.edit_text(
        f"📝 Send the Telegram ID of the admin you want to remove.\n\nAdmins:\n{admins_text}",
        reply_markup=adminCancelKey,
        parse_mode="Markdown"
    )
    await state.update_data(msgID=call.message.message_id)
    await state.set_state('remove_admin')

# Handle removing an admin
@dp.message_handler(state='remove_admin')
async def remove_old_admin(message: Message, state: FSMContext):
    data = await state.get_data()
    message_id = data.get('msgID')
    try:
        admin_to_remove = int(message.text)
        if admin_to_remove in [admin_id for admin_id in get_admins()]:  # Check from the database
            remove_admin(admin_to_remove)  # Remove from the database
            await message.answer(f"✅ User {admin_to_remove} has been removed as an admin.", reply_markup=backToSettings)
            await bot.delete_message(chat_id=message.chat.id, message_id=message_id)
        else:
            await message.answer("⚠️ This user is not an admin.", reply_markup=backToSettings)
            await bot.delete_message(chat_id=message.chat.id, message_id=message_id)
    except ValueError:
        await message.answer("❌ Invalid Telegram ID. Please send a valid numeric ID.", reply_markup=backToSettings)
        await bot.delete_message(chat_id=message.chat.id, message_id=message_id)
    finally:
        await state.finish()

# Cancel adding/removing admin
@dp.callback_query_handler(text='cancel_add_admin', state='*')
async def cancel_add_remove_admin(call: CallbackQuery, state: FSMContext):
    await state.finish()
    admins_details = get_admin_details()
    admins_text = ""
    for admin in admins_details:
        admin_id = admin[0]
        admin_name = admin[1] if admin[1] else "Name not found"
        # Create a clickable link for each admin's Telegram ID
        admin_link = f"[{admin_id}](tg://user?id={admin_id})"
        admins_text += f"{admin_link} | {admin_name}\n"

    all_admins_ids = get_admins()
    missing_admins = set(all_admins_ids) - {admin[0] for admin in admins_details}
    for missing_admin in missing_admins:
        admins_text += f"{missing_admin} | None\n"

    settings_message = f"⚙️ Settings Menu:\n\nAdmins:\n{admins_text}"

    await call.message.edit_text(
        settings_message,
        reply_markup=settingsKey,
        parse_mode="Markdown"
    )


# ===================================================================
# STATS ==============================================================
# ===================================================================

# Show bot stats
@dp.callback_query_handler(text='stats')
async def stats(call: CallbackQuery):
    total_users = count_users()
    new_users = count_new_users_last_24_hours()  # Count new users in the last 24 hours
    uptime_seconds = int(time.time() - BOT_START_TIME)
    days, remainder = divmod(uptime_seconds, 86400)  # 86400 seconds in a day
    hours, remainder = divmod(remainder, 3600)      # 3600 seconds in an hour
    minutes, seconds = divmod(remainder, 60)       # 60 seconds in a minute
    uptime = f"{days}d {hours}h {minutes}m {seconds}s"
    total_admins = count_admins()
    await call.message.edit_text(
        f"📊 All users: {total_users}\n"
        f"👥 Admins: {total_admins}\n"
        f"🆕 New users (last 24h): {new_users}\n"
        f"🕒 Bot Uptime: {uptime}",
        reply_markup=statsKey
    )


@dp.callback_query_handler(text='update')
async def stat_update(call: CallbackQuery):
    total_users = count_users()
    new_users = count_new_users_last_24_hours()  # Count new users in the last 24 hours
    uptime_seconds = int(time.time() - BOT_START_TIME)
    days, remainder = divmod(uptime_seconds, 86400)  # 86400 seconds in a day
    hours, remainder = divmod(remainder, 3600)      # 3600 seconds in an hour
    minutes, seconds = divmod(remainder, 60)       # 60 seconds in a minute
    uptime = f"{days}d {hours}h {minutes}m {seconds}s"
    total_admins = count_admins()
    await bot.answer_callback_query(call.id, "🔄 Everything's updated and ready!", show_alert=True)
    await call.message.edit_text(
        f"📊 All users: {total_users}\n"
        f"👥 Admins: {total_admins}\n"
        f"🆕 New users (last 24h): {new_users}\n"
        f"🕒 Bot Uptime: {uptime}",
        reply_markup=statsKey
    )




# ===================================================================
# DATABASE CLEARING ==================================================
# ===================================================================

# Ask to clear the database
@dp.callback_query_handler(text='clear_db')
async def ask_clear_db(call: CallbackQuery):
    if call.from_user.id in get_admins() or call.from_user.id in ADMINS:
        await call.message.edit_text(
            "⚠️ Are you sure you want to clear the database? This action cannot be undone.",
            reply_markup=adminConfirmDB
        )
    else:
        pass

# Confirm clearing the database
@dp.callback_query_handler(text='confirm_clear_db')
async def confirm_clear_db(call: CallbackQuery):
    if call.from_user.id in get_admins() or call.from_user.id in ADMINS:
        clear_db()
        await call.message.edit_text("🗑 Database has been cleared.", reply_markup=dbBack) # cancel admin
    else:
        pass

# Cancel clearing the database
@dp.callback_query_handler(text='cancel_clear_db')
async def cancel_clear_db(call: CallbackQuery):
    admins_details = get_admin_details()
    admins_text = ""
    for admin in admins_details:
        admin_id = admin[0]
        admin_name = admin[1] if admin[1] else "Name not found"
        # Create a clickable link for each admin's Telegram ID
        admin_link = f"[{admin_id}](tg://user?id={admin_id})"
        admins_text += f"{admin_link} | {admin_name}\n"

    all_admins_ids = get_admins()
    missing_admins = set(all_admins_ids) - {admin[0] for admin in admins_details}
    for missing_admin in missing_admins:
        admins_text += f"{missing_admin} | None\n"

    settings_message = f"⚙️ Settings Menu:\n\nAdmins:\n{admins_text}"

    await call.message.edit_text(
        settings_message,
        reply_markup=settingsKey,
        parse_mode="Markdown"
    )


# ===================================================================
# ADD CHANNEL FUNCTIONALITY ========================================
# ===================================================================
async def get_channel_username(channel_id):
    # Use Bot API to get chat information
    chat = await bot.get_chat(channel_id)
    return chat.username  # This is the channel's username

# Add new channel
@dp.callback_query_handler(text='add_channel')
async def add_channel_prompt(call: CallbackQuery, state: FSMContext):
    channels = get_channel_ids()  # Fetch existing channels from DB
    channels_text = ""
    for channel in channels:
        channel_username = await get_channel_username(channel)
        channels_text += f"@{channel_username} {channel}\n"

    # Display the list of current channels and ask for a new channel
    await call.message.edit_text(
        f"📝 Send the Telegram channel ID you want to add.\n\nExisting channels:\n{channels_text}",
        reply_markup=adminCancelKey,
        parse_mode='Markdown'
    )
    await state.update_data(msgID=call.message.message_id)
    await state.set_state('add_channel')


# Handle adding a channel
@dp.message_handler(state='add_channel')
async def add_new_channel(message: Message, state: FSMContext):
    data = await state.get_data()
    message_id = data.get('msgID')
    new_channel = message.text.strip()

    # Check if the channel already exists in the DB
    if new_channel in get_channel_ids():
        await message.answer("⚠️ This channel is already added.", reply_markup=backToSettings)
        await bot.delete_message(chat_id=message.chat.id, message_id=message_id)
    else:
        # Add the new channel to the database
        add_channel(new_channel)
        channel = await get_channel_username(new_channel)
        await message.answer(f"✅ Channel @{channel} has been added.", reply_markup=backToSettings)
        await bot.delete_message(chat_id=message.chat.id, message_id=message_id)

    await state.finish()


# Remove an existing channel
@dp.callback_query_handler(text='remove_channel')
async def remove_channel_prompt(call: CallbackQuery, state: FSMContext):
    channels = get_channel_ids()  # Fetch existing channels from DB
    channels_text = ""
    for channel in channels:
        channel_username = await get_channel_username(channel)
        channels_text += f"@{channel_username} {channel}\n"

    # Display the list of current channels and ask for a channel to remove
    await call.message.edit_text(
        f"📝 Send the channel ID you want to remove.\n\nExisting channels:\n{channels_text}",
        reply_markup=adminCancelKey,
        parse_mode='Markdown'
    )
    await state.update_data(msgID=call.message.message_id)
    await state.set_state('remove_channel')


# Handle removing a channel
@dp.message_handler(state='remove_channel')
async def remove_existing_channel(message: Message, state: FSMContext):
    data = await state.get_data()
    message_id = data.get('msgID')
    channel_to_remove = message.text.strip()

    # Check if the channel exists in the DB
    if channel_to_remove in get_channel_ids():
        remove_channel(channel_to_remove)  # Remove from DB
        channel = await get_channel_username(channel_to_remove)
        await message.answer(f"✅ Channel @{channel} has been removed.", reply_markup=backToSettings)
        await bot.delete_message(chat_id=message.chat.id, message_id=message_id)
    else:
        await message.answer("⚠️ This channel does not exist.", reply_markup=backToSettings)
        await bot.delete_message(chat_id=message.chat.id, message_id=message_id)

    await state.finish()


# ===================================================================
# SETTINGS ===========================================================
# ===================================================================

# Open settings menu
@dp.callback_query_handler(text='settings')
async def open_settings(call: CallbackQuery):
    admins_details = get_admin_details()
    admins_text = ""
    for admin in admins_details:
        admin_id = admin[0]
        admin_name = admin[1] if admin[1] else "Name not found"
        # Create a clickable link for each admin's Telegram ID
        admin_link = f"[{admin_id}](tg://user?id={admin_id})"
        admins_text += f"{admin_link} | {admin_name}\n"

    all_admins_ids = get_admins()
    missing_admins = set(all_admins_ids) - {admin[0] for admin in admins_details}
    for missing_admin in missing_admins:
        admins_text += f"{missing_admin} | None\n"

    settings_message = f"⚙️ Settings Menu:\n\nAdmins:\n{admins_text}"

    await call.message.edit_text(
        settings_message,
        reply_markup=settingsKey,
        parse_mode="Markdown"
    )


# Go back to settings
@dp.callback_query_handler(text='goback', state='*')
async def goback(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(f"Choose what are you going to do?", reply_markup=adminKey)
    await state.finish()

