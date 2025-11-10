import asyncio
import time
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from config import ADMINS
from utils.consts import BOT_START_TIME
from core.db import count_users, get_user_ids, count_new_users_last_24_hours, clear_db, get_admins, add_admin, \
    remove_admin, count_admins, get_admin_details, get_channel_ids, remove_channel, add_channel
from core.keyboards import admin_keyboard, confirm_broadcast_keyboard, settings_keyboard, stats_keyboard, \
    admin_back_keyboard, db_back_keyboard, admin_confirm_db_keyboard, admin_cancel_keyboard, back_to_settings_keyboard
from utils.helpers import get_channel_username

router = Router()

class BroadcastState(StatesGroup):
    get_message = State()
    get_action = State()

class AdminManagementState(StatesGroup):
    add_admin = State()
    remove_admin = State()

class ChannelManagementState(StatesGroup):
    add_channel = State()
    remove_channel = State()

@router.message(Command("admin"))
async def admin_command(message: Message):
    if message.from_user.id in await get_admins() or message.from_user.id in ADMINS:
        await message.answer("Choose what you are going to do?", reply_markup=admin_keyboard())

@router.callback_query(F.data == 'broadcast')
async def broadcast_handler(call: CallbackQuery, state: FSMContext):
    msg = await call.message.edit_text("✍️ Send your message: ", reply_markup=admin_back_keyboard())
    await state.set_state(BroadcastState.get_message)
    await state.update_data(id=msg.message_id)
    await call.answer()

@router.message(BroadcastState.get_message)
async def get_message_handler(message: Message, state: FSMContext, bot: Bot):
    message_id = message.message_id
    await state.update_data(msgID=message_id)
    data = await state.get_data()
    msg_id = data.get('id')
    await bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=msg_id, reply_markup=None)
    await bot.copy_message(message.from_user.id, message.from_user.id, message_id)
    await message.answer("👆 Press confirm if message above is correct.", reply_markup=confirm_broadcast_keyboard())
    await state.set_state(BroadcastState.get_action)

