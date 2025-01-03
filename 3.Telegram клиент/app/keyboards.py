from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from app.storage import storage

def get_disciplines_keyboard(user_id):
    """Клавиатура для выбора или создания дисциплины с кнопками переходов."""
    disciplines = storage.get_disciplines(user_id)
    buttons = [
        [InlineKeyboardButton(text=d, callback_data=f"discipline:{d}")] for d in disciplines
    ]
    buttons.append([InlineKeyboardButton(text="Создать новую дисциплину", callback_data="create_discipline")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_tests_keyboard(user_id, discipline):
    """Клавиатура для выбора или создания теста с кнопками переходов."""
    tests = storage.get_tests(user_id, discipline)
    buttons = [
        [InlineKeyboardButton(text=t, callback_data=f"test:{t}")] for t in tests
    ]
    buttons.append([InlineKeyboardButton(text="Создать новый тест", callback_data="create_test")])
    buttons.append([
            InlineKeyboardButton(text="Сохранить тесты", callback_data="save_tests"),
            InlineKeyboardButton(text="Очистить тесты", callback_data="clear_tests")
        ])
    buttons.append([
        InlineKeyboardButton(text="Перейти к дисциплинам", callback_data="go_to_disciplines"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_questions_keyboard(user_id, test):
    """Клавиатура для выбора или создания вопросов в тесте с кнопками переходов."""
    questions = storage.get_questions(user_id, test)
    buttons = [
        [InlineKeyboardButton(text=q, callback_data=f"question:{q}")] for q in questions
    ]
    buttons.append([InlineKeyboardButton(text="Создать новый вопрос", callback_data="create_question")])
    # Кнопки переходов
    buttons.append([
        InlineKeyboardButton(text="Перейти в тесты", callback_data="go_to_tests"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_answer_selection_keyboard(user_id):
    """Клавиатура для выбора правильного ответа из предложенных."""
    answers = storage.get_answers(user_id)
    buttons = [
        [InlineKeyboardButton(text=answer, callback_data=f"set_correct_answer:{answer}")] for answer in answers
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_answers_keyboard(user_id, question):
    """Клавиатура для управления ответами к текущему вопросу."""
    answers = storage.get_answers_for_question(user_id, question)
    buttons = [
        [InlineKeyboardButton(text=answer, callback_data=f"edit_answer:{answer}")]
        for answer in answers
    ]
    buttons.append([InlineKeyboardButton(text="Добавить новый ответ", callback_data="create_answer")])
    buttons.append([
        InlineKeyboardButton(text="Перейти к вопросам", callback_data="go_to_questions"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
