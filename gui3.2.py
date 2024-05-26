import re
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, font
import os
import fitz
from unipdfconv import Unipdfconv
from PIL import Image, ImageTk
import shutil
from watcher import DirectoryWatcher
import datetime

converter = Unipdfconv()
images = []
raw_images = []
selected_file = None  # Переменная для хранения пути к выбранному файлу
if not os.path.exists("Документы"):
    os.makedirs("Документы")
os.chdir("Документы")
current_directory = os.getcwd()  # Переменная для хранения текущей директории
working_file_path = ""
In_work = False
folders = ["Конституция РФ", "Федеральный конституционный закон", "Федеральный закон", "Указ Президента РФ",
           "Постановление Правительства РФ", "Нормативный акт министерства или ведомства"]

npa_hierarchy = {
    "Конституция РФ": 1,
    "Федеральный конституционный закон": 2,
    "Федеральный закон": 3,
    "Указ Президента РФ": 4,
    "Постановление Правительства РФ": 5,
    "Нормативный акт министерства или ведомства": 6
}


def get_sort_key(npa):
    return npa_hierarchy.get(npa, float('inf'))  # Если НПА не найден, присваивается бесконечность


sorted_npa_list = sorted(folders, key=get_sort_key)
folders = [
    f"{get_sort_key(npa)}. {npa}" for npa in sorted_npa_list
]

def update_npa_list():
    global sorted_npa_list



def create_dirs():
    global folders
    cd = os.getcwd()
    for folder in folders:
        if not os.path.exists(os.path.join(cd, folder)):
            os.makedirs(folder)


create_dirs()


def scan_directory(directory=None, element_id=None):
    contents = os.listdir(directory)
    contents.sort(key=lambda x: (os.path.isdir(os.path.join(current_directory, x)), x))

    # Сортируем содержимое: сначала директории, потом файлы
    contents.sort(key=lambda x: (os.path.isdir(os.path.join(current_directory, x)), x))
    for item in contents:
        item_path = os.path.join(current_directory, item)
        if os.path.isdir(item_path):
            # Если элемент является директорией, добавляем метку и рекурсивно отображаем ее содержимое
            content_listbox.insert(element_id + 1, f"         📁 {item}")
        elif item.endswith((".pdf", ".odt", ".rtf", ".docx", ".doc")):
            # Если элемент является файлом, добавляем метку с его именем
            content_listbox.insert(element_id + 1, f"         📄 {item}")
    # root.after(0, font_listbox)


def show_directory_contents(directory=None):
    global current_directory

    if directory is not None:
        current_directory = directory

    # Очищаем содержимое списка файлов
    content_listbox.delete(0, tk.END)

    # Выводим текущую директорию
    # content_listbox.insert(tk.END, f"Текущая директория: {current_directory}")

    # Получаем содержимое текущей директории
    contents = os.listdir(current_directory)
    sorted_npa_list = sorted(contents, key=get_sort_key)

    for item in sorted_npa_list:
        item_path = os.path.join(current_directory, item)
        if os.path.isdir(item_path):
            # Если элемент является директорией, добавляем метку и рекурсивно отображаем ее содержимое
            content_listbox.insert(tk.END, f"📁 {item}")
        elif item.endswith((".pdf", ".odt", ".rtf", ".docx", ".doc")):
            # Если элемент является файлом, добавляем метку с его именем
            content_listbox.insert(tk.END, f"📄 {item}")


def close_folder(el_id):
    while content_listbox.get(el_id + 1).startswith(f"         "):
        content_listbox.delete(el_id + 1)


def user_choose_file():
    global working_file_path
    file_path = filedialog.askopenfilename()
    if not file_path:
        return False
    main_l_file.config(text=f'Выбранный файл: {os.path.basename(file_path)}')
    main_e_date.focus_set()
    working_file_path = file_path
    main_b_add.config(text="Добавить файл", command=add_file)
    root.after(1, lambda: preview_file(file_path))
    # shutil.copy(file_path, os.path.join(path, os.path.basename(file_path)))
    # messagebox.showinfo("Добавление файла", "Файл успешно добавлен")


