import json
from aiogram import Bot, Dispatcher, executor, types
import random
from datetime import datetime
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

admin_ids = ['id']

API_TOKEN = 'token'


bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)



data_file = 'sizes.json'


def load_sizes():
    try:
        with open(data_file, 'r') as file:
            return json.load(file)
    except (IOError, json.JSONDecodeError):
        return {}

def save_sizes(sizes):
    with open(data_file, 'w') as file:
        json.dump(sizes, file)

sizes = load_sizes()


@dp.message_handler(commands=['top_dick'])
async def chat_top(message: types.Message):
    chat_id = str(message.chat.id)
    chat_sizes = sizes.get(chat_id, {})
    
    if not chat_sizes:
        await message.reply("В этом чате ещё нет записей.")
        return

    top_users = sorted(chat_sizes.items(), key=lambda x: x[1]['size'], reverse=True)[:10]
    response = "Топ пользователей в этом чате:\n" + "\n".join(
        [f"{idx+1}. {data['name']}: {data['size']} см" for idx, (user_id, data) in enumerate(top_users)]
    )
    await message.reply(response)


@dp.message_handler(commands=['global_top'])
async def global_top(message: types.Message):
    all_sizes = {user_id: data for chat in sizes.values() for user_id, data in chat.items() if isinstance(data, dict) and 'size' in data}
    top_users = sorted(all_sizes.items(), key=lambda x: x[1]['size'], reverse=True)[:10]

    response = "Глобальный топ пользователей:\n" + "\n".join(
        [f"{idx+1}. {data['name']}: {data['size']} см" for idx, (user_id, data) in enumerate(top_users)]
    )
    await message.reply(response)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    if message.chat.type == 'private':
        welcome_text = (
            "Привет! я линейка — бот для чатов (групп).\n\n"
            "Смысл бота: бот работает только в чатах. Раз\n"
            "в 24 часа игрок может прописать команду\n"
            "/dick, где в ответ получит от бота рандомное\n"
            "число.\n"
            "Рандом работает от -5 см до +10 см.\n\n"
            "Если у тебя есть вопросы — пиши команду: /help"
        )
        keyboard = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton(text="Добавить бота в группу", url=f"https://t.me/payseratest_bot?startgroup=true")#замените на свои
        keyboard.add(button)
        await message.reply(welcome_text, reply_markup=keyboard)
    else:
        await message.reply("Этот бот работает только в личных сообщениях.")
@dp.message_handler(commands=['help'])
async def send_help(message: types.Message):
    help_text = (
        "Команды бота:\n"
        "/dick — Вырастить/уменьшить пипису\n"
        "/top_dick — Топ 10 пипис чата\n"
        "/stats — Статистика в виде картинки\n"
        "/global_top — Глобальный топ 10 игроков\n"
        "Контакты:\n"
        "Наш канал — @pipisa_news\n"#замените на свои
        "Наш чат — https://t.me/+Vc5u7PMtm543YWVi" #замените на свои
    )
    await message.reply(help_text)

@dp.message_handler(commands=['dick'])
async def send_random_size(message: types.Message):
    if message.chat.type == 'private':
        keyboard = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton(text="Добавить бота в группу", url=f"https://t.me/payseratest_bot?startgroup=true")#замените на свои
        keyboard.add(button)
        await message.reply("Используйте эту команду в групповом чате.", reply_markup=keyboard)
        return

    chat_id = str(message.chat.id)
    user_id = str(message.from_user.id)
    user_name = message.from_user.full_name 
    user_mention = message.from_user.get_mention(as_html=True)  

    if chat_id not in sizes:
        sizes[chat_id] = {}

    if user_id not in sizes[chat_id]:
        sizes[chat_id][user_id] = {'size': 15, 'last_time': 0, 'name': user_name}
    else:
        sizes[chat_id][user_id]['name'] = user_name  

    user_data = sizes[chat_id][user_id]
    last_time = user_data['last_time']

    if last_time:
        last_time_dt = datetime.fromtimestamp(last_time)
        if (message.date - last_time_dt).total_seconds() < 86400:
            await message.reply("Следующая попытка завтра!")
            return

    change = random.randint(-5, 10)
    user_data['size'] += change
    user_data['last_time'] = message.date.timestamp()
    sizes[chat_id][user_id] = user_data
    save_sizes(sizes)

    chat_sizes = sizes[chat_id]
    sorted_users = sorted(chat_sizes.items(), key=lambda x: x[1]['size'], reverse=True)
    rank = next((idx for idx, item in enumerate(sorted_users, 1) if item[0] == user_id), None)

    response = (
        f"{user_mention}, твой писюн вырос на {change} см.\n"
        f"Теперь он равен {user_data['size']} см.\n"
        f"Ты занимаешь {rank} место в топе этого чата.\n"
        "Следующая попытка завтра!"
    )
    await message.reply(response, parse_mode='HTML')

@dp.message_handler(commands=['admin']) # не готова
async def admin_panel(message: types.Message):
    if str(message.from_user.id) in admin_ids:
        keyboard = InlineKeyboardMarkup(row_width=1)
        reset_button = InlineKeyboardButton(text="Сбросить время", callback_data="reset_time") 
        broadcast_button = InlineKeyboardButton(text="Рассылка изображения", callback_data="broadcast_image")
        keyboard.add(reset_button, broadcast_button)
        await message.reply("Админ панель:", reply_markup=keyboard)
    else:
        await message.reply("У вас нет прав для доступа к админ панели.")

@dp.callback_query_handler(lambda c: c.data == 'broadcast_image')
async def send_broadcast_image(callback_query: types.CallbackQuery):
    if str(callback_query.from_user.id) in admin_ids:
        await bot.answer_callback_query(callback_query.id, "Здесь будет реализация отправки изображения")
    else:
        await bot.answer_callback_query(callback_query.id, "У вас нет прав для выполнения этой команды.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
