import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.enums import ParseMode
from aiogram.client.bot import DefaultBotProperties

logging.basicConfig(level=logging.INFO)

# Замените на токен вашего бота
BOT_TOKEN = "7712066245:AAHHkKuTRWW9VFk3wl6gxkBOWi679wfBg5c"
# ID администратора, которому будут пересылаться данные о пользователе
ADMIN_ID = 7667816800

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Маппинг для преобразования значений ответов в читаемые строки
ANSWER_TEXTS = {
    'q1': {
         'q1_yes': "Да",
         'q1_no': "Нет"
    },
    'q2': {
         'q2_1': "до 1 часа в день",
         'q2_3_5': "до 3-5 часов в день",
         'q2_6_10': "до 6-10 часов в день"
    },
    'q3': {
         'q3_option1': "от 250к до 350.000кР",
         'q3_option2': "от 500.000₽",
         'q3_option3': "от 1.000.000₽"
    },
    'q4': {
         'q4_option1': "500.000₽",
         'q4_option2': "3.000.000₽",
         'q4_option3': "1.000.000₽"
    }
}

# Определяем состояния для квиза
class Quiz(StatesGroup):
    q1 = State()  # Выбор "Да" / "Нет"
    q2 = State()  # Выбор по времени (часы в день)
    q3 = State()  # Выбор бюджета (первый блок)
    q4 = State()  # Выбор бюджета (второй блок)
    waiting_for_final = State()  # ожидание финальных действий

# Стартовая команда /start
@dp.message(Command("start"))
async def start_handler(message: types.Message, state: FSMContext):
    photo_path = "1.jpg"  # путь к первой картинке
    text = """<b>Приветствую!</b> 🖐

Ты попал в самый мощный бесплатный продукт на рынке Telegram

Лично я благодаря этим знаниям залил больше 20 миллионов рублей рекламного бюджета

➡️ <b>Сейчас расскажу</b>, как заработать в телеге 150к+ с нуля за месяц и узнать, как тебе масштабироваться ещё больше

Поэтому, давай договоримся:

Ты тщательно изучаешь информацию и относишься к ней максимально серьёзно

Но перед тем как ты получишь материал, ты должен ответить на вопросы, которые определят твой уровень знаний в профессии "Закупщик рекламы"

<b>Изучай, я уверен, тебе понравится</b> 🙌"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Погнали!", callback_data="start_quiz")]
    ])
    photo = FSInputFile(photo_path)
    await bot.send_photo(chat_id=message.chat.id,
                         photo=photo,
                         caption=text,
                         parse_mode=ParseMode.HTML,
                         reply_markup=keyboard)
    await state.clear()

# Обработка нажатия на кнопку "Погнали!"
@dp.callback_query(F.data == "start_quiz")
async def process_start_quiz(callback: types.CallbackQuery, state: FSMContext):
    photo_path = "2.jpg"  # путь ко второй картинке
    text = """🗣: <b>Чтобы начать работать закупщиком, мне нужен стартовый капитал, у меня нет возможности начать...

Правда или Миф?</b>

Как ты думаешь, нужен ли капитал для того, чтобы начать работать закупщиком в Telegram?"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Да", callback_data="q1_yes"),
            InlineKeyboardButton(text="Нет", callback_data="q1_no")
        ]
    ])
    photo = FSInputFile(photo_path)
    await bot.send_photo(chat_id=callback.message.chat.id,
                         photo=photo,
                         caption=text,
                         parse_mode=ParseMode.HTML,
                         reply_markup=keyboard)
    await callback.answer()
    await state.set_state(Quiz.q1)