invalid_chars = '<>:"/\\|?*'


def validate_number(event=None):
    global last_valid_value_num
    new_value = main_e_number.get()

    # Проверка на наличие запрещенных символов
    if any(char in invalid_chars for char in new_value):
        messagebox.showerror("Ошибка", f"Введены запрещенные символы: {invalid_chars}")
        main_e_number.delete(0, tk.END)  # Очищаем поле ввода при ошибке
        main_e_number.insert(0, last_valid_value_num)  # Возвращаем последнее допустимое значение
        if new_value != "о создании..." and (len(new_value) > 0):
            return True
    else:
        last_valid_value_num = new_value
        if new_value != "о создании..." and (len(new_value) > 0):
            return True


def validate_name(event=None):
    global last_valid_value
    new_value = main_e_name.get()

    # Проверка на наличие запрещенных символов
    if any(char in invalid_chars for char in new_value):
        messagebox.showerror("Ошибка", f"Введены запрещенные символы: {invalid_chars}")
        main_e_name.delete(0, tk.END)  # Очищаем поле ввода при ошибке
        main_e_name.insert(0, last_valid_value)  # Возвращаем последнее допустимое значение
        if new_value != "О создании..." and (len(new_value) > 0):
            return True
    else:
        last_valid_value = new_value
        if new_value != "О создании..." and (len(new_value) > 0):
            return True


def select_file(event):
    global selected_file
    element_id = content_listbox.curselection()[0]
    selected_file = content_listbox.get(element_id)
    if selected_file.startswith("▼"):
        name = content_listbox.get(element_id)
        close_folder(element_id)
        content_listbox.delete(element_id)  # Удаляем выбранный элемент
        content_listbox.insert(element_id, name[1:])
    elif selected_file.startswith("📁"):
        directory = selected_file.split(maxsplit=1)[1]
        name = content_listbox.get(element_id)
        content_listbox.delete(element_id)  # Удаляем выбранный элемент
        content_listbox.insert(element_id, "▼" + name)
        scan_directory(directory, element_id)

    else:
        file_path = get_file_path_from_listbox(element_id)
        preview_file(file_path)


def resize_images(event=None):
    global images, raw_images

    # Проверяем, есть ли изображения для изменения размеров
    if images:
        # Получаем новые размеры холста
        canvas_width = event.width
        canvas_height = event.height

        # Очищаем список изображений
        images.clear()

        # Обновляем размеры изображений с сохранением пропорций
        for image in raw_images:
            width, height = canvas_width, int((canvas_width / image.width) * image.height)
            resized_image = image.resize((width, height))
            photo = ImageTk.PhotoImage(resized_image)
            images.append(photo)

        # Отображаем все страницы на холсте
        canvas.delete("all")
        y_offset = 0
        for photo in images:
            canvas.create_image(0, y_offset, anchor=tk.NW, image=photo)
            y_offset += photo.height()
        canvas.config(scrollregion=canvas.bbox("all"))
        # Перемещаем прокрутку в начало
        canvas.yview_moveto(0.0)


def preview_file(file_path):
    global images, raw_images, converter  # Объявляем глобальные изображения

    if not file_path.endswith(".pdf"):
        # main_l_file.config(text="Идёт преобразование")
        root.title("Идёт преобразование")
        file_path = converter.convert_to_pdf(file_path)
        watcher.add_file_to_info(file_path)
    if os.path.isfile(file_path) and (file_path.endswith(".pdf") or file_path.endswith(".PDF")):
        # Открываем PDF файл
        doc = fitz.open(file_path)
        root.title("Файловый менеджер")
        canvas.delete("all")
        # Очищаем список изображений
        images.clear()
        raw_images.clear()
        # Отображаем все страницы PDF файла
        for page_number in range(len(doc)):
            page = doc.load_page(page_number)
            pix = page.get_pixmap()
            image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            width, height = canvas.winfo_width(), int((canvas.winfo_width() / image.width) * image.height)
            image = image.resize((width, height))
            raw_images.append(image)
            photo = ImageTk.PhotoImage(image)
            images.append(photo)  # Добавляем фото в список

        doc.close()

        # Устанавливаем размер холста в соответствии с размерами первой страницы

        # Отображаем все страницы на холсте
        y_offset = 0
        for photo in images:
            canvas.create_image(0, y_offset, anchor=tk.NW, image=photo)
            y_offset += photo.height()
        canvas.config(scrollregion=canvas.bbox("all"))
        # Перемещаем прокрутку в начало
        canvas.yview_moveto(0.0)

    else:
        print("Указанный файл не является PDF файлом или не существует.")


