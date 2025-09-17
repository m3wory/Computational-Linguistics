"""Класс для работы с частотными словарями"""

import json
import re
import locale
from pathlib import Path
from typing import Dict, Optional, List
from collections import defaultdict
from tqdm import tqdm

from config import (
    DEFAULT_DATA_DIR, DEFAULT_DICT_DIR, DICTIONARY_FILE_TEMPLATE,
    LANGUAGES, LOCALES, CLEAN_PATTERNS, ENCODINGS, ALLOWED_EXTENSIONS,
    MAX_DISPLAY_WORDS, MAX_SEARCH_RESULTS, NUMBER_FORMAT, SORT_SYMBOLS,
    MESSAGES
)


class FrequencyDictionary:
    """Единый класс для создания и работы с частотными словарями"""
    
    def __init__(self, data_dir=DEFAULT_DATA_DIR, dict_dir=DEFAULT_DICT_DIR):
        self.data_dir = Path(data_dir)
        self.dict_dir = Path(dict_dir)
        self.current_language = None
        self.current_data = None
        
        # Создаем директории
        self.data_dir.mkdir(exist_ok=True)
        self.dict_dir.mkdir(exist_ok=True)
    
    # ==================== БАЗОВЫЕ МЕТОДЫ ====================
    
    def clean_word(self, word: str, language: str) -> Optional[str]:
        """Очистка слова от лишних символов"""
        if not word or language not in LANGUAGES:
            return None
            
        pattern = CLEAN_PATTERNS.get(language, r'[^\w\-\']')
        cleaned = re.sub(pattern, '', word.lower()).strip('-')
        
        if not cleaned or cleaned.replace('-', '').replace("'", '') == '':
            return None
        return cleaned
    
    def read_file(self, file_path: Path) -> List[str]:
        """Чтение файла с разными кодировками"""
        for encoding in ENCODINGS:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.readlines()
            except UnicodeDecodeError:
                continue
        raise UnicodeDecodeError(MESSAGES['unicode_decode_error'].format(path=file_path))
    
    def set_locale(self, language: str):
        """Установка локали для сортировки"""
        try:
            locale.setlocale(locale.LC_COLLATE, LOCALES.get(language, "C"))
        except locale.Error:
            print(MESSAGES['locale_not_supported'])
            locale.setlocale(locale.LC_COLLATE, "C")
    
    def get_dictionary_path(self, language: str) -> Path:
        """Получение пути к файлу словаря"""
        filename = DICTIONARY_FILE_TEMPLATE.format(language=language)
        return self.dict_dir / filename
    
    # ==================== СОЗДАНИЕ СЛОВАРЕЙ ====================
    
    def create_dictionary(self, language: str, force: bool = False) -> bool:
        """Создание частотного словаря для языка"""
        if language not in LANGUAGES:
            print(MESSAGES['unsupported_language'].format(language=language))
            return False
        
        dict_file = self.get_dictionary_path(language)
        
        # Проверяем существование
        if dict_file.exists() and not force:
            print(MESSAGES['dictionary_exists'].format(language=language))
            return True
        
        # Получаем текстовые файлы
        lang_dir = self.data_dir / language
        if not lang_dir.exists():
            print(MESSAGES['directory_not_found'].format(path=lang_dir))
            return False
        
        txt_files = []
        for ext in ALLOWED_EXTENSIONS:
            txt_files.extend(lang_dir.glob(f"*{ext}"))
        
        if not txt_files:
            print(MESSAGES['no_txt_files'].format(path=lang_dir))
            return False
        
        print(MESSAGES['processing_files'].format(count=len(txt_files), language=language))
        
        # Обрабатываем файлы
        word_counts = defaultdict(int)
        
        for file_path in tqdm(txt_files, desc=MESSAGES['creating_dictionary'].format(language=language)):
            try:
                lines = self.read_file(file_path)
                for line in lines:
                    for word in line.split():
                        cleaned = self.clean_word(word, language)
                        if cleaned:
                            word_counts[cleaned] += 1
            except Exception as e:
                print(MESSAGES['file_read_error'].format(path=file_path, error=e))
        
        # Сохраняем словарь
        data = {
            'word_counts': dict(word_counts),
            'total_words': sum(word_counts.values()),
            'unique_words': len(word_counts)
        }
        
        try:
            with open(dict_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(MESSAGES['dictionary_created'].format(language=language))
            print(MESSAGES['total_words'].format(count=NUMBER_FORMAT.format(data['total_words'])))
            print(MESSAGES['unique_words'].format(count=NUMBER_FORMAT.format(data['unique_words'])))
            return True
            
        except Exception as e:
            print(MESSAGES['save_error'].format(error=e))
            return False
    
    def create_all(self, force: bool = False):
        """Создание всех словарей"""
        for lang in LANGUAGES:
            self.create_dictionary(lang, force)
    
    # ==================== ЗАГРУЗКА И ИНТЕРФЕЙС ====================
    
    def load_dictionary(self, language: str) -> bool:
        """Загрузка словаря"""
        if language not in LANGUAGES:
            print(MESSAGES['unsupported_language'].format(language=language))
            return False
        
        dict_file = self.get_dictionary_path(language)
        if not dict_file.exists():
            print(MESSAGES['dictionary_not_found'].format(language=language))
            return False
        
        try:
            with open(dict_file, 'r', encoding='utf-8') as f:
                self.current_data = json.load(f)
            self.current_language = language
            self.set_locale(language)
            return True
        except Exception as e:
            print(MESSAGES['load_error'].format(error=e))
            return False
    
    def save_current(self) -> bool:
        """Сохранение текущего словаря"""
        if not self.current_data or not self.current_language:
            return False
        
        dict_file = self.get_dictionary_path(self.current_language)
        try:
            with open(dict_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(MESSAGES['save_error'].format(error=e))
            return False
    
    def stats(self):
        """Показать статистику"""
        if not self.current_data:
            print(MESSAGES['no_dictionary_loaded'])
            return
        
        lang_name = LANGUAGES[self.current_language]
        print(f"\n=== {MESSAGES['stats_title'].format(language=lang_name)} ===")
        total = NUMBER_FORMAT.format(self.current_data['total_words'])
        unique = NUMBER_FORMAT.format(self.current_data['unique_words'])
        print(MESSAGES['total_words'].format(count=total))
        print(MESSAGES['unique_words'].format(count=unique))
    
    def display_sorted(self, by_freq: bool = False, reverse: bool = False):
        """Показать отсортированный список"""
        if not self.current_data:
            print(MESSAGES['no_dictionary_loaded'])
            return
        
        words = list(self.current_data['word_counts'].items())
        
        if by_freq:
            words.sort(key=lambda x: x[1], reverse=not reverse)
            direction = SORT_SYMBOLS['asc'] if reverse else SORT_SYMBOLS['desc']
            sort_type = MESSAGES['sorted_by_frequency'].format(direction=direction)
        else:
            words.sort(key=lambda x: locale.strxfrm(x[0]), reverse=reverse)
            direction = SORT_SYMBOLS['desc'] if reverse else SORT_SYMBOLS['asc']
            sort_type = MESSAGES['sorted_by_alphabet'].format(direction=direction)
        
        print(f"\n=== {sort_type} ===")
        display_count = min(len(words), MAX_DISPLAY_WORDS)
        for i, (word, count) in enumerate(words[:display_count]):
            formatted_count = NUMBER_FORMAT.format(count)
            print(f"{i+1:3d}. {word:20s} : {formatted_count:>8s}")
        
        if len(words) > MAX_DISPLAY_WORDS:
            remaining = len(words) - MAX_DISPLAY_WORDS
            print(MESSAGES['more_words'].format(count=remaining))
    
    def search(self, pattern: str):
        """Поиск слов по шаблону"""
        if not self.current_data:
            print(MESSAGES['no_dictionary_loaded'])
            return
        
        pattern = pattern.lower().strip()
        found = [(w, c) for w, c in self.current_data['word_counts'].items() 
                if w.startswith(pattern)]
        found.sort(key=lambda x: x[1], reverse=True)
        
        print(f"\n=== {MESSAGES['search_results'].format(pattern=pattern, count=len(found))} ===")
        display_count = min(len(found), MAX_SEARCH_RESULTS)
        for i, (word, count) in enumerate(found[:display_count]):
            formatted_count = NUMBER_FORMAT.format(count)
            print(f"{i+1:3d}. {word:20s} : {formatted_count:>8s}")
        
        if len(found) > MAX_SEARCH_RESULTS:
            remaining = len(found) - MAX_SEARCH_RESULTS
            print(MESSAGES['more_words'].format(count=remaining))
    
    def correct_word(self, wrong: str, correct: str) -> bool:
        """Исправление слова"""
        if not self.current_data:
            print(MESSAGES['no_dictionary_loaded'])
            return False
        
        wrong = wrong.lower().strip()
        correct = correct.lower().strip()
        
        if not wrong or not correct:
            print(MESSAGES['empty_word'])
            return False
        
        if wrong not in self.current_data['word_counts']:
            print(MESSAGES['word_not_found'].format(word=wrong))
            return False
        
        # Переносим частоту
        count = self.current_data['word_counts'].pop(wrong)
        if correct in self.current_data['word_counts']:
            self.current_data['word_counts'][correct] += count
        else:
            self.current_data['word_counts'][correct] = count
        
        # Обновляем статистику
        self.current_data['unique_words'] = len(self.current_data['word_counts'])
        
        if self.save_current():
            print(MESSAGES['word_corrected'].format(wrong=wrong, correct=correct, count=count))
            return True
        return False
    
    def delete_word(self, word: str) -> bool:
        """Удаление слова"""
        if not self.current_data:
            print(MESSAGES['no_dictionary_loaded'])
            return False
        
        word = word.lower().strip()
        if not word:
            print(MESSAGES['empty_word'])
            return False
            
        if word not in self.current_data['word_counts']:
            print(MESSAGES['word_not_found'].format(word=word))
            return False
        
        confirm = input(MESSAGES['confirm_delete'].format(word=word))
        if confirm.lower() != 'y':
            print(MESSAGES['cancelled'])
            return False
        
        count = self.current_data['word_counts'].pop(word)
        self.current_data['total_words'] -= count
        self.current_data['unique_words'] = len(self.current_data['word_counts'])
        
        if self.save_current():
            print(MESSAGES['word_deleted'].format(word=word))
            return True
        return False
    
    def add_word(self, word: str) -> bool:
        """Добавление слова"""
        if not self.current_data:
            print(MESSAGES['no_dictionary_loaded'])
            return False
        
        word = word.lower().strip()
        if not word:
            print(MESSAGES['empty_word'])
            return False
            
        cleaned = self.clean_word(word, self.current_language)
        
        if not cleaned:
            print(MESSAGES['invalid_word'])
            return False
        
        if cleaned in self.current_data['word_counts']:
            print(MESSAGES['word_already_exists'].format(word=cleaned))
            return False
        
        self.current_data['word_counts'][cleaned] = 0
        self.current_data['unique_words'] = len(self.current_data['word_counts'])
        
        if self.save_current():
            print(MESSAGES['word_added'].format(word=cleaned))
            return True
        return False
    
    def add_text_file(self, file_path: str) -> bool:
        """Пополнение словаря новым текстом"""
        if not self.current_data:
            print(MESSAGES['no_dictionary_loaded'])
            return False
        
        file_path = Path(file_path.strip())
        if not file_path.exists() or file_path.suffix not in ALLOWED_EXTENSIONS:
            print(MESSAGES['invalid_file_format'])
            return False
        
        print(MESSAGES['processing_new_file'])
        try:
            lines = self.read_file(file_path)
            new_counts = defaultdict(int)
            
            for line in tqdm(lines, desc=MESSAGES['processing_lines']):
                for word in line.split():
                    cleaned = self.clean_word(word, self.current_language)
                    if cleaned:
                        new_counts[cleaned] += 1
            
            # Статистика
            old_total = self.current_data['total_words']
            old_unique = self.current_data['unique_words']
            new_words = 0
            total_new = sum(new_counts.values())
            
            # Обновляем словарь
            for word, count in new_counts.items():
                if word in self.current_data['word_counts']:
                    self.current_data['word_counts'][word] += count
                else:
                    self.current_data['word_counts'][word] = count
                    new_words += 1
            
            self.current_data['total_words'] += total_new
            self.current_data['unique_words'] = len(self.current_data['word_counts'])
            
            if self.save_current():
                print(f"\n{MESSAGES['update_stats_title']}")
                print(MESSAGES['new_words_processed'].format(count=NUMBER_FORMAT.format(total_new)))
                print(MESSAGES['new_unique_words'].format(count=new_words))
                
                old_total_fmt = NUMBER_FORMAT.format(old_total)
                new_total_fmt = NUMBER_FORMAT.format(self.current_data['total_words'])
                print(MESSAGES['total_words_change'].format(old=old_total_fmt, new=new_total_fmt))
                
                old_unique_fmt = NUMBER_FORMAT.format(old_unique)
                new_unique_fmt = NUMBER_FORMAT.format(self.current_data['unique_words'])
                print(MESSAGES['unique_words_change'].format(old=old_unique_fmt, new=new_unique_fmt))
                return True
            return False
                
        except Exception as e:
            print(MESSAGES['error_occurred'].format(error=e))
            return False