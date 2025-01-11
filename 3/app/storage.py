import json
import os

class Storage:
    def __init__(self, filename='data.json'):
        self.filename = filename
        self.data = self.load_data()
        self.user_states = {}  # Словарь для хранения состояния пользователей
        self.current_disciplines = {}  # Словарь для хранения текущих дисциплин пользователей
        self.user_answers = {}
        self.tests = {}  # Данные о тестах
        self.authorized_users = set()  # Множество для хранения авторизованных пользователей

    def is_user_authorized(self, user_id):
        return user_id in self.authorized_users

    def set_user_authorized(self, user_id, authorized=False):
        if authorized:
            self.authorized_users.add(user_id)
        else:
            self.authorized_users.discard(user_id)

    def clear_user_state_for_attemp(self, user_id):
        if user_id in self.user_states:
            self.user_states[user_id] = {}

    def clear_user_state(self, user_id):
        if user_id in self.user_states:
            # Очищаем только состояние, оставляя другие данные
            if 'state' in self.user_states[user_id]:
                del self.user_states[user_id]['state']

    def load_data(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                # Если файл пуст или содержит невалидный JSON, возвращаем пустой словарь
                return {}
        else:
            # Если файл не существует, возвращаем пустой словарь
            return {}

    def save_data(self):
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    def initialize_user(self, user_id):
        if str(user_id) not in self.data:
            self.data[str(user_id)] = {
                "disciplines": [],
                "tests": {},
                "questions": {},
                "answers": [],
                "answer_count": 0,
                "correct_answer": None
            }
            self.save_data()

    def get_disciplines(self, user_id):
        return self.data.get(str(user_id), {}).get('disciplines', [])

    def get_current_discipline(self, user_id):
        return self.current_disciplines.get(user_id, None)  # Получаем текущую дисциплину

    def add_discipline(self, user_id, discipline):
        if str(user_id) not in self.data:
            self.initialize_user(user_id)
        self.data[str(user_id)]['disciplines'].append(discipline)
        self.save_data()

    def rename_discipline(self, user_id, old_discipline, new_discipline):
        """Переименовывает дисциплину."""
        if str(user_id) in self.data:
            disciplines = self.data[str(user_id)]['disciplines']
            if old_discipline in disciplines:
                index = disciplines.index(old_discipline)
                disciplines[index] = new_discipline  # Обновляем название дисциплины

                # Если вы используете тесты, нужно также обновить ключи тестов
                if old_discipline in self.data[str(user_id)]['tests']:
                    self.data[str(user_id)]['tests'][new_discipline] = self.data[str(user_id)]['tests'].pop(old_discipline)

                self.save_data()  # Сохраняем изменения в файл

    def set_current_discipline(self, user_id, discipline):
        """Устанавливает текущую дисциплину для пользователя."""
        self.current_disciplines[user_id] = discipline  # Сохраняем текущую дисциплину в памяти

    def get_user_state(self, user_id):
        return self.user_states.get(user_id, {}).get('state', None)  # Возвращаем состояние

    def set_user_state(self, user_id, state):
        if user_id not in self.user_states:
            self.user_states[user_id] = {}  # Инициализируем как словарь, если его нет
        self.user_states[user_id]['state'] = state  # Сохраняем состояние в словаре
        
    def get_user_state(self, user_id):
        return self.user_states.get(user_id, {}).get('state', None)  # Возвращаем состояние

    def set_user_state(self, user_id, state):
        if user_id not in self.user_states:
            self.user_states[user_id] = {}  # Инициализируем как словарь, если его нет
        self.user_states[user_id]['state'] = state  # Сохраняем состояние в словаре

    
    def set_current_test(self, user_id, test_name):
        """Устанавливает текущий тест для пользователя."""
        if user_id not in self.user_states:
            self.user_states[user_id] = {}  # Инициализируем как словарь, если его нет
        self.user_states[user_id]['current_test'] = test_name  # Сохраняем текущий тест
        print(f"DEBUG: Текущий тест сохранен для пользователя {user_id}: {test_name}")  # Отладочное сообщение

    def get_current_test(self, user_id):
        """Возвращает текущий тест для пользователя."""
        current_test = self.user_states.get(user_id, {}).get('current_test', None)
        print(f"DEBUG: Текущий тест для пользователя {user_id}: {current_test}")  # Отладочное сообщение
        return current_test

    def get_tests(self, user_id, discipline):
        return self.data.get(str(user_id), {}).get('tests', {}).get(discipline, [])

    def add_test(self, user_id, discipline, test_name):
        if str(user_id) not in self.data:
            self.initialize_user(user_id)
        if discipline not in self.data[str(user_id)]['tests']:
            self.data[str(user_id)]['tests'][discipline] = []
        self.data[str(user_id)]['tests'][discipline].append(test_name)
        self.save_data()

    def get_questions(self, user_id, test):
        """Возвращает список вопросов для указанного теста."""
        user_data = self.data.get(str(user_id), {})
        questions = user_data.get("questions", {})
        normalized_test = test.strip().lower()
        normalized_questions = {k.lower(): v for k, v in questions.items()}
        return normalized_questions.get(normalized_test, [])

    def set_current_question(self, user_id, question_id):
        """Устанавливает текущий вопрос для пользователя."""
        if user_id not in self.user_states:
            self.user_states[user_id] = {}  # Инициализируем как словарь, если его нет
        self.user_states[user_id]['current_question'] = question_id  # Сохраняем текущий вопрос

    def get_current_question(self, user_id):
        """Возвращает текущий вопрос для пользователя."""
        return self.user_states.get(user_id, {}).get('current_question', None)
    # def add_question(self, user_id, test, question):
    #     """Добавляет новый вопрос в тест."""
    #     if str(user_id) not in self.data:
    #         self.initialize_user(user_id)
    #     if test not in self.data[str(user_id)]['questions']:
    #         self.data[str(user_id)]['questions'][test] = []
    #     self.data[str(user_id)]['questions'][test].append({"text": question, "answers": []})
    #     self.save_data()

    def set_answer_count(self, user_id, count):
        """Устанавливает количество вариантов ответа для текущего вопроса."""
        self.user_states[user_id]['answer_count'] = count

    def add_question(self, user_id, test, question):
        """Добавляет новый вопрос в тест."""
        # Проверяем, что пользователь и тест валидны
        if str(user_id) not in self.data:
            print(f"ERROR: Пользователь {user_id} не инициализирован.")
            self.initialize_user(user_id)
        
        if not test:
            print(f"ERROR: Тест не указан для пользователя {user_id}.")
            return
        
        # Убедимся, что структура вопросов для теста существует
        if 'questions' not in self.data[str(user_id)]:
            self.data[str(user_id)]['questions'] = {}
        if test not in self.data[str(user_id)]['questions']:
            self.data[str(user_id)]['questions'][test] = []
        
        # Добавляем вопрос
        self.data[str(user_id)]['questions'][test].append({
            "text": question,
            "answers": [],
            "correct_answer": None  # Добавляем поле для правильного ответа
        })
        
        # Сохраняем данные
        self.save_data()
        print(f"DEBUG: Вопрос '{question}' добавлен в тест '{test}' для пользователя {user_id}.")

    def add_answer(self, user_id, answer):
        """Добавляет ответ к текущему вопросу."""
        current_test = self.get_current_test(user_id)
        questions = self.data[str(user_id)]['questions'][current_test]
        questions[-1]['answers'].append(answer)
        self.save_data()

    def set_correct_answer(self, user_id, answer):
        """Устанавливает правильный ответ для текущего вопроса."""
        current_test = self.get_current_test(user_id)
        questions = self.data[str(user_id)]['questions'][current_test]
        questions[-1]['correct_answer'] = answer
        self.save_data()

    def get_answers(self, user_id):
        """Возвращает список ответов для текущего вопроса."""
        current_test = self.get_current_test(user_id)
        questions = self.data[str(user_id)]['questions'][current_test]
        return questions[-1]['answers']
    def get_answers_for_question(self, user_id, question_index):
        """Возвращает список ответов для указанного вопроса."""
        current_test = self.get_current_test(user_id)
        questions = self.data.get(str(user_id), {}).get("tests", {}).get(current_test, [])
        if 0 <= question_index < len(questions):
            return questions[question_index].get("answers", [])
        return []

    def set_current_question_index(self, user_id, index):
        if user_id not in self.user_states:
            self.user_states[user_id] = {}
        self.user_states[user_id]["current_question_index"] = index

    def get_current_question_index(self, user_id):
        return self.user_states.get(user_id, {}).get("current_question_index", 0)

    def save_user_answer(self, user_id, test_name, question_index, answer_index):
        if user_id not in self.user_answers:
            self.user_answers[user_id] = {}
        if test_name not in self.user_answers[user_id]:
            self.user_answers[user_id][test_name] = {}
        self.user_answers[user_id][test_name][question_index] = answer_index


    def clear_tests(self, user_id, discipline):
        """Очищает все тесты для указанной дисциплины."""
        if str(user_id) in self.data and discipline in self.data[str(user_id)]['tests']:
            # Очищаем список тестов для указанной дисциплины
            self.data[str(user_id)]['tests'][discipline] = []
            
            # Также очищаем вопросы, связанные с этой дисциплиной
            if 'questions' in self.data[str(user_id)]:
                # Удаляем вопросы для всех тестов в этой дисциплине
                for test_name in list(self.data[str(user_id)]['questions'].keys()):
                    if test_name.startswith(discipline):
                        del self.data[str(user_id)]['questions'][test_name]
            
            # Сохраняем изменения в файл
            self.save_data()
            print(f"DEBUG: Все тесты и вопросы для дисциплины '{discipline}' очищены.")
        else:
            print(f"DEBUG: Дисциплина '{discipline}' не найдена для пользователя {user_id}.")
            
    def delete_test(self, user_id, discipline, test_name):
        """Удаляет конкретный тест из дисциплины и все связанные с ним вопросы."""
        if str(user_id) in self.data and discipline in self.data[str(user_id)]['tests']:
            tests = self.data[str(user_id)]['tests'][discipline]
            if test_name in tests:
                # Удаляем тест из списка
                tests.remove(test_name)
                
                # Удаляем все вопросы, связанные с этим тестом
                if 'questions' in self.data[str(user_id)] and test_name in self.data[str(user_id)]['questions']:
                    del self.data[str(user_id)]['questions'][test_name]
                
                # Сохраняем изменения в файл
                self.save_data()
                print(f"DEBUG: Тест '{test_name}' и связанные с ним вопросы удалены.")
            else:
                print(f"DEBUG: Тест '{test_name}' не найден в дисциплине '{discipline}'.")
        else:
            print(f"DEBUG: Дисциплина '{discipline}' не найдена для пользователя {user_id}.")

    def clear_questions(self, user_id, test):
        """Очищает все вопросы для указанного теста."""
        if str(user_id) in self.data and 'questions' in self.data[str(user_id)]:
            if test in self.data[str(user_id)]['questions']:
                del self.data[str(user_id)]['questions'][test]  # Удаляем все вопросы для теста
                self.save_data()  # Сохраняем изменения
                print(f"DEBUG: Все вопросы для теста '{test}' очищены.")
            else:
                print(f"DEBUG: Тест '{test}' не найден в вопросах.")
        else:
            print(f"DEBUG: Пользователь {user_id} не инициализирован или вопросы отсутствуют.")

    def delete_discipline(self, user_id, discipline):
        """Удаляет дисциплину и все связанные с ней тесты и вопросы."""
        if str(user_id) in self.data and discipline in self.data[str(user_id)]['disciplines']:
            # Удаляем дисциплину из списка
            self.data[str(user_id)]['disciplines'].remove(discipline)

            # Удаляем все тесты, связанные с этой дисциплиной
            if 'tests' in self.data[str(user_id)] and discipline in self.data[str(user_id)]['tests']:
                del self.data[str(user_id)]['tests'][discipline]

            # Удаляем все вопросы, связанные с тестами этой дисциплины
            if 'questions' in self.data[str(user_id)]:
                # Создаем список тестов для удаления
                tests_to_delete = self.data[str(user_id)]['tests'].get(discipline, [])
                for test_name in tests_to_delete:
                    if test_name in self.data[str(user_id)]['questions']:
                        del self.data[str(user_id)]['questions'][test_name]

            # Сохраняем изменения в файл
            self.save_data()
            print(f"DEBUG: Дисциплина '{discipline}' и связанные с ней тесты и вопросы удалены.")
        else:
            print(f"DEBUG: Дисциплина '{discipline}' не найдена для пользователя {user_id}.")
    def clear_disciplines(self, user_id):
        """Очищает все дисциплины, тесты и вопросы для пользователя."""
        if str(user_id) in self.data:
            # Очищаем дисциплины
            self.data[str(user_id)]['disciplines'] = []

            # Очищаем все тесты
            self.data[str(user_id)]['tests'] = {}

            # Очищаем все вопросы
            self.data[str(user_id)]['questions'] = {}

            # Сохраняем изменения в файл
            self.save_data()
            print(f"DEBUG: Все дисциплины, тесты и вопросы для пользователя {user_id} очищены.")
        else:
            print(f"DEBUG: Пользователь {user_id} не инициализирован.")



storage = Storage()