# Обработка ответа на вопрос 1 ("Да" или "Нет")
@dp.callback_query(F.data.in_(["q1_yes", "q1_no"]))
async def process_q1(callback: types.CallbackQuery, state: FSMContext):
    answer = callback.data  # "q1_yes" или "q1_no"
    await state.update_data(q1=answer)

    # Отправляем вопрос 2 с выбором времени
    photo_path = "3.jpg"  # путь к следующей картинке
    text = "<b>Сколько времени уделяет закупщик работе в день?</b>"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="до 1 часа в день", callback_data="q2_1")],
        [InlineKeyboardButton(text="до 3 - 5 часов в день", callback_data="q2_3_5")],
        [InlineKeyboardButton(text="до 6 - 10 часов в день", callback_data="q2_6_10")]
    ])
    photo = FSInputFile(photo_path)
    await bot.send_photo(chat_id=callback.message.chat.id,
                         photo=photo,
                         caption=text,
                         parse_mode=ParseMode.HTML,
                         reply_markup=keyboard)
    await callback.answer()
    await state.set_state(Quiz.q2)

# Обработка ответа на вопрос 2
@dp.callback_query(F.data.in_(["q2_1", "q2_3_5", "q2_6_10"]))
async def process_q2(callback: types.CallbackQuery, state: FSMContext):
    answer = callback.data
    await state.update_data(q2=answer)

    # Отправляем вопрос 3 с выбором бюджета (варианты 1)
    photo_path = "4.jpg"
    text = """<b>К тебе поступает запрос на создание канала под ключ по тематике женской психологии, но клиент не может определиться с выделением рекламного бюджета</b>

Твоя Задача: 

Определить минимальный порог входа по бюджету в тематике «Женской психологии»"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="от 250к до 350.000кР", callback_data="q3_option1")],
        [InlineKeyboardButton(text="от 500.000₽", callback_data="q3_option2")],
        [InlineKeyboardButton(text="от 1.000.000₽", callback_data="q3_option3")]
    ])
    photo = FSInputFile(photo_path)
    await bot.send_photo(chat_id=callback.message.chat.id,
                         photo=photo,
                         caption=text,
                         parse_mode=ParseMode.HTML,
                         reply_markup=keyboard)
    await callback.answer()
    await state.set_state(Quiz.q3)

# Обработка ответа на вопрос 3
@dp.callback_query(F.data.in_(["q3_option1", "q3_option2", "q3_option3"]))
async def process_q3(callback: types.CallbackQuery, state: FSMContext):
    answer = callback.data
    await state.update_data(q3=answer)

    # Отправляем вопрос 4 с выбором бюджета (варианты 2)
    photo_path = "5.jpg"
    text = """Мне поступил запрос от клиента:

— Нужен пассивный бизнес под ключ. Сказали ты можешь помочь. Есть сумма (Х) — суммы достаточно, чтобы что-нибудь сотворить? 

С этого проекта я заработал - 300.000р 

Вопрос: 

Сколько рекламного бюджета выделил клиент на закуп рекламы?"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="500.000₽", callback_data="q4_option1")],
        [InlineKeyboardButton(text="3.000.000₽", callback_data="q4_option2")],
        [InlineKeyboardButton(text="1.000.000₽", callback_data="q4_option3")]
    ])
    photo = FSInputFile(photo_path)
    await bot.send_photo(chat_id=callback.message.chat.id,
                         photo=photo,
                         caption=text,
                         parse_mode=ParseMode.HTML,
                         reply_markup=keyboard)
    await callback.answer()
    await state.set_state(Quiz.q4)

# Обработка ответа на вопрос 4 с дополнительным сообщением "Неплохо, продолжаем?"
@dp.callback_query(F.data.in_(["q4_option1", "q4_option2", "q4_option3"]))
async def process_q4(callback: types.CallbackQuery, state: FSMContext):
    answer = callback.data
    await state.update_data(q4=answer)

    chat_id = callback.message.chat.id
    text = "Неплохо, продолжаем?"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да, Даееем Газу!!!", callback_data="continue_after_q4")]
    ])
    await bot.send_message(chat_id=chat_id, text=text, reply_markup=keyboard)
    await callback.answer()

