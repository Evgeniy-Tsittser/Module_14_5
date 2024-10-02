from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
from crud_functions import *

connection = sqlite3.connect('products.db')
cursor = connection.cursor()
# Создаем базу данных
initiate_db()

# for i in range(1, 5):
#      cursor.execute("INSERT INTO Products (title, description, price) VALUES (?,?,?)",
#                    (f"Продукт_{i}", f"Описание_{i}", f"Цена_{100*i}"))

connection.commit()


# Инициализируем связь с Телеграмм-ботом
api = "6428640948:AAFPKZ7HJ8wCkhT37935upmsO_1N-YVWOH4"
bot = Bot(token=api)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Создаем кнопку "Рассчитать" (после ввода /start)
kb = ReplyKeyboardMarkup(resize_keyboard=True)
button_1 = KeyboardButton(text='Рассчитать')
button_2 = KeyboardButton(text='Информация')
kb.row(button_1, button_2)
button_3 = KeyboardButton(text='Купить')
button_4 = KeyboardButton(text='Регистрация')
kb.row(button_3, button_4)

catalog_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
        InlineKeyboardButton(text='Продукт 1', callback_data='product_buying'),
        InlineKeyboardButton(text='Продукт 2', callback_data='product_buying'),
        InlineKeyboardButton(text='Продукт 3', callback_data='product_buying'),
        InlineKeyboardButton(text='Продукт 4', callback_data='product_buying')
         ]
    ]
)

# Создаем инлайн-кнопки в одну строку (после нажатия кнопки "Рассчитать")
combined_kb = InlineKeyboardMarkup(row_width=2)
combined_kb.add(InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories'),
    InlineKeyboardButton(text='Формулы расчета', callback_data='formulas'))

# Создаем класс вводимых параметров для регистрации
class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()
    balance = 1000

# Создаем класс вводимых параметров для рассчетов
class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

# Запускаем бота в работу
@dp.message_handler(commands=['start'])
async def start(message):
    await message.answer('Привет, я бот помогающий твоему здоровью!', reply_markup = kb)

# Ответ на нажатие кнопки "Регистрация"
@dp.message_handler(text=['Регистрация'])
async def sing_up(message):
    await message.answer('Введите имя пользователя (только латинский алфавит):')
    await RegistrationState.username.set()

# Проверка имени пользователя
@dp.message_handler(state=RegistrationState.username)
async def set_username(message, state):
    if not is_included(message.text):
        await state.update_data(username=message.text)
        await message.answer('Введите свой email:')
        await RegistrationState.email.set()
    else:
        await message.answer('Пользователь существует, введите другое имя')
        await RegistrationState.username.set()

# Ввод почты
@dp.message_handler(state=RegistrationState.email)
async def set_email(message, state):
    await state.update_data(email=message.text)
    await message.answer('Введите свой возраст:')
    await RegistrationState.age.set()

# Ввод возраста
@dp.message_handler(state=RegistrationState.age)
async def set_age(message, state):
    await state.update_data(age=message.text)
    data = await state.get_data()
    add_user(data['username'], data['email'], data['age'])
    await message.answer('Регистрация успешна!')
    await state.finish()

# Ответ на нажатие кнопки "Купить"
@dp.message_handler(text=['Купить'])
async def get_buying_list(message):
    products = get_all_products()
    for product in products:
            await message.answer(text = f'Название: {product[1]}, Описание: {product[2]}, Цена: {product[3]}')
            with open(f'files2/{product[0]}.png', 'rb') as img:
                await message.answer_photo(img)
    await message.answer(text="Выберите продукт для покупки", reply_markup=catalog_kb)

@dp.callback_query_handler(text =['product_buying'])
async def send_confirm_message(call):
    await call.message.answer('Вы успешно приобрели продукт!')

# Ответ на нажатие кнопки "Рассчитать"
@dp.message_handler(text=['Рассчитать'])
async def main_menu(message):
    await message.answer('Выберите опцию:', reply_markup=combined_kb)

# Ответ на нажатие кнопки "Формулы рассчета"
@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer("Упрощенный вариант формулы Миффлина-Сан Жеора: "
                              "для мужчин: 10 * вес (кг) + 6,25 * рост (см) – 5 * возраст (г) + 5; "
                              "для женщин: 10 * вес (кг) + 6,25 * рост (см) – 5 * возраст (г) - 161")
    await call.answer()

# Ответ на нажатие кнопки "Расситать норму калорий" (запуск запроса параметров)
@dp.callback_query_handler(text =['calories'])
async def set_age(call):
    await call.message.answer('Введите свой возраст, лет:')
    await UserState.age.set()

# запрос параметров
@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=message.text)
    await message.answer(f'Введите свой рост, сантиметры:')
    await UserState.growth.set()

# запрос параметров
@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=message.text)
    await message.answer(f'Введите свой вес, килограммы:')
    await UserState.weight.set()

# рассчет калорий по параметрам
@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=message.text)
    data = await state.get_data()
    norm_calory = 10 * int(data['weight']) + 6.25 * int(data['growth']) - 5 * int(data['age']) + 5
    await message.answer(f'Ваша норма калорий: {norm_calory} в сутки')
    await state.finish()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)