from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from app.storage import storage


from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from app.storage import storage

def get_tests_keyboard_for_attempt(teacher_id, discipline):
    """
    Создает клавиатуру для выбора теста по дисциплине.
    
    :param teacher_id: ID преподавателя.
    :param discipline: Название дисциплины.
    :return: InlineKeyboardMarkup с кнопками для выбора теста.
    """
    # Получаем тесты для дисциплины
    tests = storage.get_tests(teacher_id, discipline)
    buttons = []

    # Создаем кнопки для каждого теста
    for test in tests:
        buttons.append([InlineKeyboardButton(
            text=test,  # Название теста
            callback_data=f"select_test_for_attempt:{test}"  # Данные для callback
        )])

    # Кнопка "Назад" (если нужно вернуться к выбору дисциплины)
    buttons.append([InlineKeyboardButton(text="Назад", callback_data=f"back_to_disciplines:{teacher_id}")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_disciplines_keyboard_for_attempt(teacher_id):
    """
    Создает клавиатуру для выбора дисциплины преподавателя.
    
    :param teacher_id: ID преподавателя.
    :return: InlineKeyboardMarkup с кнопками для выбора дисциплины.
    """
    # Получаем дисциплины преподавателя
    disciplines = storage.get_disciplines(teacher_id)
    buttons = []

    # Создаем кнопки для каждой дисциплины
    for discipline in disciplines:
        buttons.append([InlineKeyboardButton(
            text=discipline,  # Название дисциплины
            callback_data=f"select_discipline_for_attempt:{discipline}"  # Данные для callback
        )])

    # Убираем кнопку "Назад"
    # buttons.append([InlineKeyboardButton(text="Назад", callback_data="back_to_teacher_input")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_question_keyboard(user_id, test_name, question_index, total_questions):
    """
    Создает клавиатуру для навигации по вопросам теста и выбора ответов.
    
    :param user_id: ID пользователя.
    :param test_name: Название теста.
    :param question_index: Индекс текущего вопроса.
    :param total_questions: Общее количество вопросов в тесте.
    :return: InlineKeyboardMarkup с кнопками навигации и ответами.
    """
    # Получаем текущий вопрос
    questions = storage.get_questions(user_id, test_name)
    question = questions[question_index]
    answers = question.get("answers", [])

    buttons = []

    # Кнопки для выбора ответов
    for i, answer in enumerate(answers):
        buttons.append([InlineKeyboardButton(text=f"{i + 1}. {answer}", callback_data=f"select_answer:{test_name}:{question_index}:{i}")])

    # Кнопки для навигации
    nav_buttons = []
    if question_index > 0:
        nav_buttons.append(InlineKeyboardButton(text="← Предыдущий вопрос", callback_data=f"prev_question:{test_name}:{question_index - 1}"))
    if question_index < total_questions - 1:
        nav_buttons.append(InlineKeyboardButton(text="Следующий вопрос →", callback_data=f"next_question:{test_name}:{question_index + 1}"))

    if nav_buttons:
        buttons.append(nav_buttons)

    # Кнопка "Завершить попытку"
    buttons.append([InlineKeyboardButton(text="Завершить попытку", callback_data=f"finish_attempt:{test_name}")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)