# Новый обработчик для кнопки "Да, Даееем Газу!!!"
@dp.callback_query(F.data == "continue_after_q4")
async def process_continue_after_q4(callback: types.CallbackQuery, state: FSMContext):
    chat_id = callback.message.chat.id
    photo_path = "6.jpg"  # путь к нужной картинке
    caption = """<b>Прежде, чем мы перейдем к материалу — ответь на последнюю линейку вопросов</b> 👇

Чтобы помочь тебе стартануть в закупах, я должен тонко понять, с чем ты пришёл.

Все лично, полностью индивидуальный подход. Всё конфиденциально.

Поэтому: очень важно, чтобы ты ответил на вопросы ниже👇

1. Как тебя зовут? Сколько лет? В каком городе живёшь?
2. Чем занимаешься? Работаешь/учишься, расскажи подробнее
3. Сколько зарабатываешь сейчас? Сколько хотел(а) бы зарабатывать?
4. Был ли опыт в том, чтобы начать свой бизнес?

<b>Ответы присылай мне в личку: @Arti_Guru</b>"""
    photo = FSInputFile(photo_path)
    await bot.send_photo(chat_id=chat_id,
                         photo=photo,
                         caption=caption,
                         parse_mode=ParseMode.HTML)
    await callback.answer()
    # Запуск отложенного сообщения
    asyncio.create_task(send_delayed_message(chat_id))
    await state.set_state(Quiz.waiting_for_final)

# Функция для отправки сообщения через 2 минуты
async def send_delayed_message(chat_id: int):
    await asyncio.sleep(2)  # ожидание 2 секунды (при необходимости увеличить время)
    photo_path = "7.jpg"
    text = "Ответы отправлены? Давай сверим правильные ответы!"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да, давай!", callback_data="final_step")]
    ])
    photo = FSInputFile(photo_path)
    await bot.send_photo(chat_id=chat_id,
                         photo=photo,
                         caption=text,
                         parse_mode=ParseMode.HTML,
                         reply_markup=keyboard)

