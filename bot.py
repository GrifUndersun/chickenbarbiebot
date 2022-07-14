import datetime
import traceback  # для правильного вывода ошибок в консоль в
import aioschedule  # для
import asyncio  # для написания асинхронного кода
import config as cfg  #
import parse_timetable as pt  # для получения расписания с сайта http://ruz.narfu.ru
import parse_weather as weather  # для получения погоды с сайта http://openwethermap.org
import os

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

from aiogram.utils.exceptions import MessageNotModified
from contextlib import suppress

# Объект бота, подключается к созданному в @BotFather в Telegram боту по токену
bot = Bot(token = os.environ['BOT_TOKEN'])
# Хранилище для FSM
storage = MemoryStorage()
# Диспетчер для бота, который будет отслеживать все сообщения от пользователя
dp = Dispatcher(bot, storage=storage)


class Form(StatesGroup):
    text = State()
    add_group = State()
    add_city = State()
    city = State()


commands = {
    'group': 'group',
    'city': 'city',
    'me': 'me',
    'help': 'help',
    'start': 'start'
}

users_students = cfg.open_usersDB('database_students.json')
users_weather = weather.openDB()

button_timetable = types.InlineKeyboardButton('Расписание 🕘')
button_mailing = types.InlineKeyboardButton('Рассылка 📪')
button_help = types.InlineKeyboardButton('Помощь 🤖', callback_data='show_help')
button_weather = types.InlineKeyboardButton('Погода ☁')

keyboard_start = types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard_start.add(button_timetable)
keyboard_start.add(button_weather)
keyboard_start.add(button_help, button_mailing)


# -------------------- Методы для работы с базами данных --------------------


def get_user_dict(db, target):
    """ Получение словаря из баззы данных
        Указываем базу данных, откуда надо достать словарь
        И ID пользователя, словарь данных которого надо найти """

    for x in db:
        if x['id'] == int(target):
            return x


# -------------------- Команда отмены добавления города или номера группы --------------------


async def cancel_handler(msg, state):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await msg.reply('ОК')


# -------------------- Обработка команд --------------------

# Обработка команды /start
@dp.message_handler(commands=['start'])
async def welcome_message(msg: types.Message):
    await bot.send_message(msg.chat.id,
                           f'Привет, <b>{msg.from_user.first_name}</b>!\n'
                           f'Здесь вы можете:\n'
                           f'✅ Узнать расписание вашей группы\n\n'
                           f'Если вы запустили этот бот в первый раз:\n'
                           f'Добавить свою группу /{commands["group"]}\n'
                           f'Добавить город /{commands["city"]}',
                           parse_mode='HTML',
                           reply_markup=keyboard_start)


# Обработка команды /help
@dp.message_handler(commands=['help'])
async def show_commands(msg: types.Message):
    await bot.send_message(msg.chat.id,
                           f'Вам доступны такие команды:\n\n'
                           f'✅ /{commands["group"]} - установить номер группы. Также можно его перезаписать\n'
                           f'✅ /{commands["city"]} - установить город. Также можно его перезаписать\n'
                           f'✅ /{commands["me"]} - информация о пользователе\n'
                           f'✅ /{commands["start"]} - отправить приветсвенное сообщение\n'
                           f'✅ /{commands["help"]} - показать список команд\n\n'
                           f'Если бот работает некорректно, писать @rewxrld')


# Обработка команды /me
@dp.message_handler(commands=commands['me'])
async def show_user_info(msg: types.Message):
    student = get_user_dict(users_students, msg.from_user.id)
    user = get_user_dict(users_weather, msg.from_user.id)
    mailing_str = ''
    if student['mailing']:
        mailing_str += f'✅ Включена рыссылка расписания\n'
    elif not student['mailing']:
        mailing_str += f'❌ Выключена рассылка расписания\n'
    if user['mailing']:
        mailing_str += f'✅ Включена рыссылка погоды\n'
    elif not user['mailing']:
        mailing_str += f'❌ Выключена рассылка погоды\n'
    try:
        await msg.reply(f'👨‍💻 Имя пользователя: <b>{msg.from_user.first_name}</b>\n'
                        f'🏫 Группа: <b>{student["group"]} - '
                        f'{pt.get_groupName(student["group"])}</b>\n\n'
                        f'{mailing_str}',
                        parse_mode='HTML')
    except Exception as e:
        print(e)
        await msg.reply(f'👨‍💻 Имя пользователя: <b>{msg.from_user.first_name}</b>\n'
                        f'🏫 Группа: <b>Вы не выбрали группу. Для выбора группы нажмите '
                        f'/{commands["group"]}</b>\n',
                        parse_mode='HTML')


