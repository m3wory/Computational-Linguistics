"""Конфигурация приложения частотного словаря"""

from pathlib import Path

# ==================== ПУТИ И ФАЙЛЫ ====================

DEFAULT_DATA_DIR = Path("data")
DEFAULT_DICT_DIR = Path("dictionaries")
DICTIONARY_FILE_TEMPLATE = "{language}_dictionary.json"
ALLOWED_EXTENSIONS = ['.txt']

# ==================== ЯЗЫКИ И ЛОКАЛИ ====================

LANGUAGES = {
    'russian': 'Русский',
    'english': 'Английский', 
    'german': 'Немецкий'
}

LOCALES = {
    'russian': 'ru_RU.UTF-8',
    'english': 'en_US.UTF-8',
    'german': 'de_DE.UTF-8'
}

# ==================== ОБРАБОТКА ТЕКСТА ====================

# Паттерны очистки слов для каждого языка
CLEAN_PATTERNS = {
    'english': r'[^a-zA-Z\-\']',
    'german': r'[^a-zA-ZäöüÄÖÜß\-\']',
    'russian': r'[^а-яёА-ЯЁ\-]'
}

# Кодировки для чтения файлов (по приоритету)
ENCODINGS = ['utf-8', 'cp1251', 'latin-1', 'cp1252']

# ==================== ИНТЕРФЕЙС И ОТОБРАЖЕНИЕ ====================

# Ограничения отображения
MAX_DISPLAY_WORDS = 50
MAX_SEARCH_RESULTS = 20

# Символы для сортировки
SORT_SYMBOLS = {
    'asc': '↑',
    'desc': '↓'
}

# Форматирование чисел
NUMBER_FORMAT = "{:,}"

# ==================== МЕНЮ ====================

MAIN_MENU_TITLE = "ЧАСТОТНЫЙ СЛОВАРЬ"
LANGUAGE_MENU_TITLE = "МЕНЮ: {language}"

MAIN_MENU_ITEMS = [
    "Статистика",
    "Алфавит А→Я", 
    "Алфавит Я→А", 
    "Частота ↓", 
    "Частота ↑",
    "Поиск слов",
    "Исправить слово", 
    "Удалить слово", 
    "Добавить слово",
    "Пополнить новым текстом"
]

# ==================== СООБЩЕНИЯ ПОЛЬЗОВАТЕЛЮ ====================

MESSAGES = {
    # Общие сообщения
    'app_title': "=== ЧАСТОТНЫЙ СЛОВАРЬ ===",
    'choose_language': "Выберите язык:",
    'exit_option': "Выход",
    'back_option': "Назад",
    'continue_prompt': "Нажмите Enter для продолжения...",
    'cancelled': "Отменено",
    
    # Ошибки
    'invalid_choice': "Неверный выбор!",
    'invalid_input': "Неверный ввод!",
    'unsupported_language': "Неподдерживаемый язык: {language}",
    'dictionary_not_found': "Словарь для {language} не найден. Создайте его сначала.",
    'no_dictionary_loaded': "Сначала загрузите словарь!",
    'file_not_found': "Файл не найден: {path}",
    'directory_not_found': "Директория {path} не найдена",
    'no_txt_files': "Текстовые файлы в {path} не найдены",
    'file_read_error': "Ошибка файла {path}: {error}",
    'save_error': "Ошибка сохранения: {error}",
    'load_error': "Ошибка загрузки словаря: {error}",
    'invalid_file_format': "Файл не найден или не .txt",
    'unicode_decode_error': "Не удалось прочитать файл: {path}",
    
    # Успешные операции
    'dictionary_created': "Словарь {language} создан:",
    'dictionary_exists': "Словарь для {language} уже существует",
    'word_corrected': "'{wrong}' → '{correct}' (частота: {count})",
    'word_deleted': "Слово '{word}' удалено",
    'word_added': "Слово '{word}' добавлено",
    'dictionary_updated': "Словарь обновлен",
    
    # Статистика
    'stats_title': "Статистика для {language}",
    'total_words': "Всего слов: {count}",
    'unique_words': "Уникальных: {count}",
    'stats_format': "{name:12}: {total:>10} слов ({unique:>8} уникальных)",
    'final_stats_title': "ИТОГОВАЯ СТАТИСТИКА",
    
    # Сортировка и поиск
    'sorted_by_alphabet': "Сортировка по алфавиту {direction}",
    'sorted_by_frequency': "Сортировка по частоте {direction}",
    'search_results': "Найдено слов с '{pattern}': {count}",
    'more_words': "... и еще {count} слов",
    
    # Подтверждения и вопросы
    'confirm_delete': "Удалить '{word}'? (y/N): ",
    'enter_pattern': "Начало слова: ",
    'enter_wrong_word': "Неправильное слово: ",
    'enter_correct_word': "Правильное слово: ",
    'enter_word_to_delete': "Слово для удаления: ",
    'enter_new_word': "Новое слово: ",
    'enter_file_path': "Путь к .txt файлу: ",
    'enter_choice': "Выбор ({range}): ",
    
    # Проверки слов
    'word_not_found': "Слово '{word}' не найдено",
    'word_already_exists': "Слово '{word}' уже есть",
    'invalid_word': "Некорректное слово",
    'empty_word': "Слово не может быть пустым",
    
    # Обработка файлов
    'processing_files': "Обработка {count} файлов для {language}...",
    'processing_new_file': "Обработка нового файла...",
    'creating_dictionary': "Создание {language}",
    'processing_lines': "Обработка",
    
    # Обновление словаря
    'update_stats_title': "=== Словарь обновлен ===",
    'new_words_processed': "Новых слов: {count}",
    'new_unique_words': "Новых уникальных: {count}",
    'total_words_change': "Всего: {old} → {new}",
    'unique_words_change': "Уникальных: {old} → {new}",
    
    # Системные сообщения
    'locale_not_supported': "Локаль не поддерживается, используется стандартная сортировка",
    'creating_directories': "Создание директорий...",
    'program_terminated': "Программа завершена.",
    'keyboard_interrupt': "Программа завершена пользователем.",
    'error_occurred': "Ошибка: {error}"
}

# ==================== КОМАНДНАЯ СТРОКА ====================

CLI_HELP = {
    'main_description': 'Частотный словарь',
    'examples': """
Примеры:
  python app.py create --language all          # создать все словари
  python app.py create --language russian      # создать только русский
  python app.py interface                      # запустить интерфейс
  python app.py interface --language russian   # сразу русский язык
    """,
    'create_help': 'Создание словарей',
    'interface_help': 'Интерактивный режим',
    'language_help': 'Язык для создания',
    'force_help': 'Пересоздать существующий словарь',
    'direct_language_help': 'Прямой запуск языка'
}

# ==================== НАСТРОЙКИ ОТЛАДКИ ====================

DEBUG = False
VERBOSE = False