# Обработка нажатия на кнопку "Да, давай!"
@dp.callback_query(F.data == "final_step")
async def process_final_step(callback: types.CallbackQuery, state: FSMContext):
    text = """<b>Правильные ответы 👇</b>

1) Правда ли, что нужен первоначальный капитал, чтобы начать работу закупщиком? 
   Правильный ответ — нет. 
   — Начать работу, выйти на первого клиента и заработать стартовый капитал для дальнейшего масштаба — можно без вложений.

<b>2) Сколько времени уделяет работе закупщик?</b>
   Правильный ответ — до 3 часов в день. Но если закупщик загружен проектами, работа может длиться 24/7. 

<b>3) Какой порог входа в тематику женской психологии?</b>
   Правильный ответ — от 500.000₽. 

<b>4) Какая ценовая политика за услугу «Канал под ключ»?</b>
   Правильный ответ — рыночная процентная политика — 30%. За работу в размере 300.000₽ я реализую бюджет в размере 1.000.000₽.
"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Хочу узнать свой уровень в телеге!", callback_data="show_result")]
    ])
    await bot.send_message(chat_id=callback.message.chat.id,
                           text=text,
                           parse_mode=ParseMode.HTML,
                           reply_markup=keyboard)
    await callback.answer()

# Обработка финальной кнопки и расчёт результатов
@dp.callback_query(F.data == "show_result")
async def process_show_result(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    score = 0
    # Определяем правильные ответы (правильный ответ на вопрос 1 — "Нет")
    correct_answers = {
        'q1': 'q1_no',
        'q2': 'q2_3_5',
        'q3': 'q3_option2',
        'q4': 'q4_option3'
    }
    results_text = "<b>Ваши результаты:</b>\n"

    # Сравниваем ответы пользователя с правильными
    for idx, key in enumerate(['q1', 'q2', 'q3', 'q4'], start=1):
        user_answer = data.get(key, "не ответил")
        if user_answer == correct_answers[key]:
            results_text += f"Вопрос {idx}: Правильно ✅\n"
            score += 1
        else:
            results_text += f"Вопрос {idx}: Неправильно ❌\n"
    results_text += f"\nОбщий результат: {score} из 4\n"

    # Определяем уровень пользователя и описание фото
    if score >= 4:
        level = "ПРОФИ"
        result_photo = "full.jpg"   # Фото для ПРОФИ
        result_file = "Профи.pdf"     # Файл для ПРОФИ
        photo_description = (
            "<b>Привет, профи</b> 👋\n\n"
            "Устал топтаться на месте? Начинай обрабатывать информацию 👇\n\n"
            "— Что если клиент проигнорил\n"
            "— Примеры холодных рассылок\n"
            "— Пример общения по звонку\n"
            "— Как донести ценность ваших услуг\n"
            "— Какими навыками должен обладать профи\n\n"
            "<b>Тогда приступай к изучению👇</b>"
        )
    elif score in [2, 3]:
        level = "ПРОДВИНУТЫЙ"
        result_photo = "middle.jpg"      # Фото для ПРОДВИНУТЫХ
        result_file = "Продвинутый.pdf"    # Файл для ПРОДВИНУТЫХ
        photo_description = (
            "<b>Привет, продвинутый!</b> 👋\n\n"
            "Я думаю, тебе не нужно объяснять, что такое CPM и прочие базовые термины. "
            "Присаживайся поудобнее и дополняй свои знания, чтобы делать первые шаги к ощутимому доходу👇\n\n"
            "Как выглядит работа с клиентом?\n"
            "— Разработка стратегии привлечения трафика\n"
            "— Закупка рекламы и тестирование гипотез\n"
            "— Оптимизация кампаний и масштабирование\n"
            "— Предоставление отчётов и корректировка стратегии\n"
            "— Как удешевлять цену за подписчика\n"
            "— Какими навыками должен обладать закупщик?\n\n"
            "<b>Начинай читать информацию и не забывай применять её на практике</b> 👇"
        )
    else:
        level = "НОВИЧОК"
        result_photo = "new.jpg"      # Фото для НОВИЧКА
        result_file = "Новичок.pdf"   # Файл для НОВИЧКА
        photo_description = (
            "<b>Как заработать в Telegram: Введение для новичков</b>\n\n"
            "Привет! Рад приветствовать тебя в этом разделе. Здесь ты найдёшь полезную информацию, "
            "которая поможет тебе сделать первые шаги к заработку в ТГ. Устраивайся поудобнее — мы начинаем!\n\n"
            "<b>Что такое Telegram?</b>\n"
            "Telegram — это не просто мессенджер, а полноценная социальная сеть, где можно зарабатывать, используя аудиторию.\n\n"
            "Монетизация в Telegram бывает разной:\n"
            "- Продажа рекламы\n"
            "- Продажа товаров и услуг\n"
            "- Другие схемы заработка\n\n"
            "Получай чек-лист и изучай информацию подробнее."
        )

    results_text += f"\nВаш уровень: {level}"

    # 1. Отправляем пользователю сообщение с результатами
    await bot.send_message(chat_id=callback.message.chat.id,
                           text=results_text,
                           parse_mode=ParseMode.HTML)

    # 2. Отправляем фотографию с описанием уровня (caption с HTML-разметкой)
    photo = FSInputFile(result_photo)
    await bot.send_photo(chat_id=callback.message.chat.id,
                         photo=photo,
                         caption=photo_description,
                         parse_mode=ParseMode.HTML)

    # 3. Отправляем соответствующий файл
    document = FSInputFile(result_file)
    await bot.send_document(chat_id=callback.message.chat.id,
                            document=document)

    # 4. Формируем данные о пользователе и его ответах для администратора с читаемыми ответами
    admin_message = f"Новый пользователь:\n" \
                    f"Имя: {callback.from_user.full_name}\n" \
                    f"Username: @{callback.from_user.username}\n" \
                    f"ID: {callback.from_user.id}\n\n" \
                    f"Ответы:\n"
    for question in ['q1', 'q2', 'q3', 'q4']:
        raw_answer = data.get(question)
        readable = ANSWER_TEXTS.get(question, {}).get(raw_answer, "не ответил")
        admin_message += f"Вопрос {question[-1]}: {readable}\n"
    admin_message += f"Баллы: {score} из 4\n" \
                     f"Уровень: {level}"
    await bot.send_message(chat_id=ADMIN_ID, text=admin_message)

    # Завершаем диалог — очищаем данные FSM
    await state.clear()
    await callback.answer()

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
