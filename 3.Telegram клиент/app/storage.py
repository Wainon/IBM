import json
import os

class Storage:
    def __init__(self):
        self.users = {}
        self.load_data()  # Загружаем данные при инициализации

    def load_data(self):
        """Загрузка данных пользователей из файла JSON."""
        if os.path.exists('users_data.json'):
            with open('users_data.json', 'r', encoding='utf-8') as f:
                try:
                    self.users = json.load(f)
                    print("Данные пользователей успешно загружены из users_data.json.")
                    print(self.users)  # Выводим загруженные данные для отладки
                except json.JSONDecodeError:
                    print("Файл users_data.json пуст или поврежден. Создается новая структура.")
                    self.users = {}
        else:
            self.users = {}
            print("Файл users_data.json не найден. Создана новая база данных пользователей.")


    def save_data(self):
        """Сохранение данных пользователей в файл JSON."""
        with open('users_data.json', 'w', encoding='utf-8') as f:
            json.dump(self.users, f, ensure_ascii=False, indent=4)  # Добавляем indent для форматирования
        print("Данные пользователей успешно сохранены в users_data.json.")

    def initialize_user(self, user_id):
        if user_id not in self.users:
            self.users[user_id] = {
                "disciplines": [],
                "tests": {},
                "current_discipline": None,
                "current_test": None,
                "questions": {},
                "state": None,
                "answers": [],
                "answer_count": 0,
                "correct_answer": None
            }
            self.save_data()  # Сохраняем данные после инициализации пользователя

    def get_disciplines(self, user_id):
        return self.users[user_id]["disciplines"]

    def add_discipline(self, user_id, discipline_name):
        self.users[user_id]["disciplines"].append(discipline_name)
        self.save_data()  # Сохраняем изменения

    def get_tests(self, user_id, discipline):
        return self.users[user_id]["tests"].get(discipline, [])

    def add_test(self, user_id, discipline, test_name):
        if discipline not in self.users[user_id]["tests"]:
            self.users[user_id]["tests"][discipline] = []
        self.users[user_id]["tests"][discipline].append(test_name)
        self.save_data()  # Сохраняем изменения

    def get_questions(self, user_id, test):
        return self.users[user_id]["questions"].get(test, [])

    def add_question(self, user_id, test, question_text):
        if test not in self.users[user_id]["questions"]:
            self.users[user_id]["questions"][test] = []
        self.users[user_id]["questions"][test].append(question_text)
        self.save_data()  # Сохраняем изменения

    # Методы для работы с текущей дисциплиной
    def set_current_discipline(self, user_id, discipline):
        self.users[user_id]["current_discipline"] = discipline
        self.save_data()  # Сохраняем изменения

    def get_current_discipline(self, user_id):
        return self.users[user_id]["current_discipline"]

    # Методы для работы с текущим тестом
    def set_current_test(self, user_id, test):
        self.users[user_id]["current_test"] = test
        self.save_data()  # Сохраняем изменения

    def get_current_test(self, user_id): 
        return self.users[user_id]["current_test"]

    def set_user_state(self, user_id, state):
        self.users[user_id]["state"] = state
        self.save_data()  # Сохраняем изменения

    def get_user_state(self, user_id):
        return self.users[user_id]["state"]

    def clear_user_state(self, user_id):
        self.users[user_id]["state"] = None
        self.save_data()  # Сохраняем изменения

    def set_answer_count(self, user_id, count):
        self.users[user_id]["answer_count"] = count
        self.save_data()  # Сохраняем изменения

    def get_answer_count(self, user_id):
        return self.users[user_id]["answer_count"]

    def set_answers(self, user_id, answers):
        self.users[user_id]["answers"] = answers
        self.save_data()  # Сохраняем изменения

    def get_answers_for_question(self, user_id, question):
        """Возвращает список ответов для заданного вопроса."""
        return self.users[user_id]["questions"].get(question, {}).get("answers", [])

    def get_answers(self, user_id):
        return self.users[user_id]["answers"]

    def set_correct_answer(self, user_id, correct_answer):
        self.users[user_id]["correct_answer"] = correct_answer
        self.save_data()  # Сохраняем изменения

    def get_correct_answer(self, user_id):
        return self.users[user_id]["correct_answer"]

    def clear_tests(self, user_id):
        print(f" Очистка тестов для пользователя {user_id}...")
        if user_id in self.users:
            self.users[user_id]["tests"] = {}
            self.save_data()  # Сохраняем изменения
            print(f"Тесты для пользователя {user_id} очищены.")

# Создание экземпляра класса
storage = Storage()