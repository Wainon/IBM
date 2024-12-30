from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from app.keyboards import (
    get_disciplines_keyboard, 
    get_tests_keyboard, get_questions_keyboard, 
    get_answer_selection_keyboard )
from app.storage import storage

router = Router()

@router.callback_query(lambda c: c.data == "go_to_disciplines")
async def go_to_disciplines(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    keyboard = get_disciplines_keyboard(user_id)
    await callback_query.message.edit_text(
        "Выберите дисциплину или создайте новую:",
        reply_markup=keyboard
    )

@router.callback_query(lambda c: c.data == "go_to_tests")
async def go_to_tests(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    current_discipline = storage.get_current_discipline(user_id)
    if current_discipline:
        keyboard = get_tests_keyboard(user_id, current_discipline)
        await callback_query.message.edit_text(
            f"Тесты для дисциплины '{current_discipline}':",
            reply_markup=keyboard
        )
    else:
        await callback_query.answer("Сначала выберите дисциплину!", show_alert=True)

@router.callback_query(lambda c: c.data == "go_to_questions")
async def go_to_questions(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    current_test = storage.get_current_test(user_id)
    if current_test:
        keyboard = get_questions_keyboard(user_id, current_test)
        await callback_query.message.edit_text(
            f"Вопросы для теста '{current_test}':",
            reply_markup=keyboard
        )
    else:
        await callback_query.answer("Сначала выберите тест!", show_alert=True)

@router.callback_query(lambda c: c.data.startswith("set_correct_answer:"))
async def set_correct_answer_callback(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    correct_answer = callback_query.data.split(":")[1]

    # Проверяем, что правильный ответ в списке ответов
    if correct_answer in storage.get_answers(user_id):
        storage.set_correct_answer(user_id, correct_answer)
        await callback_query.message.edit_text(
            f"Правильный ответ '{correct_answer}' сохранен.",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Перейти к вопросам", callback_data="go_to_questions")]
                ]
            )
        )
        storage.clear_user_state(user_id)
    else:
        await callback_query.answer("Этот ответ не найден среди предложенных!", show_alert=True)

@router.callback_query(lambda c: c.data == "save_tests")
async def save_tests(callback_query: CallbackQuery):
    """Обработка нажатия кнопки сохранения тестов."""
    storage.save_data()  # Сохраняем все данные пользователей
    await callback_query.answer("Данные успешно сохранены!")

@router.callback_query(lambda c: c.data == "clear_tests")
async def clear_tests(callback_query: CallbackQuery):
    """Обработка нажатия кнопки очистки тестов."""
    user_id = callback_query.from_user.id
    storage.clear_tests(user_id)  # Очищаем тесты для конкретного пользователя
    await callback_query.answer("Все тесты успешно очищены!")

    
@router.message(Command(commands=["start"]))
async def start_command(message: Message):
    """Обработка команды /start."""
    user_id = message.from_user.id
    storage.initialize_user(user_id)  # Инициализируем пользователя
    await message.answer(
        "Добро пожаловать! Выберите дисциплину или создайте новую:",
        reply_markup=get_disciplines_keyboard(user_id)
    )
    
@router.callback_query()
async def callback_handler(callback_query: CallbackQuery):
    """Обработка нажатий на inline-кнопки."""
    user_id = callback_query.from_user.id
    data = callback_query.data.split(":")
    action = data[0]

    if action == "discipline":
        discipline = data[1]
        storage.set_current_discipline(user_id, discipline)
        await callback_query.message.edit_text(
            f"Вы выбрали дисциплину: {discipline}. Выберите тест:",
            reply_markup=get_tests_keyboard(user_id, discipline)
        )
    elif action == "test":
        test = data[1]
        storage.set_current_test(user_id, test)
        await callback_query.message.edit_text(
            f"Вы выбрали тест: {test}. Напишите текст вопроса:",
            reply_markup=get_questions_keyboard(user_id, test)
        )
        storage.set_user_state(user_id, "waiting_for_question_text")  # Устанавливаем состояние "ожидание текста вопроса"
    elif action == "create_discipline":
        # Создание новой дисциплины
        storage.set_user_state(user_id, "waiting_for_discipline_name")
        await callback_query.message.edit_text("Напишите название новой дисциплины:")
    elif action == "create_test":
        # Создание нового теста
        storage.set_user_state(user_id, "waiting_for_test_name")
        await callback_query.message.edit_text("Напишите название нового теста:")
    elif action == "create_question":
        # Создание нового вопроса
        storage.set_user_state(user_id, "waiting_for_question_text")
        await callback_query.message.edit_text("Напишите текст нового вопроса:")
    await callback_query.answer()

@router.message()
async def text_handler(message: Message):
    """Обработка текстовых сообщений."""
    user_id = message.from_user.id
    state = storage.get_user_state(user_id)

    print(f"User state: {state}")  # Отладочный вывод

    if state == "waiting_for_discipline_name":
        discipline_name = message.text.strip()
        storage.add_discipline(user_id, discipline_name)
        await message.answer(
            f"Дисциплина '{discipline_name}' успешно создана. Выберите ее или создайте новую:",
            reply_markup=get_disciplines_keyboard(user_id)
        )
        storage.clear_user_state(user_id)
    elif state == "waiting_for_test_name":
        test_name = message.text.strip()
        discipline = storage.get_current_discipline(user_id)
        storage.add_test(user_id, discipline, test_name)
        await message.answer(
            f"Тест '{test_name}' для дисциплины '{discipline}' успешно создан. Выберите его или создайте новый:",
            reply_markup=get_tests_keyboard(user_id, discipline)
        )
        storage.set_current_test(user_id, test_name)
        storage.clear_user_state(user_id)
    elif state == "waiting_for_question_text":
        question_text = message.text.strip()
        test = storage.get_current_test(user_id)
        if test:
            storage.add_question(user_id, test, question_text)
            await message.answer(f"Вопрос '{question_text}' добавлен в тест '{test}'. Теперь введите количество вариантов ответов.")
            storage.set_user_state(user_id, "waiting_for_answer_count")
        else:
            await message.answer("Сначала выберите тест.")
    elif state == "waiting_for_answer_count":
        try:
            answer_count = int(message.text.strip())
            storage.set_answer_count(user_id, answer_count)
            storage.set_answers(user_id, [])  # Инициализируем пустой список для ответов
            await message.answer("Введите ответ 1:")
            storage.set_user_state(user_id, f"waiting_for_answer_1")
        except ValueError:
            await message.answer("Пожалуйста, введите корректное число.")
    elif state.startswith("waiting_for_answer_"):
        try:
            current_answer_number = int(state.split("_")[-1])
            answers = storage.get_answers(user_id)
            answers.append(message.text.strip())
            storage.set_answers(user_id, answers)

            answer_count = storage.get_answer_count(user_id)
            if current_answer_number < answer_count:
                next_answer_number = current_answer_number + 1
                await message.answer(f"Введите ответ {next_answer_number}:")
                storage.set_user_state(user_id, f"waiting_for_answer_{next_answer_number}")
            else:
                await message.answer(
                    "Все ответы добавлены. Теперь выберите правильный ответ:",
                    reply_markup=get_answer_selection_keyboard(user_id)
                )
                storage.set_user_state(user_id, "waiting_for_correct_answer")
        except ValueError:
            await message.answer("Произошла ошибка. Попробуйте снова.")
    elif state == "waiting_for_correct_answer":

        correct_answer = message.text.strip()

        answers = storage.get_answers(user_id)


        if correct_answer in answers:

            storage.set_correct_answer(user_id, correct_answer)

            await message.answer(

                f"Правильный ответ '{correct_answer}' сохранен.",

                reply_markup=InlineKeyboardMarkup(

                    inline_keyboard=[

                        [InlineKeyboardButton(text="Перейти к вопросам", callback_data="go_to_questions")]

                    ]

                )

            )

            storage.clear_user_state(user_id)

        else:

            await message.answer("Этот ответ не найден среди предложенных! Пожалуйста, выберите правильный ответ через кнопки или введите его снова.")

    # Остальная часть вашего text_handler остается без изменений





