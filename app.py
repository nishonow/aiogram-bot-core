import logging
from aiogram import executor
from loader import dp, bot
import handlers
import core
import time

BOT_START_TIME = time.time()
logging.basicConfig(
    format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
    level=logging.INFO,
)

async def on_startup(dp):
    await core.db.init_db()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
