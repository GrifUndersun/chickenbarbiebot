import config
import parse_anek
import aiogram
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor


BOT_TOKEN = config.BOT_TOKEN
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


groupNum = 151115

button_anekdot = types.InlineKeyboardButton('Анекдоты 🤡', callback_data='anek')
keyboard_start = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard = False)
keyboard_start.add(button_anekdot)


@dp.message_handler(commands=['start'])
async def welcome_message(msg: types.Message):
    await bot.send_message(msg.chat.id,
                           f'Че надо?\n'
                           f'Читай анеки /anek',
                           parse_mode='HTML',
                           reply_markup=keyboard_start)


@dp.message_handler(commands='anek')
async def send_anekdot(msg: types.Message):
    str = parse_anek.getanekdot()
    await bot.send_message(msg.chat.id,
                           str, parse_mode='HTML')


@dp.message_handler(lambda message: message.text == 'Анекдоты 🤡')
async def ans_button_anekdot(msg: types.Message):
    await send_anekdot(msg)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