# Обработка команды /group
@dp.message_handler(commands=commands["group"])
async def add_user(msg: types.Message):
    await Form.add_group.set()
    await msg.answer('Напишите номер вашей группы\n'
                     'Для отмены /cancel')


# Обработка команды /city
@dp.message_handler(commands=commands["city"])
async def add_city(msg: types.Message):
    await Form.add_city.set()
    await msg.answer('Напишите название вашего города\n'
                     'Для отмены /cancel')


# -------------------- Расписание --------------------


def get_keyboard_days_timetable(id):
    try:
        user = get_user_dict(users_students, id)
        timetable = pt.get_timetable(user["group"])
        days, table = pt.print_timetable(timetable)
        keyboard_days = types.InlineKeyboardMarkup(row_width=1)
        for i in range(len(days)):
            keyboard_days.add(types.InlineKeyboardButton(text=days[i], callback_data='num_{}'.format(i)))
        return keyboard_days
    except Exception as e:
        print(traceback.format_exc())
        print('Get keyboard days timetable:', e)


@dp.message_handler(lambda message: message.text == 'Расписание 🕘')
async def show_timetable(msg: types.Message):
    try:
        await msg.answer(f'Выберите дату', reply_markup=get_keyboard_days_timetable(msg.chat.id))
    except Exception as e:
        print(traceback.format_exc())
        print('Exception (show timetable): ', e)
        await bot.send_message(msg.chat.id, f'<b>Вы не выбрали свою группу!</b>\nВыбрать группу /{commands["group"]}',
                               parse_mode='HTML')


async def update_timetable_text(msg, value):
    try:
        with suppress(MessageNotModified):
            await msg.edit_text(f'{value}\n\nВыберите дату', parse_mode='HTML',
                                reply_markup=get_keyboard_days_timetable(msg.chat.id))
    except Exception as e:
        print(traceback.format_exc())
        print('Update timetable text:', e)


@dp.callback_query_handler(Text(startswith="num_"))
async def callbacks_num(call: types.CallbackQuery):
    try:
        user = get_user_dict(users_students, call.from_user.id)
        timetable = pt.get_timetable(user["group"])
        days, table = pt.print_timetable(timetable)
        action = int(call.data.split('num_')[1])

        result_str = f'{days[action]}\n{table[action]}'
        await update_timetable_text(call.message, result_str)
        # Отчитываемся о получении колбэка
        await call.answer()
    except Exception as e:
        print('Callbacks num:', e)
        await bot.send_message(call.from_user.id, '<b>Вы не выбрали свою группу!</b>\nВыбрать группу /group',
                               parse_mode='HTML')
        await call.answer()


# Добавляем возможность отмены, если пользователь передумал добавлять номер группы
@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('ОК')


# Сюда приходит ответ с номером группы
@dp.message_handler(state=Form.add_group)
async def process_name(msg: types.Message, state: FSMContext):
    global users_students
    if pt.get_siteID(msg.text) is None:
        await bot.send_message(msg.chat.id, f'Такой группы не существует! Попробуйте снова')
    else:
        users_students = cfg.save_usersDB('database_students.json', int(msg.from_user.id), int(msg.text), 0)
        await state.finish()
        print(users_students)
        await bot.send_message(msg.chat.id, f'Ваша группа {msg.text} - {pt.get_groupName(msg.text)}')


# -------------------- Погода --------------------


@dp.message_handler(lambda message: message.text == 'Погода ☁')
async def get_weather(msg: types.Message):
    print(users_weather, '\n', msg.from_user.id)
    try:
        user = get_user_dict(users_weather, msg.from_user.id)
        result = weather.get_weather(user['city'])
        await bot.send_message(msg.chat.id, result)
    except Exception as e:
        print('Get weather:', e)
        await Form.add_city.set()
        await msg.answer('Вы не сохраняли город.\nВведите название города')


# Добавляем возможность отмены, если пользователь передумал добавлять номер группы
@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('ОК')


# Сюда приходит ответ с ннавазнием города
@dp.message_handler(state=Form.add_city)
async def add_city(msg: types.Message, state: FSMContext):
    global users_weather
    if weather.get_weather(str(msg.text)) is None:
        await bot.send_message(msg.chat.id, 'Проверьте название города')
    else:
        users_weather = weather.saveDB(int(msg.from_user.id), str(msg.text), False)
        await state.finish()
        print(users_weather)
        await bot.send_message(msg.chat.id, f'Ваш город - {msg.text.capitalize()}')


# -------------------- Обработка кнопки помощь --------------------


@dp.message_handler(lambda message: message.text == 'Помощь 🤖')
async def ans_button_commands(msg: types.Message):
    await show_commands(msg)


