import json
import re
import os
from pathlib import Path
import argparse
import locale

class FrequencyDictionaryApp:
    def __init__(self, data_dir="data", dict_dir="dictionaries"):
        self.data_dir = Path(data_dir)
        self.dict_dir = Path(dict_dir)
        self.current_language = None
        self.current_data = None
        self.dictionaries = {}

    def set_locale(self, language):
        """Установка локали в зависимости от языка"""
        try:
            if language == "russian":
                locale.setlocale(locale.LC_COLLATE, "ru_RU.UTF-8")
            elif language == "english":
                locale.setlocale(locale.LC_COLLATE, "en_US.UTF-8")
            elif language == "german":
                locale.setlocale(locale.LC_COLLATE, "de_DE.UTF-8")
            else:
                locale.setlocale(locale.LC_COLLATE, "C")  # дефолт
        except locale.Error:
            print("Локаль не поддерживается в системе, сортировка может быть некорректной")
            locale.setlocale(locale.LC_COLLATE, "C")

    def load_dictionary(self, language):
        """Загрузка словаря из файла"""
        dict_file = self.dict_dir / f"{language}_dictionary.json"

        if not dict_file.exists():
            print(f"Словарь для {language} не найден. Сначала создайте его.")
            return False

        try:
            with open(dict_file, 'r', encoding='utf-8') as f:
                self.current_data = json.load(f)
            self.current_language = language
            self.dictionaries[language] = self.current_data
            self.set_locale(language)
            return True
        except Exception as e:
            print(f"Ошибка загрузки словаря: {e}")
            return False

    def display_stats(self):
        """Отображение статистики"""
        if not self.current_data:
            print("Сначала загрузите словарь!")
            return

        print(f"\n=== Статистика для {self.current_language} ===")
        print(f"Всего слов: {self.current_data['total_words']:,}")
        print(f"Уникальных слов: {self.current_data['unique_words']:,}")

    def display_sorted(self, sort_by='alphabet', reverse=False):
        """Отображение отсортированного словаря"""
        if not self.current_data:
            print("Сначала загрузите словарь!")
            return

        words = list(self.current_data['word_counts'].items())

        if sort_by == 'alphabet':
            words.sort(key=lambda x: locale.strxfrm(x[0]), reverse=reverse)
            sort_name = "алфавиту" + (" (обратный порядок)" if reverse else "")
        elif sort_by == 'frequency':
            words.sort(key=lambda x: x[1], reverse=not reverse)
            sort_name = "частоте" + (" (убывание)" if not reverse else " (возрастание)")

        print(f"\n=== Словарь по {sort_name} ===")
        for i, (word, count) in enumerate(words[:50]):  # Показываем первые 50
            print(f"{i+1:3d}. {word:20s} : {count:8d}")

        if len(words) > 50:
            print(f"... и еще {len(words) - 50} слов")

    def search_words(self, pattern):
        """Поиск слов по шаблону"""
        if not self.current_data:
            print("Сначала загрузите словарь!")
            return

        pattern = pattern.lower()
        found_words = []

        for word, count in self.current_data['word_counts'].items():
            if word.startswith(pattern):
                found_words.append((word, count))

        found_words.sort(key=lambda x: x[1], reverse=True)

        print(f"\n=== Найдено слов начинающихся с '{pattern}': {len(found_words)} ===")
        for i, (word, count) in enumerate(found_words[:20]):
            print(f"{i+1:3d}. {word:20s} : {count:8d}")

        if len(found_words) > 20:
            print(f"... и еще {len(found_words) - 20} слов")

    def correct_word(self, wrong_word, correct_word):
        """Исправление слова с суммированием частот"""
        if not self.current_data:
            print("Сначала загрузите словарь!")
            return False

        wrong_word = wrong_word.lower()
        correct_word = correct_word.lower()

        if wrong_word not in self.current_data['word_counts']:
            print(f"Слово '{wrong_word}' не найдено в словаре!")
            return False

        if correct_word not in self.current_data['word_counts']:
            # Если правильного слова нет, создаем его
            self.current_data['word_counts'][correct_word] = 0

        # Суммируем частоты
        wrong_count = self.current_data['word_counts'].pop(wrong_word)
        self.current_data['word_counts'][correct_word] += wrong_count

        # Обновляем счетчики
        self.current_data['unique_words'] = len(self.current_data['word_counts'])

        self.save_dictionary()
        print(f"Слово '{wrong_word}' исправлено на '{correct_word}'")
        return True

    def delete_word(self, word):
        """Удаление слова из словаря"""
        if not self.current_data:
            print("Сначала загрузите словарь!")
            return False

        word = word.lower()

        if word not in self.current_data['word_counts']:
            print(f"Слово '{word}' не найдено в словаре!")
            return False

        # Подтверждение удаления
        confirm = input(f"Вы уверены, что хотите удалить слово '{word}'? (y/N): ")
        if confirm.lower() != 'y':
            print("Удаление отменено.")
            return False

        count = self.current_data['word_counts'].pop(word)
        self.current_data['total_words'] -= count
        self.current_data['unique_words'] = len(self.current_data['word_counts'])

        self.save_dictionary()
        print(f"Слово '{word}' удалено из словаря")
        return True

    def add_word(self, word):
        """Добавление нового слова"""
        if not self.current_data:
            print("Сначала загрузите словарь!")
            return False

        word = word.lower()

        if word in self.current_data['word_counts']:
            print(f"Слово '{word}' уже есть в словаре!")
            return False

        self.current_data['word_counts'][word] = 0
        self.current_data['unique_words'] = len(self.current_data['word_counts'])

        self.save_dictionary()
        print(f"Слово '{word}' добавлено в словарь с частотой 0")
        return True

    def save_dictionary(self):
        """Сохранение словаря в файл"""
        if not self.current_data or not self.current_language:
            return False

        dict_file = self.dict_dir / f"{self.current_language}_dictionary.json"

        try:
            with open(dict_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Ошибка сохранения словаря: {e}")
            return False

    def interactive_mode(self):
        """Интерактивный режим работы"""
        print("=== Частотный словарь ===")

        while True:
            print("\nДоступные языки:")
            print("1. Русский")
            print("2. Английский")
            print("3. Немецкий")
            print("0. Выход")

            choice = input("\nВыберите язык (1-3) или 0 для выхода: ")

            if choice == '0':
                break
            elif choice == '1':
                language = 'russian'
            elif choice == '2':
                language = 'english'
            elif choice == '3':
                language = 'german'
            else:
                print("Неверный выбор!")
                continue

            if not self.load_dictionary(language):
                continue

            self.language_menu()

    def language_menu(self):
        """Меню для выбранного языка"""
        while True:
            print(f"\n=== Меню для {self.current_language} ===")
            print("1. Показать статистику")
            print("2. Отсортировать по алфавиту (А-Я)")
            print("3. Отсортировать по алфавиту (Я-А)")
            print("4. Отсортировать по частоте (убывание)")
            print("5. Отсортировать по частоте (возрастание)")
            print("6. Поиск слов по шаблону")
            print("7. Исправить слово")
            print("8. Удалить слово")
            print("9. Добавить слово")
            print("0. Назад к выбору языка")

            choice = input("\nВыберите действие (0-9): ")

            if choice == '0':
                break
            elif choice == '1':
                self.display_stats()
            elif choice == '2':
                self.display_sorted('alphabet', False)
            elif choice == '3':
                self.display_sorted('alphabet', True)
            elif choice == '4':
                self.display_sorted('frequency', False)
            elif choice == '5':
                self.display_sorted('frequency', True)
            elif choice == '6':
                pattern = input("Введите начало слова для поиска: ")
                self.search_words(pattern)
            elif choice == '7':
                wrong = input("Введите неправильное слово: ")
                correct = input("Введите правильное слово: ")
                self.correct_word(wrong, correct)
            elif choice == '8':
                word = input("Введите слово для удаления: ")
                self.delete_word(word)
            elif choice == '9':
                word = input("Введите новое слово: ")
                self.add_word(word)
            else:
                print("Неверный выбор!")

def main():
    parser = argparse.ArgumentParser(description='Интерфейс частотного словаря')
    parser.add_argument('--language', choices=['russian', 'english', 'german'],
                       help='Язык для загрузки')

    args = parser.parse_args()

    app = FrequencyDictionaryApp()

    if args.language:
        if app.load_dictionary(args.language):
            app.language_menu()
    else:
        app.interactive_mode()

if __name__ == "__main__":
    main()
