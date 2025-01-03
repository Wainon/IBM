from aiogram import Router
from aiogram.types import CallbackQuery
from app.storage import storage  # Импортируйте ваш storage
from app.keyboards import (  # Импортируйте функции для создания клавиатур
    get_disciplines_keyboard,
    get_tests_keyboard,
    get_questions_keyboard,
    get_answers_keyboard,
    go_to_questions_keyboard
)

def transfers_handlers(router: Router):
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

    @router.callback_query(lambda c: c.data == "go_to_answers")
    async def go_to_answers(callback_query: CallbackQuery):
        """Обработка перехода к ответам для текущего вопроса."""
        user_id = callback_query.from_user.id
        current_question = storage.get_current_question(user_id)  # Получаем текущий вопрос
        if current_question:
            keyboard = get_answers_keyboard(user_id, current_question)
            await callback_query.message.edit_text(
                f"Ответы для вопроса '{current_question}':",
                reply_markup=keyboard
            )
        else:
            await callback_query.answer("Сначала выберите вопрос!", show_alert=True)

    @router.callback_query(lambda c: c.data.startswith("set_correct_answer:"))
    async def set_correct_answer_callback(callback_query: CallbackQuery):
        user_id = callback_query.from_user.id
        correct_answer = callback_query.data.split(":")[1]

        if correct_answer in storage.get_answers(user_id):
            storage.set_correct_answer(user_id, correct_answer)
            
            # Здесь вы должны вызвать функцию с нужными аргументами
            keyboard = go_to_questions_keyboard(user_id, storage.get_current_test(user_id))  # Передайте user_id и test
            
            await callback_query.message.edit_text(
                f"Правильный ответ '{correct_answer}' сохранен.",
                reply_markup=keyboard
            )
            storage.clear_user_state(user_id)
        else:
            await callback_query.answer("Этот ответ не найден среди предложенных!", show_alert=True)

    @router.callback_query(lambda c: c.data == "save_tests")
    async def save_tests(callback_query: CallbackQuery):
        storage.save_data()
        await callback_query.answer("Данные успешно сохранены!")

    @router.callback_query(lambda c: c.data == "clear_tests")
    async def clear_tests(callback_query: CallbackQuery):
        user_id = callback_query.from_user.id
        storage.clear_tests(user_id)
        await callback_query.answer("Все тесты успешно очищены!")