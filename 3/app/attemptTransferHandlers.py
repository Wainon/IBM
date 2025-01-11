from aiogram import Router
from aiogram.types import CallbackQuery
from app.storage import storage
from app.keyboardsforAttempt import get_question_keyboard

attempt_transfer_router = Router()


@attempt_transfer_router.callback_query(lambda c: c.data.startswith("select_test_for_attempt:"))
async def select_test_for_attempt(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    test_name = callback_query.data.split(":")[1]

    # Получаем teacher_id из сообщения (можно сохранить его в storage или передать в callback_data)
    teacher_id = callback_query.message.text.split()[-1]  # Последнее слово в сообщении — teacher_id

    # Сохраняем текущий тест
    storage.set_current_test(user_id, test_name)

    # Получаем вопросы для теста
    questions = storage.get_questions(teacher_id, test_name)
    total_questions = len(questions)

    # Отображаем первый вопрос и клавиатуру с ответами
    await callback_query.message.edit_text(
        f"Вопрос 1: {questions[0]['text']}",
        reply_markup=get_question_keyboard(user_id, test_name, 0, total_questions)
    )

@attempt_transfer_router.callback_query(lambda c: c.data.startswith("prev_question:"))
async def prev_question(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    test_name = callback_query.data.split(":")[1]
    question_index = int(callback_query.data.split(":")[2])

    # Получаем вопросы для теста
    questions = storage.get_questions(user_id, test_name)
    total_questions = len(questions)

    # Отображаем предыдущий вопрос и клавиатуру с ответами
    await callback_query.message.edit_text(
        f"Вопрос {question_index + 1}: {questions[question_index]['text']}",
        reply_markup=get_question_keyboard(user_id, test_name, question_index, total_questions)
    )
@attempt_transfer_router.callback_query(lambda c: c.data.startswith("select_answer:"))
async def select_answer(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    test_name = callback_query.data.split(":")[1]
    question_index = int(callback_query.data.split(":")[2])
    answer_index = int(callback_query.data.split(":")[3])

    # Получаем текущий вопрос
    questions = storage.get_questions(user_id, test_name)
    question = questions[question_index]
    answers = question.get("answers", [])

    # Сохраняем выбранный ответ
    storage.save_user_answer(user_id, test_name, question_index, answer_index)

    # Уведомляем студента о выборе ответа
    await callback_query.answer(f"Вы выбрали ответ: {answers[answer_index]}")

    # Переходим к следующему вопросу (если он есть)
    total_questions = len(questions)
    if question_index < total_questions - 1:
        await callback_query.message.edit_text(
            f"Вопрос {question_index + 2}: {questions[question_index + 1]['text']}",
            reply_markup=get_question_keyboard(user_id, test_name, question_index + 1, total_questions)
        )
    else:
        await callback_query.message.edit_text(
            "Вы ответили на все вопросы. Нажмите 'Завершить попытку', чтобы завершить тест."
        )

@attempt_transfer_router.callback_query(lambda c: c.data.startswith("next_question:"))
async def next_question(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    test_name = callback_query.data.split(":")[1]
    question_index = int(callback_query.data.split(":")[2])

    # Получаем вопросы для теста
    questions = storage.get_questions(user_id, test_name)
    total_questions = len(questions)

    # Отображаем следующий вопрос
    await callback_query.message.edit_text(
        f"Вопрос {question_index + 1}: {questions[question_index]['text']}",
        reply_markup=get_question_keyboard(user_id, test_name, question_index, total_questions)
    )

@attempt_transfer_router.callback_query(lambda c: c.data.startswith("finish_attempt:"))
async def finish_attempt(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    test_name = callback_query.data.split(":")[1]

    # Здесь можно добавить логику подсчета результатов
    await callback_query.message.edit_text(
        f"Попытка завершена. Спасибо за прохождение теста '{test_name}'!"
    )