# -------------------- Рассылка --------------------


def get_keyboard_mailing(mailing_timetable, mailing_weather):
    if mailing_timetable:
        button_1 = types.InlineKeyboardButton('❌ Отказаться от рассылки расписания',
                                              callback_data='mailing_off_timetable')
    else:
        button_1 = types.InlineKeyboardButton('✅ Согласиться на рыссылку расписания',
                                              callback_data='mailing_on_timetable')
    if mailing_weather:
        button_2 = types.InlineKeyboardButton('❌ Отказаться от рассылки погоды',
                                              callback_data='mailing_off_weather')
    else:
        button_2 = types.InlineKeyboardButton('✅ Согласиться на рыссылку погоды',
                                              callback_data='mailing_on_weather')
    keyboard = types.InlineKeyboardMarkup().add(button_1)
    keyboard.add(button_2)

    return keyboard


@dp.message_handler(lambda message: message.text == 'Рассылка 📪')
async def ans_button_mailing(msg: types.Message):
    student = get_user_dict(users_students, msg.from_user.id)
    user = get_user_dict(users_weather, msg.from_user.id)
    try:
        MailingTimetable = student['mailing']
        MailingWeather = user['mailing']
        with suppress(MessageNotModified):
            await msg.answer(f'Выберите действие', parse_mode='HTML',
                             reply_markup=get_keyboard_mailing(MailingTimetable, MailingWeather))
    except Exception as e:
        print(e)
        if student is None:
            await add_user(msg)
        elif user is None:
            await Form.city.set()
            await msg.answer('Вы не сохраняли город.\nВведите название города')


async def update_text_mailing(msg: types.Message, valueTimetable, valueWeather):
    with suppress(MessageNotModified):
        await msg.edit_text(f'Выберите действие', parse_mode='HTML',
                            reply_markup=get_keyboard_mailing(valueTimetable, valueWeather))


@dp.callback_query_handler(Text(startswith="mailing_"))
async def callbacks_mail(call: types.CallbackQuery):
    global users_students, users_weather
    student = get_user_dict(users_students, int(call.from_user.id))
    user = get_user_dict(users_weather, int(call.from_user.id))
    action = str(call.data.split('mailing_')[1])
    switch1 = student['mailing']
    switch2 = user['mailing']
    if action == 'on_timetable':
        switch1 = True
        users_students = cfg.save_usersDB('database_students.json', int(call.from_user.id), student['group'], True)
    elif action == 'off_timetable':
        switch1 = False
        users_students = cfg.save_usersDB('database_students.json', str(call.from_user.id), student['group'], False)
    else:
        pass
    if action == 'on_weather':
        switch2 = True
        users_weather = weather.saveDB(int(call.from_user.id), user['city'], True)
    elif action == 'off_weather':
        switch2 = False
        users_weather = weather.saveDB(int(call.from_user.id), user['city'], False)
    await update_text_mailing(call.message, switch1, switch2)
    await call.answer()


@dp.message_handler(content_types=['text'])
async def send_text(msg: types.Message):
    if msg.text == 'Расписание 🕘' or msg.text == 'Помощь 🤖' or msg.text == 'Рассылка 📪' \
            or msg.text == 'Погода ☁' or msg.text in commands.keys():
        pass
    else:
        await bot.send_message(msg.chat.id, f'❌ <b>Я не понимаю этой команды!</b>\n'
                                            f'Посмотреть список доступных команд\n/{commands["help"]}',
                               parse_mode='HTML')


@dp.message_handler()
async def mailing_timetable():
    dayNumber = datetime.datetime.today().weekday()
    if dayNumber == 6:
        pass
    else:
        for x in users_students:
            if x['mailing']:
                timetable = pt.get_timetable(x['group'])
                days, table = pt.print_timetable(timetable)
                result_str = f'Ежедневная рассылка расписания\n\n{days[dayNumber]}\n{table[dayNumber]}'
                await bot.send_message(x['id'], result_str, parse_mode='HTML')


@dp.message_handler()
async def mailing_weather():
    for x in users_weather:
        if x['mailing']:
            result_str = f'Ежедневная рассылка погоды\n\n{weather.get_forecast(x["city"])}'
            await bot.send_message(x['id'], result_str, parse_mode='HTML')


async def scheduler():
    try:
        aioschedule.every().day.at("0:50").do(mailing_timetable)
        aioschedule.every().day.at("3:30").do(mailing_weather)
        while True:
            await aioschedule.run_pending()
            await asyncio.sleep(1)
    except Exception as e:
        print(e)
        pass


async def on_startup(dp):
    asyncio.create_task(scheduler())


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
