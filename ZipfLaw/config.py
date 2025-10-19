"""Конфигурация для статистического анализа"""

from pathlib import Path

# Пути
FREQ_DICT_DIR = Path("../FrequencyDictionary/dictionaries")
DATA_DIR = Path("../FrequencyDictionary/data")
OUTPUT_DIR = Path("output")
PLOTS_DIR = OUTPUT_DIR / "plots"
TABLES_DIR = OUTPUT_DIR / "tables"

# Создание директорий
OUTPUT_DIR.mkdir(exist_ok=True)
PLOTS_DIR.mkdir(exist_ok=True)
TABLES_DIR.mkdir(exist_ok=True)

# Языки
LANGUAGES = {
    'russian': 'Русский',
    'english': 'Английский',
    'german': 'Немецкий'
}

# Служебные слова для задания 2
FUNCTION_WORDS = {
    'russian': [
        'и', 'в', 'не', 'на', 'я', 'что', 'он', 'с', 'а', 'как',
        'это', 'по', 'но', 'к', 'его', 'за', 'о', 'от', 'у', 'из',
        'до', 'при', 'для', 'или', 'бы', 'же', 'еще', 'ни', 'уже', 'да'
    ],
    'english': [
        'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
        'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
        'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she'
    ],
    'german': [
        'der', 'die', 'und', 'in', 'den', 'von', 'zu', 'das', 'mit', 'sich',
        'des', 'auf', 'für', 'ist', 'im', 'dem', 'nicht', 'ein', 'eine', 'als',
        'auch', 'es', 'an', 'werden', 'aus', 'er', 'hat', 'dass', 'sie', 'nach', 'war'
    ]
}

# Параметры для графиков
PLOT_STYLE = 'seaborn-v0_8-darkgrid'
PLOT_DPI = 300
FIGURE_SIZE = (12, 8)

# Параметры для анализа
TOP_WORDS_ZIPF = 100  # Количество слов для анализа закона Ципфа
SEGMENT_SIZE = 250000  # Размер сегмента для коэффициента Жуйана (в словах)
TOP_WORDS_JUYAN = 50  # Количество слов в итоговой таблице Жуйана

# Кодировки для чтения файлов
ENCODINGS = ['utf-8', 'cp1251', 'latin-1', 'cp1252']