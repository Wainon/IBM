from aiogram import Router, types
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.keyboards import (
    get_disciplines_keyboard, 
    get_tests_keyboard, 
    get_questions_keyboard, 
    get_answers_keyboard,
    get_answer_selection_keyboard
)
# from app.keyboardsforAttempt import get_disciplines_keyboard_for_attempt
from app.storage import storage
import aiohttp
import json
router = Router()

@router.message(Command(commands=["start"]))
async def start_command(message: Message):
    user_id = message.from_user.id
    storage.initialize_user(user_id)
    await message.answer(
        "Добро пожаловать! Это бот для создания тестов внутри мессенджера телеграмм\nПожалуйста, авторизуйтесь, чтобы продолжить. Введите команду /login",
    )

@router.message(Command(commands=["create"]))
async def create_command(message: Message):
    user_id = message.from_user.id
    await message.answer(
        "Выберите дисциплину или создайте новую:",
        reply_markup=get_disciplines_keyboard(user_id)
    )

@router.message(Command(commands=["help"]))
async def help_command(message: types.Message):
    help_text = (
        "🤖 **Доступные команды:**\n\n"
        "▶️ `/start` - Запуск бота\n"
        "🔑 `/login` - Авторизуйтесь, чтобы получить доступ к функциям бота\n"
        "📚 `/create` - Начните создание дисциплин (доступно после авторизации)\n"
        "🔢 `/code <код>` - Введите код доступа для авторизации\n\n"
        "Если у вас возникли вопросы, обратитесь к администратору."
    )

    # Создаем интерактивные кнопки
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="Запуск бота", callback_data="start"))
    builder.add(types.InlineKeyboardButton(text="Авторизация", callback_data="login"))
    builder.add(types.InlineKeyboardButton(text="Создать дисциплину", callback_data="create"))
    builder.adjust(2)  # Группируем кнопки по 2 в строке

    await message.answer(help_text, parse_mode="Markdown", reply_markup=builder.as_markup())
    
@router.message(Command(commands=["code"]))
async def process_code_input(message: Message):
    chat_id = message.chat.id
    code = message.text.split()[1]  # Получаем код из команды

    # Проверяем, что код состоит из 6 цифр
    if not code.isdigit() or len(code) != 6:
        await message.answer("Код должен состоять из 6 цифр. Пожалуйста, введите код еще раз.")
        return

    # Вызываем функцию code_auth с полученным кодом
    status_auth = f"http://localhost/botTelegramLogic/codeinput?chat_id={chat_id}&code={code}"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(status_auth) as response:
                if response.status == 200:
                    try:
                        json_response = await response.json()
                        auth_state = json_response.get("auth")
                        if auth_state == "success":
                            print(f"auth state: {auth_state}")
                            await message.answer("Авторизация успешна, продолжите вход на другом устройстве")
                        else:
                            await message.answer("Начните процесс авторизации заново. Авторизация провалена")
                            print("не удалось извлечь auth_state")
                    except ValueError:
                        print("Ошибка: ответ не является корректным JSON.")
                else:
                    print(f"Ошибка при получении данных. Статус: {response.status}")

        except aiohttp.ClientError as e:
            await message.answer(f"Ошибка при выполнении запроса: {str(e)}")

@router.callback_query()
async def callback_handler(callback_query: CallbackQuery):
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
    elif action == "edit_discipline":
        storage.set_user_state(user_id, "waiting_for_discipline_to_edit")
        await callback_query.message.edit_text(
            "Выберите дисциплину для изменения названия:",
            reply_markup=get_disciplines_keyboard(user_id, edit_mode=True)
        )
    elif action == "select_discipline_to_edit":
        discipline = data[1]
        storage.set_user_state(user_id, f"waiting_for_new_discipline_name:{discipline}")
        await callback_query.message.edit_text(
            f"Вы выбрали дисциплину '{discipline}'. Напишите новое название для этой дисциплины:"
        )

    elif action == "test":
        test = data[1]  # Извлекаем название теста
        storage.set_current_test(user_id, test)  # Сохраняем текущий тест
        print(f"DEBUG: Текущий тест сохранен: {test}")  # Отладочное сообщение
        await callback_query.message.edit_text(
            f"Вы выбрали тест: {test}. Выберите вопрос:",
            reply_markup=get_questions_keyboard(user_id, test)
        )
    elif action == "create_question":
        current_test = storage.get_current_test(user_id)  # Получаем текущий тест
        print(f"DEBUG: Текущий тест: {current_test}")  # Отладочное сообщение

        if current_test:
            question_count = len(storage.get_questions(user_id, current_test)) + 1  # Считаем количество вопросов
            storage.set_user_state(user_id, "waiting_for_question_text")  # Устанавливаем состояние
            await callback_query.message.edit_text(
                f"Введите вопрос {question_count} для теста {current_test}."
            )
        else:
            print("DEBUG: Текущий тест не найден!")  # Отладочное сообщение
            await callback_query.answer("Сначала выберите тест!", show_alert=True)
    elif action == "create_discipline":
        storage.set_user_state(user_id, "waiting_for_discipline_name")
        await callback_query.message.edit_text("Напишите название новой дисциплины:")
    elif action == "create_test":    
        storage.set_user_state(user_id, "waiting_for_test_name")  # Устанавливаем состояние
        await callback_query.message.edit_text("Напишите название нового теста:")
    await callback_query.answer()  # Не забудьте ответить на callback_query