def search_files(event=None):
    search_term = []
    date = main_e_date.get().lower()
    number = main_e_number.get().lower()
    name = main_e_name.get().lower()
    dir = combo.get()

    if dir:
        dir = os.path.join(current_directory, dir)
    else:
        dir = current_directory
    if number != "1_1234" and (len(number) > 0):
        search_term.append(number)
    if date != "дд.мм.гггг" and (len(date) > 0):
        search_term.append(date)
    if name != "о создании..." and (len(name) > 0):
        search_term.append(name)
    if search_term:
        matches = []
        for parent, dirs, files in os.walk(dir):
            for file in files:
                if all(term.lower() in file.lower() for term in search_term):
                    if parent not in matches:
                        matches.append(parent)
                    matches.append(file)

        show_search_results(matches)
    else:
        show_directory_contents()


def show_search_results(matches):
    content_listbox.delete(0, tk.END)
    for item in matches:
        item_path = os.path.join(current_directory, item)
        if os.path.isdir(item_path):
            content_listbox.insert(tk.END, f"▼📁 {os.path.split(item)[1]}")
        else:
            content_listbox.insert(tk.END, f"         📄 {item}")


def on_mousewheel(event):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


def show_context_menu(event):
    element_id = content_listbox.curselection()[0]
    selected_file = content_listbox.get(element_id)
    if selected_file.startswith(("📄", "         📄")):
        context_menu.post(event.x_root, event.y_root)

    # Получаем индекс выбранного элемента


def add_file():
    global In_work, working_file_path
    if validate_name() and validate_number() and validate_date():
        extention = os.path.splitext(os.path.basename(working_file_path))[1]
        name = f'{main_e_date.get()} №{main_e_number.get()} {combo.get().split(". ",1)[1]} \'\'{main_e_name.get()}\'\''
        path_to_new_file = os.path.join(os.getcwd(), combo.get(), (name + extention))
        shutil.copy(working_file_path, path_to_new_file)
        watcher.add_file_to_info(path_to_new_file)
        clear_main()
        main_l_file.config(text="Успешно сохраненно!")
        working_file_path = ""
        In_work = False
        show_directory_contents()


def validate_date_format(date_str):
    """Проверка частичных форматов и полного формата даты."""
    if re.match(r"^(\d{1,2}(\.\d{0,2}(\.\d{0,4})?)?)?$", date_str):
        parts = date_str.split('.')
        if len(parts) > 1:
            if len(parts[0]) > 2 or len(parts[1]) > 2:
                return False
            day = int(parts[0]) if parts[0] else 1
            month = int(parts[1]) if parts[1] else 1
            if not (1 <= day <= 31 and 1 <= month <= 12):
                return False
        if len(parts) == 3 and len(parts[2]) == 4:
            day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
            try:
                datetime.date(year, month, day)
                return True
            except ValueError:
                return False
        return True
    return False


def validate_date(event=None):
    """Функция, вызываемая при каждом отпускании клавиши."""
    entry_value = main_e_date.get().replace('.', '')
    new_value = ""

    # Автоматическая расстановка точек
    for i, char in enumerate(entry_value):
        if i in [2, 4]:  # Позиции, где должны быть точки
            new_value += "."
        new_value += char

    # Ограничиваем длину строки до 10 символов (дд.мм.гггг)
    if len(new_value) > 10:
        new_value = new_value[:10]

    main_e_date.delete(0, tk.END)
    main_e_date.insert(0, new_value)

    # Проверка корректности даты
    if validate_date_format(new_value):
        main_e_date.config(bg="white")  # Корректный ввод
        if main_e_date.get() != "дд.мм.гггг":
            return True
    else:
        main_e_date.config(bg="red")  # Некорректный ввод
        return False


