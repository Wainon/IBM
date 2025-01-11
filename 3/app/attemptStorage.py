import json
import os

class AttemptStorage:
    def __init__(self, filename='attempts_data.json'):
        self.filename = filename
        self.data = self.load_data()

    def load_data(self):
        """Загружает данные о попытках из файла."""
        if os.path.exists(self.filename):
            with open(self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def save_data(self):
        """Сохраняет данные о попытках в файл."""
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)


    def get_tests(self, user_id, discipline):
        return self.data.get(str(user_id), {}).get('tests', {}).get(discipline, [])

# Создаем экземпляр хранилища попыток
attempt_storage = AttemptStorage()