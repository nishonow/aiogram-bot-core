import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import handlers
from core.db import on_startup
from config import BOT_TOKEN

async def main():
    logging.basicConfig(
        format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
        level=logging.INFO,
    )

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Include routers from handlers
    dp.include_router(handlers.start.router)
    dp.include_router(handlers.admin.router)

    # Register admin middleware
    from middlewares.admin_middleware import AdminMiddleware
    handlers.admin.router.message.middleware(AdminMiddleware())
    handlers.admin.router.callback_query.middleware(AdminMiddleware())

    await on_startup()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