def on_new_file(file_path):
    global working_file_path

    def _reject():
        global In_work
        newfile_win.destroy()
        In_work = False

    def _add():
        global In_work, helper_window, working_file_path, folders
        newfile_win.destroy()
        preview_file(file_path)
        parent_dir = os.path.split(os.path.dirname(file_path))[1]
        main_l_file.config(text=f'Выбранный файл: {os.path.basename(file_path)}')
        working_file_path = file_path
        main_b_add.config(text="Добавить файл", command=add_file)
        if parent_dir in folders:
            combo.set(parent_dir)

        """rename(file_path)
        root.wait_window(helper_window)
        dir_path = os.path.abspath(filedialog.askdirectory(initialdir=os.getcwd()))
        shutil.move(working_file_path, os.path.join(dir_path, os.path.basename(working_file_path)))
        watcher.add_file_to_info(os.path.join(dir_path, os.path.basename(working_file_path)))
        messagebox.showinfo("Добавление файла", "Файл успешно добавлен")
        In_work = False
        show_directory_contents()"""

    newfile_win = tk.Toplevel(root)
    newfile_win.title("Переименование файла")
    name_label = tk.Label(newfile_win, text=f'Найден новый файл {os.path.basename(file_path)}')
    name_label.pack(pady=5, padx=10, side=tk.TOP, fill=tk.X)
    name_label = tk.Label(newfile_win, text=f'Добавить файл?')
    name_label.pack(pady=5, padx=10, side=tk.TOP, fill=tk.X)
    btn1 = tk.Button(newfile_win, text="Да", command=_add)
    btn1.pack(pady=5, padx=10, side=tk.LEFT, fill=tk.X, expand=True)
    btn2 = tk.Button(newfile_win, text="Нет", command=_reject)
    btn2.pack(pady=5, padx=10, side=tk.RIGHT, fill=tk.X, expand=True)


def get_file_path_from_listbox(element_id):
    name = content_listbox.get(element_id)
    if name.startswith("📄"):
        path = os.path.join(os.getcwd(), name.split("📄")[1][1:])
    else:
        while not content_listbox.get(element_id).startswith("▼"):
            element_id += -1

        path = os.path.join(os.getcwd(), content_listbox.get(element_id)[2:][1:], name.split("📄")[1][1:])

    return path


def rename_file_from_contex():
    element_id = content_listbox.curselection()[0]
    path = get_file_path_from_listbox(element_id)

    rename(path)


def rename(path_to_file):
    def _on_date_entry_change(event):
        entry_text = user_input1.get()
        if len(entry_text) == 2 or len(entry_text) == 5:
            user_input1.insert(tk.END, '.')

    def _write_to_file(name):
        global working_file_path, helper_window
        new_path_to_file = os.path.join(os.path.dirname(path_to_file), name)

        os.rename(path_to_file, new_path_to_file)
        watcher.add_file_to_info(new_path_to_file)
        working_file_path = new_path_to_file
        win.destroy()
        show_directory_contents()
        helper_window.destroy()
        messagebox.showinfo("Переименование", f'Файл переименован в {name}')

    pack_name = lambda: f'{combobox.get()} от {user_input1.get()} №{user_input2.get()} \'\'{user_input3.get()}\'\'{os.path.splitext(path_to_file)[1]}'

    win = tk.Toplevel(root)
    win.title("Переименование файла")
    options = ["Указ Президента", "Постановление правительства", "Федеральный закон"]
    combobox = ttk.Combobox(win, values=options)
    combobox.pack(pady=5, padx=10, side=tk.LEFT, fill=tk.X)

    label_input1 = tk.Label(win, text="Дата:")
    label_input1.pack(pady=5, padx=10, side=tk.LEFT, fill=tk.X)

    # Создаем два поля для пользовательского ввода
    # Создаем метки над полями ввода

    user_input1 = tk.Entry(win)
    user_input1.pack(pady=5, padx=10, side=tk.LEFT, fill=tk.X)
    user_input1.bind("<KeyRelease>", _on_date_entry_change)

    label_input2 = tk.Label(win, text="Номер:")
    label_input2.pack(pady=5, padx=10, side=tk.LEFT, fill=tk.X)

    # Добавляем символ "#" в поле ввода для "Название 2"
    user_input2 = tk.Entry(win)
    user_input2.pack(pady=5, padx=10, side=tk.LEFT, fill=tk.X)

    label_input3 = tk.Label(win, text="Название:")
    label_input3.pack(pady=5, padx=10, side=tk.LEFT, fill=tk.X)

    # Добавляем символ "#" в поле ввода для "Название 2"
    user_input3 = tk.Entry(win)
    user_input3.pack(pady=5, padx=10, side=tk.LEFT, fill=tk.X)
    btn_rename_files = tk.Button(win, text="Переименовать файл", command=lambda: _write_to_file(pack_name()))
    btn_rename_files.pack(pady=5, padx=10, side=tk.TOP, anchor="ne")
    preview_file(path_to_file)


