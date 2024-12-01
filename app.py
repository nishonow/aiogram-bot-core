import logging
from aiogram import executor
from loader import dp, bot
import handlers
import core
logging.basicConfig(
    format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
    level=logging.INFO,
)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
