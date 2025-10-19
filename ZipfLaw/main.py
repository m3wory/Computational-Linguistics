"""Главный скрипт для запуска всех статистических анализов"""

import argparse
from zipf_law import ZipfAnalyzer
from empirical_zipf import EmpiricalZipfAnalyzer
from juyan_coefficient import JuyanAnalyzer
from config import LANGUAGES


def analyze_language(language, tasks=None):
    """Анализ для одного языка"""
    if tasks is None:
        tasks = [1, 2, 3]
    
    print(f"\n{'='*60}")
    print(f"{LANGUAGES[language].upper()}")
    print(f"{'='*60}")
    
    if 1 in tasks:
        print("\nЗАДАНИЕ 1: ЗАКОН ЦИПФА")
        zipf = ZipfAnalyzer(language)
        zipf.analyze()
    
    if 2 in tasks:
        print("\nЗАДАНИЕ 2: ЭМПИРИЧЕСКИЙ ЗАКОН ЦИПФА")
        empirical = EmpiricalZipfAnalyzer(language)
        empirical.analyze()
    
    if 3 in tasks:
        print("\nЗАДАНИЕ 3: КОЭФФИЦИЕНТ ЖУЙАНА")
        juyan = JuyanAnalyzer(language)
        juyan.analyze()


def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(
        description='Статистический анализ частотных словарей'
    )
    
    parser.add_argument(
        '--language',
        choices=list(LANGUAGES.keys()) + ['all'],
        default='all',
        help='Язык для анализа (по умолчанию: all)'
    )
    
    parser.add_argument(
        '--tasks',
        nargs='+',
        type=int,
        choices=[1, 2, 3],
        default=[1, 2, 3],
        help='Номера заданий для выполнения'
    )
    
    args = parser.parse_args()
    
    print("="*60)
    print("СТАТИСТИЧЕСКИЙ АНАЛИЗ ЧАСТОТНЫХ СЛОВАРЕЙ")
    print("="*60)
    
    try:
        if args.language == 'all':
            for lang in LANGUAGES.keys():
                analyze_language(lang, args.tasks)
        else:
            analyze_language(args.language, args.tasks)
        
        print("\n" + "="*60)
        print("ЗАВЕРШЕНО")
        print(f"Результаты: output/ (графики, таблицы, отчеты)")
        print("="*60)
        
    except Exception as e:
        print(f"\nОШИБКА: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()