"""def helper():
    if main_b_add.cget("text") == "Выбрать файл":
        hint = "Выберите файл для загрузки или для предпросмотра"
    elif main_e_date.get() == "дд.мм.гггг" or (len(main_e_date.get()) < 10):
        hint = "Введите корректную дату издания документа в формате:\"дд.мм.гггг\""
    elif main_e_number.get() == "1_1234" or main_e_name.get() == "О создании...":
        hint = "Введите номер и имя создаваемого документа"
    elif len(combo.get()) <= 0:
        hint = "Выберите вид документа"
    else:
        hint = "Сохраните документ"
    main_l_hint.config(text=hint)"""


def file_routine():
    global In_work, helper_window
    if not watcher.file_q.empty() and not In_work:
        In_work = True
        helper_window = tk.Toplevel(root)
        helper_window.withdraw()
        on_new_file(watcher.file_q.get())
    root.after(1000, file_routine)


def add_dir():
    def _create():
        os.mkdir(entrydir.get())
        dir_win.destroy()
        messagebox.showinfo("Создание папки", f'Успешно создано')
        show_directory_contents()

    dir_win = tk.Toplevel(root)
    labeld = tk.Label(dir_win, text="Введите название папки")
    entrydir = tk.Entry(dir_win)
    labeld.pack(pady=5, padx=10, side=tk.TOP, fill=tk.X)
    btn1 = tk.Button(dir_win, text="Создать", command=_create)
    btn1.pack(pady=5, padx=10, side=tk.BOTTOM, fill=tk.BOTH, expand=True)
    entrydir.pack(pady=5, padx=10, side=tk.BOTTOM, fill=tk.BOTH, expand=True)


def create_paned():
    paned_window = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
    paned_window.pack(fill=tk.BOTH, expand=True)


def get_folder_options():
    directories = [name for name in os.listdir(os.getcwd()) if os.path.isdir(os.path.join(os.getcwd(), name))]
    directories.append("<<Создать новый класс НПА>>")
    return directories


def set_placeholder1(event):
    if main_e_date.get() == "":
        main_e_date.config(fg="grey")
        main_e_date.insert(0, "дд.мм.гггг")


def remove_placeholder1(event):
    if main_e_date.get() == "дд.мм.гггг":
        main_e_date.delete(0, tk.END)
        main_e_date.config(fg="black")


def set_placeholder2(event):
    if main_e_number.get() == "":
        main_e_number.config(fg="grey")
        main_e_number.insert(0, "1_1234")


def remove_placeholder2(event):
    if main_e_number.get() == "1_1234":
        main_e_number.delete(0, tk.END)
        main_e_number.config(fg="black")


def set_placeholder3(event):
    if main_e_name.get() == "":
        main_e_name.config(fg="grey")
        main_e_name.insert(0, "О создании...")


def remove_placeholder3(event):
    if main_e_name.get() == "О создании...":
        main_e_name.delete(0, tk.END)
        main_e_name.config(fg="black")


