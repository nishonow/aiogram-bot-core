from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

def start_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="🎲 Random Fact")
    return builder.as_markup(resize_keyboard=True)

def admin_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="📊 Statistics", callback_data="stats")
    builder.button(text="📤 Broadcast", callback_data='broadcast')
    builder.button(text="⚙️ Settings", callback_data="settings")
    builder.adjust(1)
    return builder.as_markup()

def settings_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🗑 Clear Database", callback_data="clear_db")
    builder.button(text="➕ Add Admin", callback_data="add_admin")
    builder.button(text="➖ Remove Admin", callback_data="remove_admin")
    builder.button(text="➕ Add Channel", callback_data="add_channel")
    builder.button(text="➖ Remove Channel", callback_data="remove_channel")
    builder.button(text="⬅️ Back", callback_data="goback")
    builder.adjust(1, 2, 2, 1)
    return builder.as_markup()

def stats_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🔄 Update", callback_data="update")
    builder.button(text="⬅️ Back", callback_data="goback")
    builder.adjust(1)
    return builder.as_markup()

def admin_back_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Back", callback_data="goback")
    return builder.as_markup()

def db_back_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Back", callback_data="cancel_add_admin")
    return builder.as_markup()

def confirm_broadcast_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Confirm", callback_data="confirm")
    builder.button(text="🚫 Decline", callback_data="decline")
    return builder.as_markup()

def admin_confirm_db_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Confirm", callback_data="confirm_clear_db")
    builder.button(text="❌ Cancel", callback_data="cancel_clear_db")
    return builder.as_markup()

def admin_cancel_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Cancel", callback_data="cancel_add_admin")
    return builder.as_markup()

def back_to_settings_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Back", callback_data="cancel_add_admin")
    return builder.as_markup()
