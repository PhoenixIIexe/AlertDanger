import asyncio
import logging
import sys
import os
from os import getenv
import threading
import cv2

from data import models

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, BufferedInputFile
from aiogram.utils.markdown import hbold

# TOKEN = getenv("BOT_TOKEN")
TOKEN = "6387141164:AAGlhalsLlLAySHRp7Qhg6e-gN_Fds23_M8"

bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer(f"Привет, {hbold(message.from_user.full_name)}!\nЧтобы получить уведомления об опасных ситуация напишете /reg")


@dp.message(Command('reg'))
async def reg(message: Message) -> None:
    user: models.User = models.session.query(
        models.User).filter_by(telegram_id=message.from_user.id).first()
    if user is None:
        await message.answer("С этого момента вам будет отправляться уведомление в случае возникновения опасной ситуации.")
        user = models.User(telegram_id=message.from_user.id)

        models.session.add(user)
        models.session.commit()


async def send_messing(photo, img_path):
    users = models.session.query(
        models.User).all()

    success, encoded_image = cv2.imencode(".jpg", photo)
    photo_file = BufferedInputFile(encoded_image.tobytes(), filename=img_path)

    for user in users:
        await bot.send_photo(user.telegram_id, photo_file, caption="Человек попал в опасную зону!")


async def get_alert():
    while True:
        for img_path in os.listdir('alert'):
            photo = cv2.imread('alert/' + img_path)
            await send_messing(photo, img_path)
            os.remove('alert/' + img_path)
        await asyncio.sleep(1)


async def main() -> None:
    await asyncio.gather(dp.start_polling(bot), get_alert())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
