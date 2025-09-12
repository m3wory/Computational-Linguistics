import os
import re
import json
import argparse
from collections import defaultdict
from pathlib import Path
from tqdm import tqdm

class FrequencyDictionary:
    def __init__(self, data_dir="data", dict_dir="dictionaries"):
        self.data_dir = Path(data_dir)
        self.dict_dir = Path(dict_dir)
        self.dictionaries = {}
        
    def clean_word(self, word, language):
        """Очистка слова от лишних символов"""
        # Удаляем все, кроме букв, дефиса и апострофа
        if language == 'english':
            # Для английского разрешаем апостроф
            cleaned = re.sub(r'[^a-zA-Z\-\']', '', word.lower())
        elif language == 'german':
            # Для немецкого разрешаем умлауты и эсцет
            cleaned = re.sub(r'[^a-zA-ZäöüÄÖÜß\-\']', '', word.lower())
        elif language == 'russian':
            # Для русского разрешаем дефис
            cleaned = re.sub(r'[^а-яёА-ЯЁ\-]', '', word.lower())
        else:
            cleaned = re.sub(r'[^\w\-\']', '', word.lower())
            
        # Удаляем ВСЕ дефисы в начале слова
        while cleaned.startswith('-'):
            cleaned = cleaned[1:]
        
        # Удаляем ВСЕ дефисы в конце слова  
        while cleaned.endswith('-'):
            cleaned = cleaned[:-1]
        
        # Удаляем слова, состоящие только из дефисов/апострофов
        if not cleaned or cleaned.replace('-', '').replace("'", '') == '':
            return None
        return cleaned
    
    def process_text_file(self, file_path, language):
        """Обработка одного текстового файла"""
        word_counts = defaultdict(int)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    words = line.split()
                    for word in words:
                        cleaned_word = self.clean_word(word, language)
                        if cleaned_word:
                            word_counts[cleaned_word] += 1
        except UnicodeDecodeError:
            # Попробуем другие кодировки
            for encoding in ['cp1251', 'latin-1', 'cp1252']:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        for line in f:
                            words = line.split()
                            for word in words:
                                cleaned_word = self.clean_word(word, language)
                                if cleaned_word:
                                    word_counts[cleaned_word] += 1
                    break
                except:
                    continue
        
        return word_counts
    
    def create_dictionary(self, language, force_recreate=False):
        """Создание частотного словаря для языка"""
        dict_file = self.dict_dir / f"{language}_dictionary.json"
        
        # Если словарь уже существует и не нужно пересоздавать
        if dict_file.exists() and not force_recreate:
            print(f"Словарь для {language} уже существует. Используется существующий.")
            with open(dict_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        language_dir = self.data_dir / language
        if not language_dir.exists():
            print(f"Директория для {language} не найдена: {language_dir}")
            return {}
        
        # Собираем все текстовые файлы
        text_files = list(language_dir.glob("*.txt"))
        if not text_files:
            print(f"Не найдено текстовых файлов для {language}")
            return {}
        
        print(f"Обработка {len(text_files)} файлов для {language}...")
        
        total_word_counts = defaultdict(int)
        total_word_count = 0
        
        for file_path in tqdm(text_files, desc=f"Обработка {language}"):
            word_counts = self.process_text_file(file_path, language)
            for word, count in word_counts.items():
                total_word_counts[word] += count
                total_word_count += count
        
        # Сохраняем словарь
        result = {
            'word_counts': dict(total_word_counts),
            'total_words': total_word_count,
            'unique_words': len(total_word_counts)
        }
        
        with open(dict_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"Создан словарь для {language}:")
        print(f"  Всего слов: {total_word_count:,}")
        print(f"  Уникальных слов: {len(total_word_counts):,}")
        
        return result
    
    def create_all_dictionaries(self, force_recreate=False):
        """Создание словарей для всех языков"""
        languages = ['russian', 'english', 'german']
        
        for language in languages:
            self.create_dictionary(language, force_recreate)

def main():
    parser = argparse.ArgumentParser(description='Создание частотных словарей')
    parser.add_argument('--language', choices=['russian', 'english', 'german', 'all'], 
                       default='all', help='Язык для обработки')
    parser.add_argument('--force', action='store_true', help='Пересоздать словарь')
    
    args = parser.parse_args()
    
    fd = FrequencyDictionary()
    
    if args.language == 'all':
        fd.create_all_dictionaries(args.force)
    else:
        fd.create_dictionary(args.language, args.force)

if __name__ == "__main__":
    main()