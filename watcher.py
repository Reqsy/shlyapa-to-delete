import os
import pickle
import threading
import time
from queue import Queue


class DirectoryWatcher:
    def __init__(self, directory_path):
        self.directory_path = directory_path
        self.files_info = {}
        self.load_files_info()
        self.file_q = Queue()

    def load_files_info(self):
        try:
            with open('files_info.pickle', 'rb') as f:
                self.files_info = pickle.load(f)
        except FileNotFoundError:
            pass

    def save_files_info(self):
        with open('files_info.pickle', 'wb') as f:
            pickle.dump(self.files_info, f)

    def process_new_files(self):
        for root, dirs, files in os.walk(self.directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                if file.endswith((".pdf", ".odt", ".rtf", ".docx", ".doc")):
                    if file_path not in self.files_info:
                        try:
                            # Получаем метаданные файла
                            file_stat = os.stat(file_path)
                            file_metadata = {
                                'filename': file,
                                'path': file_path,
                                'created_at': file_stat.st_ctime
                            }
                            # Сохраняем метаданные файла в словаре
                            self.files_info[file_path] = file_metadata
                            self.file_q.put(file_path)
                            print(f"Найден новый файл: {file_path}")
                        except Exception as e:
                            print(f"Ошибка при обработке файла {file_path}: {e}")

    def add_file_to_info(self, file_path):
        print("Добавляю")
        print(file_path)
        if os.path.exists(file_path):
            try:
                # Получаем метаданные файла
                file_stat = os.stat(file_path)
                file_metadata = {
                    'filename': os.path.basename(file_path),
                    'path': file_path,
                    'created_at': file_stat.st_ctime
                }
                # Сохраняем метаданные файла в словаре
                self.files_info[file_path] = file_metadata
                print(f"Файл успешно добавлен в список: {file_path}")
            except Exception as e:
                print(f"Ошибка при добавлении файла в список: {e}")
        else:
            print("Файл не существует.")

    def watch_directory(self):
        while True:
            self.process_new_files()
            self.save_files_info()
            time.sleep(1)  # проверка каждую минуту

    def start_watching(self):
        watcher_thread = threading.Thread(target=self.watch_directory)
        watcher_thread.daemon = True
        watcher_thread.start()


if __name__ == '__main__':
    # Пример использования
    directory_to_watch = '/путь/к/директории'
    watcher = DirectoryWatcher(directory_to_watch)
    watcher.start_watching()