@router.message()
async def text_handler(message: Message):
    user_id = message.from_user.id
    state = storage.get_user_state(user_id)

    state = storage.get_user_state(user_id)
    if state is None:
        await message.answer("Нет такой команды")
        return

    if state == "waiting_for_discipline_name":
        discipline_name = message.text.strip()
        storage.add_discipline(user_id, discipline_name)
        await message.answer(
            f"Дисциплина '{discipline_name}' успешно создана. Выберите ее или создайте новую:",
            reply_markup=get_disciplines_keyboard(user_id)
        )
        storage.clear_user_state(user_id)
    elif state.startswith("waiting_for_new_discipline_name:"):
        old_discipline = state.split(":")[1]
        new_discipline_name = message.text.strip()
        storage.rename_discipline(user_id, old_discipline, new_discipline_name)
        await message.answer(
            f"Название дисциплины '{old_discipline}' изменено на '{new_discipline_name}'.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Перейти к дисциплинам", callback_data="go_to_disciplines")]
            ])
        )
        storage.clear_user_state(user_id)
    elif state == "waiting_for_test_name":
        test_name = message.text.strip()
        discipline = storage.get_current_discipline(user_id)  # Получаем текущую дисциплину
        print(f"Текущая дисциплина: {discipline}")  # Отладочное сообщение
        if discipline:  # Проверяем, что дисциплина установлена
            storage.add_test(user_id, discipline, test_name)  # Добавляем тест
            await message.answer(
                f"Тест '{test_name}' для дисциплины '{discipline}' успешно создан. Выберите его или создайте новый:",
                reply_markup=get_tests_keyboard(user_id, discipline)
            )
            storage.clear_user_state(user_id)  # Очищаем состояние после обработки
        else:
            await message.answer("Сначала выберите дисциплину.")
    elif state == "waiting_for_question_text":
        test = storage.get_current_test(user_id)
        question_text = message.text.strip()
        storage.add_question(user_id, test, question_text)
        storage.set_user_state(user_id, "waiting_for_answer_count")
        await message.answer(
            f"Введите количество вариантов ответа для вопроса '{question_text}'."
        )

    elif state == "waiting_for_answer_count":
        try:
            answer_count = int(message.text.strip())
            storage.set_answer_count(user_id, answer_count)  # Добавьте метод в Storage
            storage.set_user_state(user_id, f"waiting_for_answer_text:1:{answer_count}")
            await message.answer(f"Введите ответ 1.")
        except ValueError:
            await message.answer("Пожалуйста, введите числовое значение.")

    elif state.startswith("waiting_for_answer_text:"):
        _, current, total = state.split(":")
        current = int(current)
        total = int(total)
        answer_text = message.text.strip()
        storage.add_answer(user_id, answer_text)  # Добавьте метод в Storage

        if current < total:
            storage.set_user_state(user_id, f"waiting_for_answer_text:{current + 1}:{total}")
            await message.answer(f"Введите ответ {current + 1}.")
        else:
            storage.set_user_state(user_id, "waiting_for_correct_answer")
            await message.answer(
                "Введите номер правильного ответа или выберите его:",
                reply_markup=get_answer_selection_keyboard(user_id)
            )

    elif state == "waiting_for_correct_answer":
        correct_answer = message.text.strip()
        answers = storage.get_answers(user_id)
        
        if correct_answer in answers:
            storage.set_correct_answer(user_id, correct_answer)
            test = storage.get_current_test(user_id)
            await message.answer(
                f"Вы выбрали правильный ответ '{correct_answer}'.",
                reply_markup=go_to_questions_keyboard(user_id, test)
            )
            # Не очищаем состояние полностью, только удаляем ключ 'state'
            if user_id in storage.user_states:
                storage.user_states[user_id].pop('state', None)
        else:
            await message.answer(
                f"Ответ '{correct_answer}' не найден среди вариантов. Пожалуйста, выберите существующий ответ."
            )
    elif action.startswith("set_correct_answer:"):
        correct_answer = action.split(":")[1]
        storage.set_correct_answer(user_id, correct_answer)  # Добавьте метод в Storage
        test = storage.get_current_test(user_id)
        await callback_query.message.edit_text(
            f"Вы выбрали правильный ответ '{correct_answer}'.",
            reply_markup=go_to_questions_keyboard(user_id, test)
        )
        storage.clear_user_state(user_id)