def clear_main():
    main_l_file.config(text="")
    main_e_name.delete(0, tk.END)
    main_e_number.delete(0, tk.END)
    main_e_date.delete(0, tk.END)
    main_e_date.insert(0, "дд.мм.гггг")
    main_e_date.config(fg="grey")
    main_e_number.insert(0, "1_1234")
    main_e_number.config(fg="grey")
    main_e_name.insert(0, "О создании...")
    main_e_name.config(fg="grey")
    main_b_add.config(text="Выбрать файл", command=user_choose_file)
    canvas.delete("all")
    # Очищаем список изображений
    images.clear()
    combo.set("")


"""def font_listbox(event=None):
    max_width = content_listbox.winfo_width()
    max_height = content_listbox.winfo_height()

    items = content_listbox.get(0, tk.END)
    max_text_width = 0
    max_text_height = 0

    # Create a font object to measure text
    for size in range(10, 71):  # Try font sizes from 1 to 100
        temp_font = font.Font(family="Helvetica", size=size)
        for item in items:
            text_width = temp_font.measure(item)
            text_height = temp_font.metrics("linespace")
            max_text_width = max(max_text_width, text_width)
            max_text_height = max(max_text_height, text_height)

        if max_text_width > max_width or max_text_height * len(items) > max_height:
            # If the text exceeds the size of the listbox, we stop
            break

    # Set the font to the last fitting size
    final_font_size = max(1, size - 1)
    new_font = ("Helvetica", final_font_size)
    content_listbox.config(font=new_font)
"""


def name_bind(event=None):
    validate_name()
    search_files()


def number_bind(event=None):
    validate_number()
    search_files()


def date_bind(event=None):
    validate_date()
    search_files()


def hint_handler(event, data):
    hints = {"num": "Введите номер документа",
             "name": "Введите название документа",
             "date": "Введите дату издания документа",
             "combo": "Выберите к какому виду документ относится",
             "listbox": "Выберите документ для просмотра",
             }
    if data in hints:
        main_l_hint.configure(text=hints[data])


def on_select_combo(event=None):
    selected_item = combo.get()
    if selected_item == "<<Создать новый класс НПА>>":
        create_new_NPA()


def create_new_NPA():
    global npa_hierarchy
    npa_hier = npa_hierarchy

    def _create_listbox():
        for i, item in enumerate(npa_hier):
            listbox.insert(tk.END, f"{i + 1}. {item}")

    def _on_drag_start(event):
        index = listbox.nearest(event.y)
        listbox.selection_clear(0, tk.END)
        listbox.selection_set(index)
        listbox._drag_start_index = index
        listbox._drag_data = listbox.get(index).split(". ", 1)[1]

    def _on_drag_motion(event):
        index = listbox.nearest(event.y)
        if index != listbox._drag_start_index:
            data = listbox.get(index).split(". ", 1)[1]
            listbox.delete(index)
            listbox.insert(listbox._drag_start_index, f"{listbox._drag_start_index + 1}. {data}")
            listbox.delete(index)
            listbox.insert(index, f"{index + 1}. {listbox._drag_data}")
            listbox.selection_set(index)
            listbox._drag_start_index = index
        # _update_item_numbers()

    def _remove_placeholder(event):
        if entry.get() == "Название вида НПА":
            entry.delete(0, tk.END)
            entry.config(fg="black")

    def _set_placeholder(event):
        if entry.get() == "":
            entry.config(fg="grey")
            entry.insert(0, "Название вида НПА")

    def _save_npa(event=None):
        global npa_hierarchy
        new_hier= {}
        for element in range(listbox.size()):
            iter1, name = listbox.get(element).split(". ", 1)
            new_hier[name]=int(iter1)
        npa_hierarchy = new_hier
    win = tk.Toplevel(root)
    win.title("Создание нового класса НПА")

    listbox = tk.Listbox(win, selectmode="single")
    listbox.pack(side=tk.TOP, fill="both", expand=True)
    help_l = tk.Label(win, text="Перетащите элемент для изменения иерархии")
    help_l.pack(side=tk.TOP, fill=tk.X, expand=True)
    b1 = tk.Button(win, text="Сохранить", command=_save_npa)
    b2 = tk.Button(win, text="Отменить", command=lambda: win.destroy())
    b3 = tk.Button(win, text="Добавить элемент",
                   command=lambda: listbox.insert(tk.END, f"{listbox.size() + 1}. {entry.get()}"))
    b4 = tk.Button(win, text="Удалить элемент",
                   command=lambda: listbox.delete(listbox.curselection()[0]))
    b1.pack(side=tk.BOTTOM, fill=tk.X, expand=True)
    b2.pack(side=tk.BOTTOM, fill=tk.X, expand=True)
    b3.pack(side=tk.BOTTOM, fill=tk.X, expand=True)
    b4.pack(side=tk.BOTTOM, fill=tk.X, expand=True)
    entry = tk.Entry(win)
    entry.bind("<FocusIn>", _remove_placeholder)
    entry.bind("<FocusOut>", _set_placeholder)

    entry.pack(side=tk.BOTTOM, fill=tk.X, expand=True)

    entry.insert(0, "Название вида НПА")
    entry.config(fg="grey")
    _create_listbox()
    listbox.bind("<ButtonPress-1>", _on_drag_start)
    listbox.bind("<B1-Motion>", _on_drag_motion)


