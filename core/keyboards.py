from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

start = ReplyKeyboardMarkup(resize_keyboard=True)
start.add(KeyboardButton(text="🎲 Random Fact"))


# ADMIN KEYBOARDS ==========================================================================

adminKey = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📊 Statistics", callback_data="stats")],
        [InlineKeyboardButton(text="📤 Broadcast", callback_data='broadcast')],
        [InlineKeyboardButton(text="⚙️ Settings", callback_data="settings")],
    ]
)
settingsKey = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🗑 Clear Database", callback_data="clear_db")],
        [
            InlineKeyboardButton(text="➕ Add Admin", callback_data="add_admin"),
            InlineKeyboardButton(text="➖ Remove Admin", callback_data="remove_admin")
        ],
        [
            InlineKeyboardButton(text="➕ Add Channel", callback_data="add_channel"),
            InlineKeyboardButton(text="➖ Remove Channel", callback_data="remove_channel")
        ],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="goback")],
    ]
)

statsKey = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Update", callback_data="update")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="goback")],
    ]
)
adminBack = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back", callback_data="goback")]
    ]
)
dbBack = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back", callback_data="cancel_add_admin")]
    ]
)

ConfirmBroadcast = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✅ Confirm", callback_data="confirm")],
        [InlineKeyboardButton(text="🚫 Decline", callback_data="decline")]
    ]
)
adminConfirmDB = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Confirm", callback_data="confirm_clear_db")],
        [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_clear_db")]
    ]
)
adminCancelKey = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_add_admin")]
    ]
)
backToSettings = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back", callback_data="cancel_add_admin")]
    ]
)