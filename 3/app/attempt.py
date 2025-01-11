from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from app.storage import storage
from app.attemptStorage import attempt_storage
from app.keyboardsforAttempt import get_question_keyboard, get_disciplines_keyboard_for_attempt
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

attempt_router = Router()

@attempt_router.message(lambda message: storage.get_user_state(message.from_user.id) and storage.get_user_state(message.from_user.id).startswith("waiting_for_discipline:"))
async def select_discipline(message: Message):
    user_id = message.from_user.id
    state = storage.get_user_state(user_id)
    teacher_id = state.split(":")[1]  # Получаем teacher_id из состояния
    discipline = message.text.strip()

    # Проверяем, что дисциплина существует
    disciplines = storage.get_disciplines(teacher_id)
    if discipline not in disciplines:
        await message.answer("Дисциплина не найдена. Пожалуйста, выберите дисциплину из списка.")
        return

    # Получаем тесты для выбранной дисциплины
    tests = storage.get_tests(teacher_id, discipline)
    if not tests:
        await message.answer(f"В дисциплине '{discipline}' нет тестов.")
        return

    # Создаем reply-кнопки для тестов
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=test)] for test in tests
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    # Устанавливаем состояние "выбор теста"
    storage.set_user_state(user_id, f"waiting_for_test:{teacher_id}:{discipline}")

    # Отображаем список тестов
    await message.answer(
        f"Выберите тест по дисциплине '{discipline}':",
        reply_markup=keyboard
    )


@attempt_router.message(lambda message: storage.get_user_state(message.from_user.id) and storage.get_user_state(message.from_user.id).startswith("waiting_for_test:"))
async def select_test(message: Message):
    user_id = message.from_user.id
    state = storage.get_user_state(user_id)
    _, teacher_id, discipline = state.split(":")  # Получаем teacher_id и дисциплину из состояния
    test_name = message.text.strip()

    # Проверяем, что тест существует
    tests = storage.get_tests(teacher_id, discipline)
    if test_name not in tests:
        await message.answer("Тест не найден. Пожалуйста, выберите тест из списка.")
        return

    # Получаем вопросы для теста
    questions = storage.get_questions_for_attempt(teacher_id, test_name)
    if not questions:
        await message.answer(f"В тесте '{test_name}' нет вопросов.")
        return

    # Устанавливаем состояние "прохождение теста"
    storage.set_user_state(user_id, f"taking_test:{teacher_id}:{discipline}:{test_name}")

    # Начинаем показ вопросов
    storage.set_current_question_index(user_id, 0)  # Устанавливаем индекс текущего вопроса
    await show_question(message, user_id, teacher_id, test_name, 0)

async def show_question(message: Message, user_id: int, teacher_id: int, test_name: str, question_index: int):
    # Получаем текущий вопрос
    questions = storage.get_questions(teacher_id, test_name)
    question = questions[question_index]

    # Создаем reply-кнопки для ответов
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=answer)] for answer in question.get("answers", [])
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    # Отображаем вопрос и кнопки с ответами
    await message.answer(
        f"Вопрос {question_index + 1}: {question['text']}",
        reply_markup=keyboard
    )

@attempt_router.message(lambda message: storage.get_user_state(message.from_user.id) and storage.get_user_state(message.from_user.id).startswith("taking_test:"))
async def answer_question(message: Message):
    user_id = message.from_user.id
    state = storage.get_user_state(user_id)
    _, teacher_id, discipline, test_name = state.split(":")  # Получаем данные из состояния
    answer = message.text.strip()

    # Получаем текущий вопрос
    questions = storage.get_questions(teacher_id, test_name)
    question_index = storage.get_current_question_index(user_id)
    current_question = questions[question_index]

    # Сохраняем ответ
    storage.save_user_answer(user_id, test_name, question_index, answer)

    # Переходим к следующему вопросу
    next_question_index = question_index + 1
    if next_question_index < len(questions):
        storage.set_current_question_index(user_id, next_question_index)
        await show_question(message, user_id, teacher_id, test_name, next_question_index)
    else:
        # Завершаем тест
        storage.clear_user_state(user_id)
        await message.answer(
            f"Тест '{test_name}' завершен. Спасибо за участие!",
            reply_markup=ReplyKeyboardRemove()  # Убираем reply-кнопки
        )