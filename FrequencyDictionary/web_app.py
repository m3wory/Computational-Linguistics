"""Веб интерфейс для частотного словаря"""

import os
import tempfile
from pathlib import Path
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from werkzeug.utils import secure_filename

from frequency_dictionary import FrequencyDictionary
from config import DEFAULT_DATA_DIR, DEFAULT_DICT_DIR, LANGUAGES, WEB_CONFIG, WEB_MESSAGES, MAX_DISPLAY_WORDS, MAX_SEARCH_RESULTS


class FrequencyDictionaryWeb:
    """Веб интерфейс для частотного словаря"""
    
    def __init__(self, data_dir=DEFAULT_DATA_DIR, dict_dir=DEFAULT_DICT_DIR):
        self.app = Flask(__name__)
        self.app.secret_key = 'frequency_dictionary_secret_key_2024'
        self.fd = FrequencyDictionary(data_dir, dict_dir)
        self.current_language = None
        
        # Настраиваем маршруты
        self.setup_routes()
    
    def setup_routes(self):
        """Настройка маршрутов Flask"""
        
        @self.app.route('/')
        def index():
            """Главная страница"""
            available_dicts = self.get_available_dictionaries()
            return render_template('index.html', 
                                 languages=LANGUAGES,
                                 available_dicts=available_dicts,
                                 current_language=self.current_language,
                                 messages=WEB_MESSAGES,
                                 config=WEB_CONFIG)
        
        @self.app.route('/load_language', methods=['POST'])
        def load_language():
            """Загрузка словаря языка"""
            language = request.form.get('language')
            if language and self.fd.load_dictionary(language):
                self.current_language = language
                flash(WEB_MESSAGES['dictionary_loaded'].format(
                    language=LANGUAGES.get(language, language)), 'success')
            else:
                flash('Ошибка загрузки словаря', 'error')
            return redirect(url_for('index'))
        
        @self.app.route('/stats')
        def stats():
            """API для получения статистики"""
            if not self.fd.current_data:
                return jsonify({'error': 'Словарь не загружен'})
            
            return jsonify({
                'language': LANGUAGES.get(self.current_language, self.current_language),
                'total_words': self.fd.current_data['total_words'],
                'unique_words': self.fd.current_data['unique_words']
            })
        
        @self.app.route('/words')
        def words():
            """API для получения слов"""
            if not self.fd.current_data:
                return jsonify({'error': 'Словарь не загружен'})
            
            # Параметры запроса
            sort_by = request.args.get('sort', 'alphabet')  # alphabet, frequency
            reverse = request.args.get('reverse', 'false').lower() == 'true'
            limit = int(request.args.get('limit', MAX_DISPLAY_WORDS))
            search = request.args.get('search', '').strip()
            
            words = list(self.fd.current_data['word_counts'].items())
            
            # Фильтрация по поиску
            if search:
                words = [(w, c) for w, c in words if w.startswith(search.lower())]
                limit = min(limit, MAX_SEARCH_RESULTS)
            
            # Сортировка
            if sort_by == 'frequency':
                words.sort(key=lambda x: x[1], reverse=not reverse)
            else:  # alphabet
                import locale
                words.sort(key=lambda x: locale.strxfrm(x[0]), reverse=reverse)
            
            # Ограничиваем результат
            words = words[:limit]
            
            return jsonify({
                'words': [{'word': w, 'count': c} for w, c in words],
                'total_found': len(words),
                'search_term': search
            })
        
        @self.app.route('/word_action', methods=['POST'])
        def word_action():
            """API для действий со словами"""
            if not self.fd.current_data:
                return jsonify({'error': 'Словарь не загружен'})
            
            action = request.form.get('action')
            
            try:
                if action == 'add':
                    word = request.form.get('word', '').strip()
                    if word:
                        success = self.fd.add_word(word)
                        return jsonify({
                            'success': success,
                            'message': f"Слово '{word}' добавлено" if success else "Ошибка добавления"
                        })
                
                elif action == 'delete':
                    word = request.form.get('word', '').strip()
                    if word:
                        # Для веб интерфейса удаляем без подтверждения
                        word = word.lower().strip()
                        if word in self.fd.current_data['word_counts']:
                            count = self.fd.current_data['word_counts'].pop(word)
                            self.fd.current_data['total_words'] -= count
                            self.fd.current_data['unique_words'] = len(self.fd.current_data['word_counts'])
                            self.fd.save_current()
                            return jsonify({
                                'success': True,
                                'message': f"Слово '{word}' удалено"
                            })
                        else:
                            return jsonify({
                                'success': False,
                                'message': f"Слово '{word}' не найдено"
                            })
                
                elif action == 'correct':
                    wrong = request.form.get('wrong_word', '').strip()
                    correct = request.form.get('correct_word', '').strip()
                    if wrong and correct:
                        success = self.fd.correct_word(wrong, correct)
                        return jsonify({
                            'success': success,
                            'message': f"'{wrong}' → '{correct}'" if success else "Ошибка исправления"
                        })
                
                return jsonify({'error': 'Неверное действие'})
                
            except Exception as e:
                return jsonify({'error': str(e)})
        
        @self.app.route('/upload_text', methods=['POST'])
        def upload_text():
            """Загрузка текстового файла"""
            if not self.fd.current_data:
                return jsonify({'error': 'Словарь не загружен'})
            
            if 'file' not in request.files:
                return jsonify({'error': 'Файл не выбран'})
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'Файл не выбран'})
            
            if not file.filename.lower().endswith('.txt'):
                return jsonify({'error': 'Поддерживаются только .txt файлы'})
            
            try:
                # Сохраняем во временный файл
                with tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', delete=False, encoding='utf-8') as tmp_file:
                    content = file.read().decode('utf-8')
                    tmp_file.write(content)
                    tmp_file_path = tmp_file.name
                
                # Обрабатываем файл
                old_total = self.fd.current_data['total_words']
                old_unique = self.fd.current_data['unique_words']
                
                success = self.fd.add_text_file(tmp_file_path)
                
                # Удаляем временный файл
                os.unlink(tmp_file_path)
                
                if success:
                    new_total = self.fd.current_data['total_words']
                    new_unique = self.fd.current_data['unique_words']
                    
                    return jsonify({
                        'success': True,
                        'message': 'Файл обработан успешно',
                        'stats': {
                            'words_added': new_total - old_total,
                            'unique_added': new_unique - old_unique,
                            'total_words': new_total,
                            'unique_words': new_unique
                        }
                    })
                else:
                    return jsonify({'error': 'Ошибка обработки файла'})
                    
            except Exception as e:
                # Удаляем временный файл при ошибке
                if 'tmp_file_path' in locals():
                    try:
                        os.unlink(tmp_file_path)
                    except:
                        pass
                return jsonify({'error': str(e)})
    
    def get_available_dictionaries(self):
        """Получение списка доступных словарей"""
        available = {}
        for lang_code, lang_name in LANGUAGES.items():
            dict_path = self.fd.get_dictionary_path(lang_code)
            available[lang_code] = {
                'name': lang_name,
                'exists': dict_path.exists(),
                'path': str(dict_path)
            }
        return available
    
    def run(self, host=None, port=None, debug=None):
        """Запуск веб сервера"""
        host = host or WEB_CONFIG['host']
        port = port or WEB_CONFIG['port']  
        debug = debug or WEB_CONFIG['debug']
        
        print(f"🌐 Веб интерфейс запущен: http://{host}:{port}")
        self.app.run(host=host, port=port, debug=debug)


def create_web_app(data_dir=DEFAULT_DATA_DIR, dict_dir=DEFAULT_DICT_DIR):
    """Фабрика для создания веб приложения"""
    web_app = FrequencyDictionaryWeb(data_dir, dict_dir)
    return web_app