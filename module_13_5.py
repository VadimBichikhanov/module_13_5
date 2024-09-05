from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import CommandStart, StateFilter
import logging
import asyncio
from os import getenv

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Получение токена бота из переменных окружения
API_TOKEN = getenv('TELEGRAM_TOKEN')

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Определение машины состояний
class Form(StatesGroup):
    age = State()
    growth = State()
    weight = State()

# Обработчик команды /start
@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Рассчитать")],
            [KeyboardButton(text="Информация")]
        ],
        resize_keyboard=True
    )
    await message.answer("Добро пожаловать! Выберите действие:", reply_markup=keyboard)

# Обработчик кнопки "Рассчитать"
@dp.message(F.text == "Рассчитать")
async def calculate_start(message: Message, state: FSMContext):
    await message.answer("Пожалуйста, введите ваш возраст:")
    await state.set_state(Form.age)

# Обработчик ввода возраста
@dp.message(StateFilter(Form.age))
async def process_age(message: Message, state: FSMContext):
    await process_numeric_input(message, state, 'age', "Теперь введите ваш рост:", Form.growth)

# Обработчик ввода роста
@dp.message(StateFilter(Form.growth))
async def process_growth(message: Message, state: FSMContext):
    await process_numeric_input(message, state, 'growth', "Теперь введите ваш вес:", Form.weight)

# Обработчик ввода веса
@dp.message(StateFilter(Form.weight))
async def process_weight(message: Message, state: FSMContext):
    await process_numeric_input(message, state, 'weight', "Спасибо за информацию! Ваш возраст: {data['age']}, рост: {data['growth']}, вес: {data['weight']}", None, calculate_calories)

# Обработчик кнопки "Информация"
@dp.message(F.text == "Информация")
async def show_info(message: Message):
    await message.answer("Этот бот помогает рассчитать ваши ежедневные потребности в калориях.")

async def process_numeric_input(message: Message, state: FSMContext, key: str, prompt: str, next_state: State, callback=None):
    try:
        value = int(message.text)
        await state.update_data(**{key: value})
        if callback:
            await callback(message, state)
        else:
            data = await state.get_data()
            await message.reply(prompt.format(data=data))
            await state.set_state(next_state)
    except ValueError:
        await message.reply('Пожалуйста, введите корректное число.')

async def calculate_calories(message: Message, state: FSMContext):
    data = await state.get_data()
    age = data['age']
    growth = data['growth']
    weight = data['weight']

    # Формула Миффлина - Сан Жеора для женщин
    calories = 10 * weight + 6.25 * growth - 5 * age - 161

    await message.reply(f'Ваша норма калорий: {calories:.2f} ккал в день.')
    await state.clear()

# Функция для перехвата сообщений
@dp.message()
async def handle_message(message: Message):
    await message.answer('Привет! Я бот, который поможет тебе рассчитать норму калорий. \nИспользуй команду /start, чтобы начать.')

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())