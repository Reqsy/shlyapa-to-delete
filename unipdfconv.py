import platform
import subprocess
import os
from docx2pdf import convert
import tempfile


class Unipdfconv():
    def __init__(self):
        self.libreoffice = False
        self._set_libreoffice_path()
        self.tmp_dir = tempfile.TemporaryDirectory().name

    def _set_libreoffice_path(self):
        # Пути к LibreOffice в разных операционных системах
        current_path = os.environ.get("PATH", "")

        # Добавление пути к LibreOffice в переменные среды PATH

        libreoffice_paths = {
            'nt': 'C:\\Program Files\\LibreOffice\\program',
            'posix': '/usr/bin/libreoffice'
        }

        # Получаем имя операционной системы
        os_name = os.name

        if os_name in libreoffice_paths:
            path = libreoffice_paths[os_name]
            if os.path.exists(path):

                libreoffice_path = path
            else:
                print("LibreOffice не найден.")
                return
        else:
            print("Данная операционная система не поддерживается.")
            return

        if libreoffice_path not in current_path:
            os.environ["PATH"] = f"{libreoffice_path};{current_path}"
            self.libreoffice = True
            print("Путь к LibreOffice добавлен в переменные среды PATH.")
        else:
            self.libreoffice = True
            print("Путь к LibreOffice уже присутствует в переменных среды PATH.")

    def _detect_os(self):
        system = platform.system()
        if system == "Windows":
            return "Windows"
        elif system == "Linux":
            return "Linux"
        else:
            return "Other"

    def _docx_win(self, file_path):
        return convert(str(file_path))

    def _soffice(self, file_path, out_dir=None):
        try:
            if not out_dir:
                out_dir = self.tmp_dir
            path = os.path.join(out_dir, (os.path.splitext(os.path.basename(file_path))[0] + ".pdf"))
            if os.path.exists(path):
                print("Существует")
                return path
            subprocess.run(['soffice', '--headless', '--convert-to', 'pdf', file_path, '--outdir', out_dir],
                           check=True)
            print("Conversion successful!")
            # path = os.path.splitext(file_path)[0] + ".pdf"

            print(path)
            return path
        except subprocess.CalledProcessError as e:
            print("Conversion failed:", e)

    def convert_to_pdf(self, file_path):
        if self.libreoffice:
            return self._soffice(file_path)
        elif platform.system() == "Windows":
            return self._docx_win(file_path)
        else:
            print("Не поддерживается конвертация, установите LibreOffice")
