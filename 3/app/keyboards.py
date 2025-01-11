from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from app.storage import storage

def get_disciplines_keyboard(user_id, edit_mode=False):
    """Клавиатура для выбора дисциплины."""
    disciplines = storage.get_disciplines(user_id)
    buttons = [
        [InlineKeyboardButton(text=d, callback_data=f"select_discipline_to_edit:{d}" if edit_mode else f"discipline:{d}")]
        for d in disciplines
    ]
    if edit_mode:
        buttons.append([InlineKeyboardButton(text="Отмена", callback_data="go_to_disciplines")])
    else:  
        buttons.append([InlineKeyboardButton(text="Создать новую дисциплину", callback_data="create_discipline")])
        buttons.append([InlineKeyboardButton(text="Изменить название дисциплины", callback_data="edit_discipline")])
        buttons.append([
            InlineKeyboardButton(text="Удалить дисциплину", callback_data="delete_discipline"),
            InlineKeyboardButton(text="Очистить дисциплины", callback_data="clear_disciplines")
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_tests_keyboard(user_id, discipline):
    """Клавиатура для выбора или создания теста с кнопками переходов."""
    tests = storage.get_tests(user_id, discipline)
    print(f"Tests for user {user_id} in discipline {discipline}:", tests)
    buttons = [
        [InlineKeyboardButton(text=t, callback_data=f"test:{t}")] for t in tests
    ]
    buttons.append([InlineKeyboardButton(text="Создать новый тест", callback_data="create_test")])
    buttons.append([
        InlineKeyboardButton(text="Сохранить тесты", callback_data="save_tests"),
        InlineKeyboardButton(text="Удалить тест", callback_data="delete_test"),
        InlineKeyboardButton(text="Очистить тесты", callback_data="clear_tests")
    ])
    buttons.append([
        InlineKeyboardButton(text="Перейти к дисциплинам", callback_data="go_to_disciplines"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_questions_keyboard(user_id, test):
    """Клавиатура для выбора вопросов."""
    questions = storage.get_questions(user_id, test)  # Получаем вопросы
    print(f"DEBUG: Вопросы для теста '{test}': {questions}")  # Отладочное сообщение
    buttons = [
        [InlineKeyboardButton(text=q["text"], callback_data=f"question:{index}")]
        for index, q in enumerate(questions)  # Используем индекс вопроса
    ]
    buttons.append([InlineKeyboardButton(text="Создать новый вопрос", callback_data="create_question")])
    buttons.append([
        InlineKeyboardButton(text="Удалить вопрос", callback_data="delete_question"),
        InlineKeyboardButton(text="Очистить вопросы", callback_data="clear_questions")
    ])
    buttons.append([InlineKeyboardButton(text="Перейти в тесты", callback_data="go_to_tests")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_answers_keyboard(user_id, question_index):
    """Клавиатура для просмотра ответов к текущему вопросу."""
    current_test = storage.get_current_test(user_id)  # Получаем текущий тест
    questions = storage.get_questions(user_id, current_test)  # Получаем вопросы для теста
    if questions and 0 <= question_index < len(questions):  # Проверяем, что индекс корректен
        question = questions[question_index]  # Получаем текущий вопрос
        answers = question.get("answers", [])  # Получаем ответы для вопроса
        buttons = [
            [InlineKeyboardButton(text=answer, callback_data=f"view_answer:{answer}")]
            for answer in answers
        ]
        # Кнопка для возврата к вопросам
        buttons.append([
            InlineKeyboardButton(text="Назад к вопросам", callback_data="go_to_questions"),
        ])
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    return InlineKeyboardMarkup(inline_keyboard=[])  # Возвращаем пустую клавиатуру, если вопрос не найден
    
def get_answer_selection_keyboard(user_id):
    """Клавиатура для выбора правильного ответа из предложенных."""
    answers = storage.get_answers(user_id)
    buttons = [
        [InlineKeyboardButton(text=answer, callback_data=f"set_correct_answer:{answer}")] for answer in answers
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def go_to_questions_keyboard(user_id, test):
    """Клавиатура для перехода к вопросам."""
    buttons = [
        [InlineKeyboardButton(text="Перейти к вопросам", callback_data="go_to_questions")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def auth_keyboard():
    """
    Создаёт клавиатуру для выбора метода авторизации.
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Авторизация через GitHub", callback_data="auth_git"),
            InlineKeyboardButton(text="Авторизация через Яндекс ID", callback_data="auth_yndex"),
        ],
        [
            InlineKeyboardButton(text="Авторизация через код (JWT)", callback_data="auth_code")
        ]
    ])
    return keyboard

def get_personal_account_keyboard():
    """
    Клавиатура для личного кабинета.
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Выйти из аккаунта", callback_data="exit_status")],
        [InlineKeyboardButton(text="Сменить имя", callback_data="change_name")],
        [InlineKeyboardButton(text="Перейти к дисциплинам", callback_data="go_to_disciplines")]
    ])