root = tk.Tk()
root.title("Менеджер файлов")
style = ttk.Style(root)
style.theme_use("clam")  # Выбираем тему оформления
style.configure("Treeview", background="#f0f0f0", fieldbackground="#f0f0f0")
style.map("Treeview", background=[('selected', '#347083')])
# root.attributes("-fullscreen", True)

paned_window = ttk.PanedWindow(root, orient=tk.HORIZONTAL)

frame1 = tk.Frame(paned_window, bg="#f0f0f0", bd=1, relief=tk.SUNKEN)
frame1.pack(pady=5, padx=10, side=tk.RIGHT, fill=tk.BOTH, expand=True)
canvas = tk.Canvas(frame1, bg="#f0f0f0")
scrollbar1 = tk.Scrollbar(frame1, orient="vertical", command=canvas.yview)
scrollbar1.pack(side="right", fill="y")
scrollbar2 = tk.Scrollbar(frame1, orient="horizontal", command=canvas.xview)
scrollbar2.pack(side="bottom", fill="x")

canvas.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
canvas.bind("<MouseWheel>", on_mousewheel)
canvas.config(yscrollcommand=scrollbar1.set, xscrollcommand=scrollbar2.set)

frame2 = tk.Frame(paned_window, bd=1, relief=tk.SUNKEN)
frame2.pack(pady=5, padx=10, side=tk.LEFT, fill=tk.BOTH, expand=True)

content_listbox = tk.Listbox(frame2, xscrollcommand=lambda *args: scrollbar_x.set(*args))
# Создаем горизонтальный Scrollbar и привязываем его к Listbox
scrollbar_x = tk.Scrollbar(frame2, orient=tk.HORIZONTAL, command=content_listbox.xview, bg="blue")
scrollbar_x.grid(row=1, column=0, columnspan=6, sticky="ew")

# Привязываем Scrollbar к Listbox
content_listbox.config(xscrollcommand=scrollbar_x.set)

content_listbox.config(font=font.Font(family="Helvetica", size=14))

content_listbox.grid(row=0, column=0, columnspan=6, sticky="nsew")
content_listbox.bind("<Double-Button-1>", select_file)
content_listbox.bind("<Button-3>", show_context_menu)
content_listbox.bind("<Enter>", lambda event: hint_handler(event, "listbox"))
# content_listbox.bind("<Configure>", font_listbox) автоматическая регулировка шрифта

frame2.grid_rowconfigure(0, weight=400)
frame2.grid_columnconfigure(0, weight=0)

# Labels
main_l_hint = tk.Label(frame2)
main_l_date = tk.Label(frame2, text="Дата \n издания")
main_l_number = tk.Label(frame2, text="№ \nДокумента")
main_l_name = tk.Label(frame2, text="Имя \nдокумента")
main_l_dir = tk.Label(frame2, text="Каталог документа")
main_l_file = tk.Label(frame2)

