"""Эмпирический закон Ципфа - длина слова обратно пропорциональна частоте"""

import json
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import spearmanr
from config import *


class EmpiricalZipfAnalyzer:
    """Анализ эмпирического закона Ципфа для служебных слов"""
    
    def __init__(self, language):
        self.language = language
        self.word_counts = None
        self.function_words_data = []
        
    def load_dictionary(self):
        """Загрузка частотного словаря"""
        dict_path = FREQ_DICT_DIR / f"{self.language}_dictionary.json"
        with open(dict_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.word_counts = data['word_counts']
        
    def extract_function_words(self):
        """Извлечение данных о служебных словах"""
        if not self.word_counts:
            self.load_dictionary()
        
        function_words_list = FUNCTION_WORDS.get(self.language, [])
        
        for word in function_words_list:
            if word in self.word_counts:
                self.function_words_data.append({
                    'word': word,
                    'length': len(word),
                    'frequency': self.word_counts[word]
                })
        
        # Сортируем по частоте
        self.function_words_data.sort(key=lambda x: x['frequency'], reverse=True)
        
    def calculate_correlation(self):
        """Расчет корреляции между длиной и частотой"""
        if not self.function_words_data:
            self.extract_function_words()
        
        lengths = np.array([d['length'] for d in self.function_words_data])
        frequencies = np.array([d['frequency'] for d in self.function_words_data])
        
        corr_coef, p_value = spearmanr(lengths, frequencies)
        
        return {
            'lengths': lengths,
            'frequencies': frequencies,
            'correlation': corr_coef,
            'p_value': p_value,
            'words': self.function_words_data
        }
    
    def plot_empirical_zipf(self, results, save_path=None):
        """Построение графика"""
        plt.style.use(PLOT_STYLE)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # График 1: Диаграмма рассеяния
        ax1.scatter(results['lengths'], results['frequencies'], alpha=0.6, s=100, c='blue')
        
        # Аннотации для некоторых слов
        for i, item in enumerate(results['words'][:10]):  # Первые 10 слов
            ax1.annotate(item['word'], 
                        (item['length'], item['frequency']),
                        xytext=(5, 5), textcoords='offset points',
                        fontsize=8, alpha=0.7)
        
        ax1.set_xlabel('Длина слова', fontsize=12)
        ax1.set_ylabel('Частота', fontsize=12)
        ax1.set_title(f'Эмпирический закон Ципфа - {LANGUAGES[self.language]}\n' + 
                     f'Корреляция: {results["correlation"]:.3f}', fontsize=14)
        ax1.grid(True, alpha=0.3)
        
        # График 2: Средняя частота по длинам
        length_freq = {}
        for item in results['words']:
            length = item['length']
            if length not in length_freq:
                length_freq[length] = []
            length_freq[length].append(item['frequency'])
        
        avg_lengths = sorted(length_freq.keys())
        avg_frequencies = [np.mean(length_freq[l]) for l in avg_lengths]
        
        ax2.plot(avg_lengths, avg_frequencies, 'ro-', markersize=8, linewidth=2)
        ax2.set_xlabel('Длина слова', fontsize=12)
        ax2.set_ylabel('Средняя частота', fontsize=12)
        ax2.set_title('Зависимость средней частоты от длины', fontsize=14)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=PLOT_DPI, bbox_inches='tight')
            print(f"График сохранен: {save_path}")
        
        plt.close()
    
    def generate_report(self, results):
        """Генерация отчета"""
        report = []
        report.append(f"=== ЭМПИРИЧЕСКИЙ ЗАКОН ЦИПФА - {LANGUAGES[self.language].upper()} ===\n")
        report.append(f"Проанализировано служебных слов: {len(results['words'])}\n")
        
        report.append("Таблица служебных слов:")
        report.append(f"{'№':>3} {'Слово':>10} {'Длина':>6} {'Частота':>10}")
        report.append("-" * 35)
        
        for i, item in enumerate(results['words'], 1):
            report.append(f"{i:>3} {item['word']:>10} {item['length']:>6} {item['frequency']:>10}")
        
        report.append(f"\nКоэффициент корреляции: {results['correlation']:.4f}")
        report.append(f"P-значение: {results['p_value']:.6f}")
        
        return "\n".join(report)
    
    def analyze(self):
        """Полный анализ"""
        print(f"\n--- Эмпирический закон Ципфа для {LANGUAGES[self.language]} ---")
        
        self.load_dictionary()
        self.extract_function_words()
        results = self.calculate_correlation()
        
        # Сохраняем график
        plot_path = PLOTS_DIR / f"empirical_zipf_{self.language}.png"
        self.plot_empirical_zipf(results, plot_path)
        
        # Сохраняем отчет
        report = self.generate_report(results)
        report_path = OUTPUT_DIR / f"empirical_zipf_report_{self.language}.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(report)
        print(f"\nОтчет сохранен: {report_path}")
        
        return results


def analyze_all_languages():
    """Анализ для всех языков"""
    all_results = {}
    
    for lang in LANGUAGES.keys():
        analyzer = EmpiricalZipfAnalyzer(lang)
        all_results[lang] = analyzer.analyze()
    
    return all_results


if __name__ == "__main__":
    analyze_all_languages()