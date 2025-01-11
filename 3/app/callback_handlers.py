from aiogram import Router
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
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
        user_id = callback_query.from_user.id
        current_test = storage.get_current_test(user_id)  # Получаем текущий тест
        print(f"DEBUG: Текущий тест: {current_test}")  # Отладочное сообщение

        current_question_index = storage.get_current_question(user_id)  # Получаем индекс текущего вопроса
        print(f"DEBUG: Текущий индекс вопроса: {current_question_index}")  # Отладочное сообщение

        if current_test and current_question_index is not None:
            questions = storage.get_questions(user_id, current_test)  # Получаем вопросы для теста
            print(f"DEBUG: Вопросы для теста '{current_test}': {questions}")  # Отладочное сообщение

            if questions and 0 <= current_question_index < len(questions):  # Проверяем, что индекс корректен
                question = questions[current_question_index]  # Получаем текущий вопрос
                print(f"DEBUG: Текущий вопрос: {question}")  # Отладочное сообщение

                answers = question.get("answers", [])  # Получаем ответы для вопроса
                print(f"DEBUG: Ответы для вопроса: {answers}")  # Отладочное сообщение

                if answers:
                    keyboard = get_answers_keyboard(user_id, current_question_index)  # Получаем клавиатуру с ответами
                    print(f"DEBUG: Клавиатура с ответами: {keyboard}")  # Отладочное сообщение

                    await callback_query.message.edit_text(
                        f"Ответы для вопроса '{question['text']}':",
                        reply_markup=keyboard
                    )
                else:
                    print("DEBUG: Для этого вопроса нет ответов.")  # Отладочное сообщение
                    await callback_query.answer("Для этого вопроса нет ответов.", show_alert=True)
            else:
                print(f"DEBUG: Вопрос не найден! Индекс: {current_question_index}, всего вопросов: {len(questions)}")  # Отладочное сообщение
                await callback_query.answer("Вопрос не найден!", show_alert=True)
        else:
            print("DEBUG: Текущий тест или вопрос не установлен.")  # Отладочное сообщение
            await callback_query.answer("Сначала выберите тест и вопрос!", show_alert=True)

    @router.callback_query(lambda c: c.data.startswith("set_correct_answer:"))
    async def set_correct_answer_callback(callback_query: CallbackQuery):
        user_id = callback_query.from_user.id
        correct_answer = callback_query.data.split(":")[1]

        if correct_answer in storage.get_answers(user_id):
            storage.set_correct_answer(user_id, correct_answer)
            
            # Получаем текущий тест
            current_test = storage.get_current_test(user_id)
            if current_test:
                # Передаем текущий тест в функцию go_to_questions_keyboard
                keyboard = go_to_questions_keyboard(user_id, current_test)
                
                await callback_query.message.edit_text(
                    f"Правильный ответ '{correct_answer}' сохранен.",
                    reply_markup=keyboard
                )
                # Очищаем только состояние, оставляя текущий тест
                if user_id in storage.user_states:
                    storage.user_states[user_id].pop('state', None)
            else:
                await callback_query.answer("Текущий тест не найден!", show_alert=True)
        else:
            await callback_query.answer("Этот ответ не найден среди предложенных!", show_alert=True)

    @router.callback_query(lambda c: c.data == "save_tests")
    async def save_tests(callback_query: CallbackQuery):
        storage.save_data()
        await callback_query.answer("Данные успешно сохранены!")

    @router.callback_query(lambda c: c.data == "clear_tests")
    async def clear_tests_callback(callback_query: CallbackQuery):
        user_id = callback_query.from_user.id
        discipline = storage.get_current_discipline(user_id)  # Получаем текущую дисциплину
        if discipline:
            storage.clear_tests(user_id, discipline)  # Передаем и user_id, и discipline
            await callback_query.answer("Все тесты успешно очищены!")
            await callback_query.message.edit_text(
                f"Тесты для дисциплины '{discipline}' очищены.",
                reply_markup=get_tests_keyboard(user_id, discipline)
            )
        else:
            await callback_query.answer("Сначала выберите дисциплину!", show_alert=True)

    @router.callback_query(lambda c: c.data.startswith("question:"))
    async def select_question(callback_query: CallbackQuery):
        user_id = callback_query.from_user.id
        question_index = int(callback_query.data.split(":")[1])  # Извлекаем индекс вопроса
        print(f"DEBUG: Выбран индекс вопроса: {question_index}")  # Отладочное сообщение

        # Получаем текущий тест
        current_test = storage.get_current_test(user_id)
        print(f"DEBUG: Текущий тест: {current_test}")  # Отладочное сообщение

        # Получаем вопросы для текущего теста
        questions = storage.get_questions(user_id, current_test)
        print(f"DEBUG: Вопросы для теста: {questions}")  # Отладочное сообщение

        # Проверяем, что индекс вопроса корректен
        if questions and 0 <= question_index < len(questions):
            question = questions[question_index]  # Получаем вопрос по индексу
            print(f"DEBUG: Выбран вопрос: {question}")  # Отладочное сообщение

            # Получаем ответы для вопроса
            answers = question.get("answers", [])
            correct_answer = question.get("correct_answer")  # Получаем правильный ответ
            print(f"DEBUG: Ответы для вопроса: {answers}")  # Отладочное сообщение
            print(f"DEBUG: Правильный ответ: {correct_answer}")  # Отладочное сообщение

            if answers:
                # Формируем текст с ответами, помечая правильный ответ символом &
                answers_text = "\n".join([
                    f"{i + 1}. {'✅ ' if answer == correct_answer else ''}{answer}"
                    for i, answer in enumerate(answers)
                ])
                message_text = (
                    f"Вопрос: {question['text']}\n\n"
                    f"Ответы:\n{answers_text}"
                )

                # Создаем клавиатуру с кнопкой для возврата к вопросам
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="Назад к вопросам", callback_data="go_to_questions")]
                ])

                # Редактируем сообщение, чтобы показать ответы
                await callback_query.message.edit_text(
                    message_text,
                    reply_markup=keyboard
                )
            else:
                # Если ответов нет, показываем сообщение
                await callback_query.answer("Для этого вопроса нет ответов.", show_alert=True)
        else:
            # Если вопрос не найден, показываем сообщение
            print(f"DEBUG: Вопрос не найден! Индекс: {question_index}, всего вопросов: {len(questions)}")  # Отладочное сообщение
            await callback_query.answer("Вопрос не найден!", show_alert=True)
        
    @router.callback_query(lambda c: c.data == "create_question")
    async def create_question(callback_query: CallbackQuery):
        user_id = callback_query.from_user.id
        current_test = storage.get_current_test(user_id)  # Получаем текущий тест
        if current_test:
            question_count = len(storage.get_questions(user_id, current_test)) + 1  # Считаем количество вопросов
            storage.set_user_state(user_id, "waiting_for_question_text")  # Устанавливаем состояние
            await callback_query.message.edit_text(
                f"Введите вопрос {question_count} для теста {current_test}."
            )
        else:
            await callback_query.answer("Сначала выберите тест!", show_alert=True)

    @router.callback_query(lambda c: c.data.startswith("test:"))
    async def select_test(callback_query: CallbackQuery):
        user_id = callback_query.from_user.id
        test_name = callback_query.data.replace("test:", "")  # Извлекаем название теста
        storage.set_current_test(user_id, test_name)  # Сохраняем текущий тест
        print(f"DEBUG: Текущий тест сохранен для пользователя {user_id}: {test_name}")  # Отладочное сообщение


        # Обновляем интерфейс (переход к вопросам)
        keyboard = get_questions_keyboard(user_id, test_name)  # Клавиатура для вопросов
        await callback_query.message.edit_text(
            f"Выбран тест: {test_name}. Переход к вопросам:",
            reply_markup=keyboard
        )
    @router.callback_query(lambda c: c.data == "clear_tests")
    async def clear_tests_callback(callback_query: CallbackQuery):
        user_id = callback_query.from_user.id
        discipline = storage.get_current_discipline(user_id)  # Получаем текущую дисциплину

        if discipline:
            # Создаем клавиатуру с кнопками "Подтвердить" и "Назад к тестам"
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Подтвердить", callback_data=f"confirm_clear_tests:{discipline}")],
                [InlineKeyboardButton(text="Назад к тестам", callback_data="go_to_tests")]
            ])
            await callback_query.message.edit_text(
                f"Очистить все тесты для дисциплины '{discipline}'?",
                reply_markup=keyboard
            )
        else:
            await callback_query.answer("Сначала выберите дисциплину!", show_alert=True)

    @router.callback_query(lambda c: c.data.startswith("confirm_clear_tests:"))
    async def confirm_clear_tests(callback_query: CallbackQuery):
        user_id = callback_query.from_user.id
        discipline = callback_query.data.split(":")[1]  # Извлекаем название дисциплины

        if discipline:
            # Очищаем все тесты для дисциплины
            storage.clear_tests(user_id, discipline)
            await callback_query.answer("Все тесты успешно очищены!")

            # Возвращаем пользователя к списку тестов с обновленной клавиатурой
            await callback_query.message.edit_text(
                f"Все тесты для дисциплины '{discipline}' очищены.",
                reply_markup=get_tests_keyboard(user_id, discipline)
            )
        else:
            await callback_query.answer("Ошибка: дисциплина не найдена!", show_alert=True)

    @router.callback_query(lambda c: c.data == "save_tests")
    async def save_tests_callback(callback_query: CallbackQuery):
        storage.save_data()
        await callback_query.answer("Данные успешно сохранены!")
    
    @router.callback_query(lambda c: c.data.startswith("select_test_to_delete:"))
    async def select_test_to_delete(callback_query: CallbackQuery):
        user_id = callback_query.from_user.id
        test_name = callback_query.data.split(":")[1]  # Извлекаем название теста
        storage.set_user_state(user_id, f"confirm_delete_test:{test_name}")  # Сохраняем состояние

        # Создаем клавиатуру с кнопками "Подтвердить" и "Назад к тестам"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Подтвердить удаление", callback_data=f"confirm_delete:{test_name}")],
            [InlineKeyboardButton(text="Назад к тестам", callback_data="go_to_tests")]
        ])
        await callback_query.message.edit_text(
            f"Вы выбрали тест '{test_name}'. Желаете его удалить?",
            reply_markup=keyboard
        )

    @router.callback_query(lambda c: c.data == "delete_test")
    async def delete_test_callback(callback_query: CallbackQuery):
        user_id = callback_query.from_user.id
        discipline = storage.get_current_discipline(user_id)
        if discipline:
            tests = storage.get_tests(user_id, discipline)
            if tests:
                # Создаем клавиатуру с тестами для удаления
                buttons = [
                    [InlineKeyboardButton(text=t, callback_data=f"select_test_to_delete:{t}")] for t in tests
                ]
                buttons.append([InlineKeyboardButton(text="Назад к тестам", callback_data="go_to_tests")])
                keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
                await callback_query.message.edit_text(
                    "Выберите тест для удаления:",
                    reply_markup=keyboard
                )
            else:
                await callback_query.answer("Нет тестов для удаления!", show_alert=True)
        else:
            await callback_query.answer("Сначала выберите дисциплину!", show_alert=True)

    @router.callback_query(lambda c: c.data.startswith("confirm_delete:"))
    async def confirm_delete_test(callback_query: CallbackQuery):
        user_id = callback_query.from_user.id
        test_name = callback_query.data.split(":")[1]  # Извлекаем название теста
        discipline = storage.get_current_discipline(user_id)

        if discipline:
            # Удаляем тест
            storage.delete_test(user_id, discipline, test_name)
            await callback_query.answer(f"Тест '{test_name}' успешно удален!")
            await callback_query.message.edit_text(
                f"Тест '{test_name}' удален.",
                reply_markup=get_tests_keyboard(user_id, discipline)
            )
        else:
            await callback_query.answer("Ошибка: дисциплина не найдена!", show_alert=True)
    
    @router.callback_query(lambda c: c.data == "delete_question")
    async def delete_question_callback(callback_query: CallbackQuery):
        user_id = callback_query.from_user.id
        test = storage.get_current_test(user_id)  # Получаем текущий тест

        if test:
            questions = storage.get_questions(user_id, test)  # Получаем вопросы
            if questions:
                # Создаем клавиатуру с вопросами для удаления
                buttons = [
                    [InlineKeyboardButton(text=q["text"], callback_data=f"select_question_to_delete:{index}")]
                    for index, q in enumerate(questions)
                ]
                buttons.append([InlineKeyboardButton(text="Назад к вопросам", callback_data="go_to_questions")])
                keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
                await callback_query.message.edit_text(
                    "Выберите вопрос для удаления:",
                    reply_markup=keyboard
                )
            else:
                await callback_query.answer("Нет вопросов для удаления!", show_alert=True)
        else:
            await callback_query.answer("Сначала выберите тест!", show_alert=True)

    @router.callback_query(lambda c: c.data.startswith("select_question_to_delete:"))
    async def select_question_to_delete(callback_query: CallbackQuery):
        user_id = callback_query.from_user.id
        question_index = int(callback_query.data.split(":")[1])  # Извлекаем индекс вопроса
        test = storage.get_current_test(user_id)

        if test:
            questions = storage.get_questions(user_id, test)
            if 0 <= question_index < len(questions):
                question_text = questions[question_index]["text"]
                storage.set_user_state(user_id, f"confirm_delete_question:{question_index}")  # Сохраняем состояние

                # Создаем клавиатуру с кнопками "Подтвердить" и "Назад к вопросам"
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="Подтвердить", callback_data=f"confirm_delete_question:{question_index}")],
                    [InlineKeyboardButton(text="Назад к вопросам", callback_data="go_to_questions")]
                ])
                await callback_query.message.edit_text(
                    f"Вы выбрали вопрос: '{question_text}'. Желаете его удалить?",
                    reply_markup=keyboard
                )
            else:
                await callback_query.answer("Вопрос не найден!", show_alert=True)
        else:
            await callback_query.answer("Сначала выберите тест!", show_alert=True)

    @router.callback_query(lambda c: c.data.startswith("confirm_delete_question:"))
    async def confirm_delete_question(callback_query: CallbackQuery):
        user_id = callback_query.from_user.id
        question_index = int(callback_query.data.split(":")[1])  # Извлекаем индекс вопроса
        test = storage.get_current_test(user_id)

        if test:
            questions = storage.get_questions(user_id, test)
            if 0 <= question_index < len(questions):
                # Удаляем вопрос
                deleted_question = questions.pop(question_index)
                storage.save_data()  # Сохраняем изменения
                await callback_query.answer(f"Вопрос '{deleted_question['text']}' успешно удален!")

                # Возвращаем пользователя к списку вопросов
                await callback_query.message.edit_text(
                    f"Вопрос '{deleted_question['text']}' удален.",
                    reply_markup=get_questions_keyboard(user_id, test)
                )
            else:
                await callback_query.answer("Вопрос не найден!", show_alert=True)
        else:
            await callback_query.answer("Сначала выберите тест!", show_alert=True)

    @router.callback_query(lambda c: c.data == "clear_questions")
    async def clear_questions_callback(callback_query: CallbackQuery):
        user_id = callback_query.from_user.id
        test = storage.get_current_test(user_id)

        if test:
            # Создаем клавиатуру с кнопками "Подтвердить" и "Назад к вопросам"
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Подтвердить", callback_data=f"confirm_clear_questions:{test}")],
                [InlineKeyboardButton(text="Назад к вопросам", callback_data="go_to_questions")]
            ])
            await callback_query.message.edit_text(
                f"Очистить все вопросы для теста '{test}'?",
                reply_markup=keyboard
            )
        else:
            await callback_query.answer("Сначала выберите тест!", show_alert=True)

    @router.callback_query(lambda c: c.data.startswith("confirm_clear_questions:"))
    async def confirm_clear_questions(callback_query: CallbackQuery):
        user_id = callback_query.from_user.id
        test = callback_query.data.split(":")[1]  # Извлекаем название теста

        if test:
            # Очищаем все вопросы для теста
            storage.clear_questions(user_id, test)
            await callback_query.answer("Все вопросы успешно очищены!")

            # Возвращаем пользователя к списку вопросов
            await callback_query.message.edit_text(
                f"Все вопросы для теста '{test}' очищены.",
                reply_markup=get_questions_keyboard(user_id, test)
            )
        else:
            await callback_query.answer("Ошибка: тест не найден!", show_alert=True)

    @router.callback_query(lambda c: c.data == "delete_discipline")
    async def delete_discipline_callback(callback_query: CallbackQuery):
        user_id = callback_query.from_user.id
        disciplines = storage.get_disciplines(user_id)  # Получаем список дисциплин

        if disciplines:
            # Создаем клавиатуру с дисциплинами для удаления
            buttons = [
                [InlineKeyboardButton(text=d, callback_data=f"select_discipline_to_delete:{d}")]
                for d in disciplines
            ]
            buttons.append([InlineKeyboardButton(text="Назад к дисциплинам", callback_data="go_to_disciplines")])
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            await callback_query.message.edit_text(
                "Выберите дисциплину для удаления:",
                reply_markup=keyboard
            )
        else:
            await callback_query.answer("Нет дисциплин для удаления!", show_alert=True)

    @router.callback_query(lambda c: c.data.startswith("select_discipline_to_delete:"))
    async def select_discipline_to_delete(callback_query: CallbackQuery):
        user_id = callback_query.from_user.id
        discipline = callback_query.data.split(":")[1]  # Извлекаем название дисциплины

        # Создаем клавиатуру с кнопками "Подтвердить" и "Назад к дисциплинам"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Подтвердить", callback_data=f"confirm_delete_discipline:{discipline}")],
            [InlineKeyboardButton(text="Назад к дисциплинам", callback_data="go_to_disciplines")]
        ])
        await callback_query.message.edit_text(
            f"Вы выбрали дисциплину: '{discipline}'. Желаете её удалить?",
            reply_markup=keyboard
        )

    @router.callback_query(lambda c: c.data.startswith("confirm_delete_discipline:"))
    async def confirm_delete_discipline(callback_query: CallbackQuery):
        user_id = callback_query.from_user.id
        discipline = callback_query.data.split(":")[1]  # Извлекаем название дисциплины

        # Удаляем дисциплину
        storage.delete_discipline(user_id, discipline)
        await callback_query.answer(f"Дисциплина '{discipline}' успешно удалена!")

        # Возвращаем пользователя к списку дисциплин
        await callback_query.message.edit_text(
            f"Дисциплина '{discipline}' удалена.",
            reply_markup=get_disciplines_keyboard(user_id)
        )

    @router.callback_query(lambda c: c.data == "clear_disciplines")
    async def clear_disciplines_callback(callback_query: CallbackQuery):
        user_id = callback_query.from_user.id

        # Создаем клавиатуру с кнопками "Подтвердить" и "Назад к дисциплинам"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Подтвердить", callback_data="confirm_clear_disciplines")],
            [InlineKeyboardButton(text="Назад к дисциплинам", callback_data="go_to_disciplines")]
        ])
        await callback_query.message.edit_text(
            "Очистить все дисциплины?",
            reply_markup=keyboard
        )

    @router.callback_query(lambda c: c.data == "confirm_clear_disciplines")
    async def confirm_clear_disciplines(callback_query: CallbackQuery):
        user_id = callback_query.from_user.id

        # Очищаем все дисциплины
        storage.clear_disciplines(user_id)
        await callback_query.answer("Все дисциплины успешно очищены!")

        # Возвращаем пользователя к списку дисциплин
        await callback_query.message.edit_text(
            "Все дисциплины очищены.",
            reply_markup=get_disciplines_keyboard(user_id)
        )





        