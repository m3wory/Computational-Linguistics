"""Анализ закона Ципфа"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from config import *


class ZipfAnalyzer:
    """Анализ закона Ципфа"""
    
    def __init__(self, language):
        self.language = language
        self.word_counts = None
        self.sorted_words = None
        
    def load_dictionary(self):
        """Загрузка частотного словаря"""
        dict_path = FREQ_DICT_DIR / f"{self.language}_dictionary.json"
        with open(dict_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.word_counts = data['word_counts']
        # Сортируем по частоте (от большей к меньшей)
        self.sorted_words = sorted(self.word_counts.items(), key=lambda x: x[1], reverse=True)
        
    def calculate_zipf(self, top_n=TOP_WORDS_ZIPF):
        """Расчет показателей закона Ципфа"""
        if not self.sorted_words:
            self.load_dictionary()
        
        # Берем top_n самых частых слов
        words = self.sorted_words[:top_n]
        
        ranks = np.arange(1, len(words) + 1)
        frequencies = np.array([count for _, count in words])
        
        # Вычисляем произведение f*r
        products = frequencies * ranks
        
        # Средний коэффициент Ципфа
        zipf_coefficient = np.mean(products)
        
        # Стандартное отклонение (для оценки разброса)
        std_deviation = np.std(products)
        
        return {
            'ranks': ranks,
            'frequencies': frequencies,
            'products': products,
            'coefficient': zipf_coefficient,
            'std': std_deviation,
            'words': [word for word, _ in words]
        }
    
    def plot_zipf(self, results, save_path=None):
        """Построение графика закона Ципфа"""
        plt.style.use(PLOT_STYLE)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # График 1: Частота от ранга (логарифмический масштаб)
        ax1.loglog(results['ranks'], results['frequencies'], 'bo-', markersize=4, linewidth=1)
        ax1.set_xlabel('Ранг (r)', fontsize=12)
        ax1.set_ylabel('Частота (f)', fontsize=12)
        ax1.set_title(f'Закон Ципфа - {LANGUAGES[self.language]}\n(логарифмическая шкала)', fontsize=14)
        ax1.grid(True, alpha=0.3)
        
        # Теоретическая кривая Ципфа
        theoretical = results['coefficient'] / results['ranks']
        ax1.loglog(results['ranks'], theoretical, 'r--', linewidth=2, label=f'Теория (c={results["coefficient"]:.0f})')
        ax1.legend()
        
        # График 2: Произведение f*r
        ax2.plot(results['ranks'], results['products'], 'go-', markersize=4, linewidth=1)
        ax2.axhline(y=results['coefficient'], color='r', linestyle='--', linewidth=2, 
                    label=f'Средний коэффициент c={results["coefficient"]:.0f}')
        ax2.set_xlabel('Ранг (r)', fontsize=12)
        ax2.set_ylabel('Произведение f·r', fontsize=12)
        ax2.set_title(f'Проверка формулы f·r = c', fontsize=14)
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=PLOT_DPI, bbox_inches='tight')
            print(f"График сохранен: {save_path}")
        
        plt.close()
        
    def generate_report(self, results):
        """Генерация текстового отчета"""
        report = []
        report.append(f"=== ЗАКОН ЦИПФА - {LANGUAGES[self.language].upper()} ===\n")
        report.append(f"Проанализировано слов: {len(results['ranks'])}\n")
        report.append(f"Коэффициент Ципфа (c): {results['coefficient']:.2f}")
        report.append(f"Стандартное отклонение: {results['std']:.2f}")
        report.append(f"Коэффициент вариации: {(results['std'] / results['coefficient'] * 100):.2f}%\n")
        
        # Примеры для первых 10 слов
        report.append("Таблица расчетов (первые 10 слов):")
        report.append(f"{'Ранг':>5} {'Слово':>15} {'Частота':>10} {'f·r':>10}")
        report.append("-" * 45)
        
        for i in range(min(10, len(results['ranks']))):
            rank = results['ranks'][i]
            word = results['words'][i]
            freq = results['frequencies'][i]
            prod = results['products'][i]
            report.append(f"{rank:>5} {word:>15} {freq:>10} {prod:>10.0f}")
        
        return "\n".join(report)
    
    def analyze(self):
        """Полный анализ"""
        print(f"\n--- Анализ закона Ципфа для {LANGUAGES[self.language]} ---")
        
        self.load_dictionary()
        results = self.calculate_zipf()
        
        # Сохраняем график
        plot_path = PLOTS_DIR / f"zipf_{self.language}.png"
        self.plot_zipf(results, plot_path)
        
        # Сохраняем отчет
        report = self.generate_report(results)
        report_path = OUTPUT_DIR / f"zipf_report_{self.language}.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(report)
        print(f"\nОтчет сохранен: {report_path}")
        
        return results


def analyze_all_languages():
    """Анализ для всех языков"""
    all_results = {}
    
    for lang in LANGUAGES.keys():
        analyzer = ZipfAnalyzer(lang)
        all_results[lang] = analyzer.analyze()
    
    return all_results


if __name__ == "__main__":
    analyze_all_languages()