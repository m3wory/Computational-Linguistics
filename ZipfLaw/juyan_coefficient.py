"""Расчет коэффициента D Жуйана"""

import json
import re
import numpy as np
import pandas as pd
from pathlib import Path
from collections import defaultdict
from tqdm import tqdm
from config import *


class JuyanAnalyzer:
    """Анализ коэффициента Жуйана"""
    
    def __init__(self, language):
        self.language = language
        self.word_counts = None
        self.segments = []
        self.clean_pattern = self._get_clean_pattern()
        
    def _get_clean_pattern(self):
        """Получение паттерна очистки для языка"""
        patterns = {
            'english': r'[^a-zA-Z\-\']',
            'german': r'[^a-zA-ZäöüÄÖÜß\-\']',
            'russian': r'[^а-яёА-ЯЁ\-]'
        }
        return patterns.get(self.language, r'[^\w\-\']')
    
    def clean_word(self, word):
        """Очистка слова"""
        cleaned = re.sub(self.clean_pattern, '', word.lower()).strip('-')
        if not cleaned or cleaned.replace('-', '').replace("'", '') == '':
            return None
        return cleaned
    
    def read_file(self, file_path):
        """Чтение файла с разными кодировками"""
        for encoding in ENCODINGS:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        raise UnicodeDecodeError(f"Не удалось прочитать файл: {file_path}")
    
    def split_into_segments(self, target_segment_size=SEGMENT_SIZE):
        """Разбиение корпуса на сегменты"""
        print(f"Разбиение корпуса на сегменты по {target_segment_size:,} слов...")
        
        # Читаем все файлы языка
        lang_dir = DATA_DIR / self.language
        txt_files = list(lang_dir.glob("*.txt"))
        
        all_words = []
        for file_path in tqdm(txt_files, desc="Чтение файлов"):
            try:
                text = self.read_file(file_path)
                words = text.split()
                for word in words:
                    cleaned = self.clean_word(word)
                    if cleaned:
                        all_words.append(cleaned)
            except Exception as e:
                print(f"Ошибка при чтении {file_path}: {e}")
        
        print(f"Всего слов в корпусе: {len(all_words):,}")
        
        # Разбиваем на сегменты
        num_segments = max(4, len(all_words) // target_segment_size)
        actual_segment_size = len(all_words) // num_segments
        
        print(f"Количество сегментов: {num_segments}")
        print(f"Размер сегмента: ~{actual_segment_size:,} слов")
        
        self.segments = []
        for i in range(num_segments):
            start = i * actual_segment_size
            end = start + actual_segment_size if i < num_segments - 1 else len(all_words)
            segment_words = all_words[start:end]
            
            # Подсчитываем частоты в сегменте
            segment_counts = defaultdict(int)
            for word in segment_words:
                segment_counts[word] += 1
            
            self.segments.append(dict(segment_counts))
        
        return len(all_words), num_segments
    
    def calculate_juyan(self, word):
        """Расчет коэффициента Жуйана для слова"""
        # Собираем частоты слова в каждом сегменте
        frequencies = []
        n_segments_with_word = 0
        
        for segment in self.segments:
            freq = segment.get(word, 0)
            frequencies.append(freq)
            if freq > 0:
                n_segments_with_word += 1
        
        if n_segments_with_word < 2:
            return None
        
        frequencies = np.array(frequencies)
        
        # Средняя частота
        mu = np.mean(frequencies)
        
        # Стандартное отклонение
        sigma = np.std(frequencies, ddof=0)  # Используем ddof=0 как в примере
        
        # Коэффициент Жуйана
        if mu == 0:
            return None
        
        n = n_segments_with_word
        D = 100 * (1 - (sigma / (mu * np.sqrt(n - 1))))
        
        return {
            'D': D,
            'mu': mu,
            'sigma': sigma,
            'n': n,
            'frequencies': frequencies
        }
    
    def analyze_top_words(self, top_n=TOP_WORDS_JUYAN):
        """Анализ топ-N слов по коэффициенту Жуйана"""
        # Загружаем частотный словарь для получения списка слов
        dict_path = FREQ_DICT_DIR / f"{self.language}_dictionary.json"
        with open(dict_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        word_counts = data['word_counts']
        
        # Разбиваем корпус на сегменты
        total_words, num_segments = self.split_into_segments()
        
        print(f"\nРасчет коэффициентов Жуйана...")
        
        # Рассчитываем D для всех слов
        results = []
        for word, total_count in tqdm(word_counts.items(), desc="Обработка слов"):
            juyan_data = self.calculate_juyan(word)
            
            if juyan_data:
                # Относительная частота (на миллион слов)
                relative_freq = (total_count / total_words) * 1_000_000
                
                results.append({
                    'word': word,
                    'total_count': total_count,
                    'relative_freq': relative_freq,
                    'D': juyan_data['D'],
                    'mu': juyan_data['mu'],
                    'sigma': juyan_data['sigma'],
                    'n_segments': juyan_data['n']
                })
        
        # Сортируем по частоте
        results.sort(key=lambda x: x['total_count'], reverse=True)
        
        # Добавляем ранг
        for i, item in enumerate(results, 1):
            item['rank'] = i
        
        return results[:top_n], total_words, num_segments
    
    def save_to_excel(self, results, total_words, num_segments):
        """Сохранение результатов в Excel"""
        df = pd.DataFrame(results)
        
        # Форматируем колонки
        df = df[['rank', 'word', 'total_count', 'relative_freq', 'mu', 'sigma', 'n_segments', 'D']]
        df.columns = ['Ранг', 'Слово', 'Частота', 'Отн.частота', 'μ', 'σ', 'n', 'D']
        
        # Округляем числа
        df['Отн.частота'] = df['Отн.частота'].round(2)
        df['μ'] = df['μ'].round(2)
        df['σ'] = df['σ'].round(2)
        df['D'] = df['D'].round(2)
        
        excel_path = TABLES_DIR / f"juyan_{self.language}.xlsx"
        
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Коэффициент Жуйана', index=False)
            
            # Добавляем информацию о корпусе
            info_df = pd.DataFrame({
                'Параметр': [
                    'Язык',
                    'Всего слов в корпусе',
                    'Количество сегментов',
                    'Размер сегмента',
                    'Проанализировано слов'
                ],
                'Значение': [
                    LANGUAGES[self.language],
                    f"{total_words:,}",
                    num_segments,
                    f"~{total_words // num_segments:,}",
                    len(results)
                ]
            })
            info_df.to_excel(writer, sheet_name='Информация', index=False)
        
        print(f"Таблица сохранена: {excel_path}")
        return excel_path
    
    def generate_report(self, results, total_words, num_segments):
        """Генерация текстового отчета"""
        report = []
        report.append(f"=== КОЭФФИЦИЕНТ ЖУЙАНА - {LANGUAGES[self.language].upper()} ===\n")
        report.append(f"Всего слов в корпусе: {total_words:,}")
        report.append(f"Количество сегментов: {num_segments}")
        report.append(f"Размер сегмента: ~{total_words // num_segments:,} слов")
        report.append(f"Проанализировано топ слов: {len(results)}\n")
        
        report.append("Формула: D = 100 × (1 - σ / (μ × √(n-1)))\n")
        
        report.append(f"{'Ранг':>5} {'Слово':>15} {'Частота':>10} {'Отн.частота':>12} {'μ':>8} {'σ':>8} {'n':>3} {'D':>8}")
        report.append("-" * 75)
        
        for item in results[:20]:  # Показываем первые 20
            report.append(
                f"{item['rank']:>5} {item['word']:>15} {item['total_count']:>10} "
                f"{item['relative_freq']:>12.2f} {item['mu']:>8.2f} {item['sigma']:>8.2f} "
                f"{item['n_segments']:>3} {item['D']:>8.2f}"
            )
        
        return "\n".join(report)
    
    def analyze(self):
        """Полный анализ"""
        print(f"\n--- Коэффициент Жуйана для {LANGUAGES[self.language]} ---")
        
        results, total_words, num_segments = self.analyze_top_words()
        
        # Сохраняем в Excel
        self.save_to_excel(results, total_words, num_segments)
        
        # Сохраняем текстовый отчет
        report = self.generate_report(results, total_words, num_segments)
        report_path = OUTPUT_DIR / f"juyan_report_{self.language}.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(report)
        print(f"\nОтчет сохранен: {report_path}")
        
        return results


def analyze_all_languages():
    """Анализ для всех языков"""
    all_results = {}
    
    for lang in LANGUAGES.keys():
        analyzer = JuyanAnalyzer(lang)
        all_results[lang] = analyzer.analyze()
    
    return all_results


if __name__ == "__main__":
    analyze_all_languages()