@router.callback_query(F.data == 'confirm', BroadcastState.get_action)
async def broadcast_confirm_handler(call: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    msg_id = data.get('msgID')
    await call.message.edit_reply_markup()
    success = 0
    error = 0
    for user_id in await get_user_ids():
        try:
            await bot.copy_message(chat_id=user_id, from_chat_id=call.message.chat.id, message_id=msg_id)
            success += 1
        except Exception:
            error += 1
        await asyncio.sleep(0.04)
    await call.message.answer(f"🆗 Message sent\nReceived: {success}\nBlocked: {error}", reply_markup=admin_back_keyboard())
    await state.clear()
    await call.answer()

@router.callback_query(F.data == 'decline', BroadcastState.get_action)
async def broadcast_decline_handler(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.delete()
    await call.message.answer("Choose what are you going to do?", reply_markup=admin_keyboard())
    await call.answer()

@router.callback_query(F.data == 'add_admin')
async def add_admin_prompt(call: CallbackQuery, state: FSMContext):
    admins_details = await get_admin_details()
    admins_text = ""
    for admin in admins_details:
        admin_id, admin_name = admin
        admin_name = admin_name or "Name not found"
        admin_link = f"[{admin_id}](tg://user?id={admin_id})"
        admins_text += f"{admin_link} | {admin_name}\n"
    all_admins_ids = await get_admins()
    missing_admins = set(all_admins_ids) - {admin[0] for admin in admins_details}
    for missing_admin in missing_admins:
        admins_text += f"{missing_admin} | None\n"
    await call.message.edit_text(
        f"📝 Send the Telegram ID of the user you want to add as an admin.\n\nAdmins:\n{admins_text}",
        reply_markup=admin_cancel_keyboard(),
        parse_mode='Markdown'
    )
    await state.update_data(msgID=call.message.message_id)
    await state.set_state(AdminManagementState.add_admin)
    await call.answer()

@router.message(AdminManagementState.add_admin)
async def add_new_admin_handler(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    message_id = data.get('msgID')
    try:
        new_admin = int(message.text)
        if new_admin in await get_admins():
            await message.answer("⚠️ This user is already an admin.", reply_markup=back_to_settings_keyboard())
        else:
            await add_admin(new_admin)
            await message.answer(f"✅ User {new_admin} has been added as an admin.", reply_markup=back_to_settings_keyboard())
        await bot.delete_message(chat_id=message.chat.id, message_id=message_id)
    except ValueError:
        await message.answer("❌ Invalid Telegram ID. Please send a valid numeric ID.", reply_markup=back_to_settings_keyboard())
        await bot.delete_message(chat_id=message.chat.id, message_id=message_id)
    finally:
        await state.clear()

@router.callback_query(F.data == 'remove_admin')
async def remove_admin_prompt(call: CallbackQuery, state: FSMContext):
    admins_details = await get_admin_details()
    admins_text = ""
    for admin in admins_details:
        admin_id, admin_name = admin
        admin_name = admin_name or "Name not found"
        admin_link = f"[{admin_id}](tg://user?id={admin_id})"
        admins_text += f"{admin_link} | {admin_name}\n"
    all_admins_ids = await get_admins()
    missing_admins = set(all_admins_ids) - {admin[0] for admin in admins_details}
    for missing_admin in missing_admins:
        admins_text += f"{missing_admin} | None\n"
    await call.message.edit_text(
        f"📝 Send the Telegram ID of the admin you want to remove.\n\nAdmins:\n{admins_text}",
        reply_markup=admin_cancel_keyboard(),
        parse_mode="Markdown"
    )
    await state.update_data(msgID=call.message.message_id)
    await state.set_state(AdminManagementState.remove_admin)
    await call.answer()

@router.message(AdminManagementState.remove_admin)
async def remove_old_admin_handler(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    message_id = data.get('msgID')
    try:
        admin_to_remove = int(message.text)
        if admin_to_remove in await get_admins():
            await remove_admin(admin_to_remove)
            await message.answer(f"✅ User {admin_to_remove} has been removed as an admin.", reply_markup=back_to_settings_keyboard())
        else:
            await message.answer("⚠️ This user is not an admin.", reply_markup=back_to_settings_keyboard())
        await bot.delete_message(chat_id=message.chat.id, message_id=message_id)
    except ValueError:
        await message.answer("❌ Invalid Telegram ID. Please send a valid numeric ID.", reply_markup=back_to_settings_keyboard())
        await bot.delete_message(chat_id=message.chat.id, message_id=message_id)
    finally:
        await state.clear()

@router.callback_query(F.data == 'cancel_add_admin', AdminManagementState.add_admin)
@router.callback_query(F.data == 'cancel_add_admin', AdminManagementState.remove_admin)
async def cancel_add_remove_admin_handler(call: CallbackQuery, state: FSMContext):
    await state.clear()
    admins_details = await get_admin_details()
    admins_text = ""
    for admin in admins_details:
        admin_id, admin_name = admin
        admin_name = admin_name or "Name not found"
        admin_link = f"[{admin_id}](tg://user?id={admin_id})"
        admins_text += f"{admin_link} | {admin_name}\n"
    all_admins_ids = await get_admins()
    missing_admins = set(all_admins_ids) - {admin[0] for admin in admins_details}
    for missing_admin in missing_admins:
        admins_text += f"{missing_admin} | None\n"
    settings_message = f"⚙️ Settings Menu:\n\nAdmins:\n{admins_text}"
    await call.message.edit_text(settings_message, reply_markup=settings_keyboard(), parse_mode="Markdown")
    await call.answer()

@router.callback_query(F.data == 'stats')
async def stats_handler(call: CallbackQuery):
    total_users = await count_users()
    new_users = await count_new_users_last_24_hours()
    uptime_seconds = int(time.time() - BOT_START_TIME)
    days, remainder = divmod(uptime_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime = f"{days}d {hours}h {minutes}m {seconds}s"
    total_admins = await count_admins()
    await call.message.edit_text(
        f"📊 All users: {total_users}\n"
        f"👥 Admins: {total_admins}\n"
        f"🆕 New users (last 24h): {new_users}\n"
        f"🕒 Bot Uptime: {uptime}",
        reply_markup=stats_keyboard()
    )
    await call.answer()

@router.callback_query(F.data == 'update')
async def stat_update_handler(call: CallbackQuery, bot: Bot):
    total_users = await count_users()
    new_users = await count_new_users_last_24_hours()
    uptime_seconds = int(time.time() - BOT_START_TIME)
    days, remainder = divmod(uptime_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime = f"{days}d {hours}h {minutes}m {seconds}s"
    total_admins = await count_admins()
    await bot.answer_callback_query(call.id, "🔄 Everything's updated and ready!", show_alert=True)
    await call.message.edit_text(
        f"📊 All users: {total_users}\n"
        f"👥 Admins: {total_admins}\n"
        f"🆕 New users (last 24h): {new_users}\n"
        f"🕒 Bot Uptime: {uptime}",
        reply_markup=stats_keyboard()
    )

@router.callback_query(F.data == 'clear_db')
async def ask_clear_db_handler(call: CallbackQuery):
    if call.from_user.id in await get_admins() or call.from_user.id in ADMINS:
        await call.message.edit_text(
            "⚠️ Are you sure you want to clear the database? This action cannot be undone.",
            reply_markup=admin_confirm_db_keyboard()
        )
    await call.answer()

@router.callback_query(F.data == 'confirm_clear_db')
async def confirm_clear_db_handler(call: CallbackQuery):
    if call.from_user.id in await get_admins() or call.from_user.id in ADMINS:
        await clear_db()
        await call.message.edit_text("🗑 Database has been cleared.", reply_markup=db_back_keyboard())
    await call.answer()

@router.callback_query(F.data == 'cancel_clear_db')
async def cancel_clear_db_handler(call: CallbackQuery):
    admins_details = await get_admin_details()
    admins_text = ""
    for admin in admins_details:
        admin_id, admin_name = admin
        admin_name = admin_name or "Name not found"
        admin_link = f"[{admin_id}](tg://user?id={admin_id})"
        admins_text += f"{admin_link} | {admin_name}\n"
    all_admins_ids = await get_admins()
    missing_admins = set(all_admins_ids) - {admin[0] for admin in admins_details}
    for missing_admin in missing_admins:
        admins_text += f"{missing_admin} | None\n"
    settings_message = f"⚙️ Settings Menu:\n\nAdmins:\n{admins_text}"
    await call.message.edit_text(settings_message, reply_markup=settings_keyboard(), parse_mode="Markdown")
    await call.answer()

@router.callback_query(F.data == 'add_channel')
async def add_channel_prompt(call: CallbackQuery, state: FSMContext, bot: Bot):
    channels = await get_channel_ids()
    channels_text = ""
    for channel in channels:
        channel_username = await get_channel_username(bot, channel)
        channels_text += f"@{channel_username} {channel}\n"
    await call.message.edit_text(
        f"📝 Send the Telegram channel ID you want to add.\n\nExisting channels:\n{channels_text}",
        reply_markup=admin_cancel_keyboard(),
        parse_mode='Markdown'
    )
    await state.update_data(msgID=call.message.message_id)
    await state.set_state(ChannelManagementState.add_channel)
    await call.answer()

@router.message(ChannelManagementState.add_channel)
async def add_new_channel_handler(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    message_id = data.get('msgID')
    new_channel = message.text.strip()
    if new_channel in await get_channel_ids():
        await message.answer("⚠️ This channel is already added.", reply_markup=back_to_settings_keyboard())
    else:
        await add_channel(new_channel)
        channel = await get_channel_username(bot, new_channel)
        await message.answer(f"✅ Channel @{channel} has been added.", reply_markup=back_to_settings_keyboard())
    await bot.delete_message(chat_id=message.chat.id, message_id=message_id)
    await state.clear()

@router.callback_query(F.data == 'remove_channel')
async def remove_channel_prompt(call: CallbackQuery, state: FSMContext, bot: Bot):
    channels = await get_channel_ids()
    channels_text = ""
    for channel in channels:
        channel_username = await get_channel_username(bot, channel)
        channels_text += f"@{channel_username} {channel}\n"
    await call.message.edit_text(
        f"📝 Send the channel ID you want to remove.\n\nExisting channels:\n{channels_text}",
        reply_markup=admin_cancel_keyboard(),
        parse_mode='Markdown'
    )
    await state.update_data(msgID=call.message.message_id)
    await state.set_state(ChannelManagementState.remove_channel)
    await call.answer()

@router.message(ChannelManagementState.remove_channel)
async def remove_existing_channel_handler(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    message_id = data.get('msgID')
    channel_to_remove = message.text.strip()
    if channel_to_remove in await get_channel_ids():
        await remove_channel(channel_to_remove)
        channel = await get_channel_username(bot, channel_to_remove)
        await message.answer(f"✅ Channel @{channel} has been removed.", reply_markup=back_to_settings_keyboard())
    else:
        await message.answer("⚠️ This channel does not exist.", reply_markup=back_to_settings_keyboard())
    await bot.delete_message(chat_id=message.chat.id, message_id=message_id)
    await state.clear()

@router.callback_query(F.data == 'settings')
async def open_settings_handler(call: CallbackQuery):
    admins_details = await get_admin_details()
    admins_text = ""
    for admin in admins_details:
        admin_id, admin_name = admin
        admin_name = admin_name or "Name not found"
        admin_link = f"[{admin_id}](tg://user?id={admin_id})"
        admins_text += f"{admin_link} | {admin_name}\n"
    all_admins_ids = await get_admins()
    missing_admins = set(all_admins_ids) - {admin[0] for admin in admins_details}
    for missing_admin in missing_admins:
        admins_text += f"{missing_admin} | None\n"
    settings_message = f"⚙️ Settings Menu:\n\nAdmins:\n{admins_text}"
    await call.message.edit_text(settings_message, reply_markup=settings_keyboard(), parse_mode="Markdown")
    await call.answer()

@router.callback_query(F.data == 'goback')
async def goback_handler(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("Choose what you are going to do?", reply_markup=admin_keyboard())
    await state.clear()
    await call.answer()