# Entries
main_e_date = tk.Entry(frame2, name="date")
main_e_number = tk.Entry(frame2, name="num")
main_e_name = tk.Entry(frame2, name="name")

main_e_date.insert(0, "дд.мм.гггг")
main_e_date.config(fg="grey")
main_e_number.insert(0, "1_1234")
main_e_number.config(fg="grey")
main_e_name.insert(0, "О создании...")
main_e_name.config(fg="grey")

main_e_date.bind("<FocusIn>", remove_placeholder1)
main_e_date.bind("<FocusOut>", set_placeholder1)
main_e_number.bind("<FocusIn>", remove_placeholder2)
main_e_number.bind("<FocusOut>", set_placeholder2)
main_e_name.bind("<FocusIn>", remove_placeholder3)
main_e_name.bind("<FocusOut>", set_placeholder3)
main_e_number.bind("<Enter>", lambda event: hint_handler(event, "num"))
main_e_name.bind("<Enter>", lambda event: hint_handler(event, "name"))
main_e_date.bind("<Enter>", lambda event: hint_handler(event, "date"))
"""main_e_date.bind("<KeyRelease>", validate_date)
main_e_name.bind("<KeyRelease>", validate_name)
main_e_number.bind("<KeyRelease>", validate_number)
main_e_number.bind("<KeyRelease>", search_files)
main_e_name.bind("<KeyRelease>", search_files)
main_e_date.bind("<KeyRelease>", search_files)
"""
main_e_number.bind("<KeyRelease>", number_bind)
main_e_name.bind("<KeyRelease>", name_bind)
main_e_date.bind("<KeyRelease>", date_bind)

# Buttons

main_b_add = tk.Button(frame2, text="Выбрать файл", command=user_choose_file)
main_b_clear = tk.Button(frame2, text="Очистить", command=clear_main)

options = get_folder_options()

# Создаем переменную для выбранного значения
selected_option = tk.StringVar()

# Создаем выпадающий список
combo = ttk.Combobox(frame2, textvariable=selected_option, values=options, state="readonly")
combo.bind("<<ComboboxSelected>>", on_select_combo)
combo.bind("<Enter>", lambda event: hint_handler(event, "combo"))

# Pack to frame
main_l_hint.grid(row=5, column=0, columnspan=6, sticky="nsew")
main_l_date.grid(row=2, column=0)
main_e_date.grid(row=2, column=1)
main_l_number.grid(row=2, column=2)
main_e_number.grid(row=2, column=3)
main_l_name.grid(row=2, column=4)
# main_l_file.grid(row=2, column=0, columnspan=4)
main_e_name.grid(row=2, column=5, sticky="nsew")
main_l_dir.grid(row=3, column=0, sticky="nsew")
main_b_add.grid(row=3, column=5, sticky="nsew")
main_b_clear.grid(row=3, column=4, sticky="nsew")
combo.grid(row=3, column=1, columnspan=3, sticky="nsew")

for n in range(1, 6):
    frame2.grid_columnconfigure(n, weight=1)
    # frame2.grid_rowconfigure(n, weight=1)
# frame2.grid_rowconfigure(1,weight=0)
for n in range(0, 5):
    frame2.grid_columnconfigure(n, weight=1)
frame2.grid_columnconfigure(1, minsize=70)

paned_window.add(frame2)
paned_window.add(frame1)

paned_window.pane(frame1, weight=3)
paned_window.pane(frame2, weight=1)
"""
Создание окна по размеру экрана
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

root.geometry(f'{screen_width}x{screen_height - (int(screen_height * 0.1))}+0+0')
"""
root.geometry(f'1400x600+0+0')

context_menu = tk.Menu(root, tearoff=0)
context_menu.add_command(label="Переименовать", command=rename_file_from_contex)

show_directory_contents()
helper_window = tk.Toplevel(root)
helper_window.withdraw()
filename = 'directory_listing.pkl'
watcher = DirectoryWatcher(os.path.dirname(os.getcwd()))
watcher.start_watching()
file_routine()
paned_window.pack(fill=tk.BOTH, expand=True)
canvas.bind("<Configure>", resize_images)
create_dirs()
root.mainloop()
