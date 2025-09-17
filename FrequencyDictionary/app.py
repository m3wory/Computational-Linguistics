"""Главный файл приложения частотного словаря"""

import argparse
from frequency_dictionary import FrequencyDictionary
from config import LANGUAGES, MESSAGES, CLI_HELP, MAIN_MENU_ITEMS, NUMBER_FORMAT


def create_mode(fd: FrequencyDictionary, args):
    """Режим создания словарей"""
    if args.language == 'all':
        print("Создание словарей для всех языков...")
        fd.create_all(args.force)
        
        # Показываем итоговую статистику
        print("\n" + "="*40)
        print(MESSAGES['final_stats_title'])
        print("="*40)
        for lang in LANGUAGES:
            if fd.load_dictionary(lang):
                name = LANGUAGES[lang]
                total = NUMBER_FORMAT.format(fd.current_data['total_words'])
                unique = NUMBER_FORMAT.format(fd.current_data['unique_words'])
                print(MESSAGES['stats_format'].format(name=name, total=total, unique=unique))
    else:
        fd.create_dictionary(args.language, args.force)


def interface_mode(fd: FrequencyDictionary, args):
    """Режим интерфейса"""
    if args.language:
        # Прямой запуск для языка
        if fd.load_dictionary(args.language):
            language_menu(fd)
        else:
            lang_name = LANGUAGES.get(args.language, args.language)
            print(f"\n{MESSAGES['dictionary_not_found'].format(language=lang_name)}")
            print("Создайте его командой: python app.py create")
    else:
        # Главное меню
        main_menu(fd)


def web_mode(args):
    """Режим веб интерфейса"""
    try:
        from web_app import create_web_app
        web_app = create_web_app()
        
        host = getattr(args, 'host', None) or '127.0.0.1'
        port = getattr(args, 'port', None) or 5000
        debug = getattr(args, 'debug', False)
        
        web_app.run(host=host, port=port, debug=debug)
        
    except ImportError as e:
        print(f"Ошибка импорта Flask: {e}")
        print("Установите Flask: pip install flask")
    except Exception as e:
        print(f"Ошибка запуска веб интерфейса: {e}")


def main_menu(fd: FrequencyDictionary):
    """Главное меню выбора языка"""
    while True:
        print(f"\n{MESSAGES['app_title']}")
        print(MESSAGES['choose_language'])
        
        menu_items = list(LANGUAGES.items())
        for i, (code, name) in enumerate(menu_items, 1):
            print(f"{i}. {name}")
        print(f"0. {MESSAGES['exit_option']}")
        
        try:
            menu_range = f"0-{len(menu_items)}"
            choice = input(f"\n{MESSAGES['enter_choice'].format(range=menu_range)}").strip()
            
            if choice == '0':
                break
            
            choice_num = int(choice) - 1
            if 0 <= choice_num < len(menu_items):
                lang_code = menu_items[choice_num][0]
                if fd.load_dictionary(lang_code):
                    language_menu(fd)
                else:
                    lang_name = LANGUAGES[lang_code]
                    print(f"\n{MESSAGES['dictionary_not_found'].format(language=lang_name)}")
                    print("Создайте его командой: python app.py create")
                    input(MESSAGES['continue_prompt'])
            else:
                print(MESSAGES['invalid_choice'])
                
        except (ValueError, IndexError):
            print(MESSAGES['invalid_input'])
        except KeyboardInterrupt:
            break


def language_menu(fd: FrequencyDictionary):
    """Меню для выбранного языка"""
    lang_name = LANGUAGES[fd.current_language].upper()
    
    while True:
        print(f"\n=== МЕНЮ: {lang_name} ===")
        
        for i, item in enumerate(MAIN_MENU_ITEMS, 1):
            print(f"{i:2d}. {item}")
        print(f" 0. {MESSAGES['back_option']}")
        
        try:
            menu_range = f"0-{len(MAIN_MENU_ITEMS)}"
            choice = input(f"\n{MESSAGES['enter_choice'].format(range=menu_range)}").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                fd.stats()
            elif choice == '2':
                fd.display_sorted(by_freq=False, reverse=False)
            elif choice == '3':
                fd.display_sorted(by_freq=False, reverse=True)
            elif choice == '4':
                fd.display_sorted(by_freq=True, reverse=False)
            elif choice == '5':
                fd.display_sorted(by_freq=True, reverse=True)
            elif choice == '6':
                pattern = input(MESSAGES['enter_pattern']).strip()
                if pattern:
                    fd.search(pattern)
            elif choice == '7':
                wrong = input(MESSAGES['enter_wrong_word']).strip()
                correct = input(MESSAGES['enter_correct_word']).strip()
                if wrong and correct:
                    fd.correct_word(wrong, correct)
            elif choice == '8':
                word = input(MESSAGES['enter_word_to_delete']).strip()
                if word:
                    fd.delete_word(word)
            elif choice == '9':
                word = input(MESSAGES['enter_new_word']).strip()
                if word:
                    fd.add_word(word)
            elif choice == '10':
                file_path = input(MESSAGES['enter_file_path']).strip()
                if file_path:
                    fd.add_text_file(file_path)
            else:
                print(MESSAGES['invalid_choice'])
                
            if choice != '0':
                input(f"\n{MESSAGES['continue_prompt']}")
                
        except (ValueError, IndexError):
            print(MESSAGES['invalid_input'])
        except KeyboardInterrupt:
            break


def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(
        description=CLI_HELP['main_description'],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=CLI_HELP['examples']
    )
    
    subparsers = parser.add_subparsers(dest='mode', help='Режим работы')
    
    # Режим создания
    create_parser = subparsers.add_parser('create', help=CLI_HELP['create_help'])
    create_parser.add_argument(
        '--language', 
        choices=list(LANGUAGES.keys()) + ['all'],
        default='all',
        help=CLI_HELP['language_help']
    )
    create_parser.add_argument(
        '--force', 
        action='store_true',
        help=CLI_HELP['force_help']
    )
    
    # Режим интерфейса
    interface_parser = subparsers.add_parser('interface', help=CLI_HELP['interface_help'])
    interface_parser.add_argument(
        '--language',
        choices=list(LANGUAGES.keys()),
        help=CLI_HELP['direct_language_help']
    )
    
    # Веб режим
    web_parser = subparsers.add_parser('web', help=CLI_HELP['web_help'])
    web_parser.add_argument(
        '--host',
        default='127.0.0.1',
        help='Хост для веб сервера (по умолчанию: 127.0.0.1)'
    )
    web_parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Порт для веб сервера (по умолчанию: 5000)'
    )
    web_parser.add_argument(
        '--debug',
        action='store_true',
        help='Режим отладки Flask'
    )
    
    args = parser.parse_args()
    
    # Если режим не указан, запускаем интерфейс
    if not args.mode:
        args.mode = 'interface'
        args.language = None
    
    fd = FrequencyDictionary()
    
    try:
        if args.mode == 'create':
            create_mode(fd, args)
        elif args.mode == 'interface':
            interface_mode(fd, args)
        elif args.mode == 'web':
            web_mode(args)
    except KeyboardInterrupt:
        print(f"\n\n{MESSAGES['keyboard_interrupt']}")
    except Exception as e:
        print(f"\n{MESSAGES['error_occurred'].format(error=e)}")


if __name__ == "__main__":
    main()