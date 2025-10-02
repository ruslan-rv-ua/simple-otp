# Реалізація роботи з множинними файлами акаунтів

## Мета
Замість жорстко заданого файлу `accounts.json`, додати можливість працювати з різними файлами баз акаунтів - відкривати, створювати нові, перемикатися між ними.

## Вимоги

### 1. Структура меню
Реорганізувати меню додавши нове меню **File** на першій позиції з наступними пунктами:
```
File
├── New...           Ctrl+N    (Створити новий файл акаунтів)
├── Open...          Ctrl+O    (Відкрити існуючий файл)
├── Recent Files     ▶         (Підменю з останніми відкритими файлами)
│   ├── C:\Users\...\accounts1.json
│   ├── C:\Users\...\work.json
│   ├── ...          (до 16 файлів)
│   ├── ─────────────
│   └── Clear History           (Очистити історію)
├── ─────────────
└── Exit             Esc       (Існуючий пункт перенести сюди)
```

Меню **Account** залишити як є (Add, Delete).

### 2. Константи
Додати у `simple_otp/constants.py`:
```python
# Maximum number of recent files to remember
MAX_RECENT_FILES = 16
```

### 3. Settings Manager - історія файлів
Розширити `DEFAULT_SETTINGS` у `SettingsManager`:
```python
"files": {
    "recent_files": [],              # List[str] - шляхи до останніх файлів
    "open_last_file_on_startup": True,  # bool - відкривати останній файл при запуску
}
```

**Важливо:**
- Поле `recent_files` НЕ показувати у Settings Dialog
- Поле `open_last_file_on_startup` додати у Settings Dialog у секцію "Behavior"

### 4. Функціонал

#### 4.1 New File (Ctrl+N)
1. Показати стандартний діалог збереження файлу (wxPython `wx.FileDialog` з `wx.FD_SAVE`)
2. Фільтр: `"JSON files (*.json)|*.json"`
3. Якщо файл вибрано:
   - Якщо файл існує - попередити користувача про перезапис
   - Запитати пароль для нового файлу (PasswordDialog з підтвердженням)
   - Створити новий `AccountsManager` з цим файлом
   - Створити порожній файл або з прикладним акаунтом (на ваш розсуд)
   - Оновити main window для роботи з новим файлом
   - Додати шлях до recent_files

#### 4.2 Open File (Ctrl+O)
1. Показати стандартний діалог відкриття файлу (`wx.FileDialog` з `wx.FD_OPEN | wx.FD_FILE_MUST_EXIST`)
2. Фільтр: `"JSON files (*.json)|*.json"`
3. Якщо файл вибрано:
   - Запитати пароль для відкриття (PasswordDialog без підтвердження)
   - Спробувати відкрити файл і перевірити пароль
   - Якщо пароль правильний - переключитися на цей файл
   - Якщо ні - показати помилку і залишитися на поточному файлі
   - Додати шлях до recent_files (на першу позицію)

#### 4.3 Recent Files (підменю)
- Динамічно генерувати пункти меню з `recent_files`
- Показувати до 16 останніх файлів
- При кліку на файл - відкрити його (аналогічно Open File)
- Якщо файл не існує - показати помилку і видалити з recent_files
- Пункт "Clear History" - очистити весь список recent_files і зберегти settings

#### 4.4 Startup Behavior
У `__main__.py` у функції `main()` після автентифікації:
```python
# Перевірити settings
if settings_manager.get("files.open_last_file_on_startup", True):
    recent_files = settings_manager.get("files.recent_files", [])
    if recent_files:
        last_file = recent_files[0]
        # Спробувати відкрити last_file з паролем password
        # Якщо помилка - відкрити стандартний файл
```

### 5. UI/UX деталі

#### 5.1 Заголовок вікна
Показувати ім'я відкритого файлу:
```python
self.SetTitle(f"Simple OTP - {Path(current_file).name}")
```

#### 5.2 Recent Files - формат відображення
- Якщо шлях дуже довгий - скоротити середню частину: `C:\Users\...\accounts.json`
- Або показувати тільки ім'я файлу + підказку (tooltip) з повним шляхом

#### 5.3 Збереження
`AccountsManager` вже автоматично зберігає зміни при add/delete/update, тому додаткова логіка не потрібна.

### 6. Рефакторинг MainWindow

#### 6.1 Додати методи:
```python
def _switch_to_file(self, file_path: Path, password: str) -> bool:
    """Переключитися на інший файл акаунтів. Повертає True якщо успішно."""

def _update_recent_files(self, file_path: Path) -> None:
    """Додати файл до recent_files і зберегти settings."""

def _load_recent_files_menu(self) -> None:
    """Динамічно оновити підменю Recent Files."""
```

#### 6.2 Змінити конструктор:
Приймати параметр `accounts_file: Path | None = None`:
```python
def __init__(self, parent, password: str, accounts_file: Path | None = None):
    # ...
    if accounts_file:
        self.accounts_manager = AccountsManager(storage_path=accounts_file)
    else:
        self.accounts_manager = AccountsManager()  # Стандартний файл
```

### 7. Технічні деталі

#### 7.1 Валідація
- Перевіряти що файл має розширення `.json`
- Перевіряти що файл доступний для читання/запису
- Обробляти помилки (файл не існує, немає прав доступу, тощо)

#### 7.2 Обробка помилок
Усі операції з файлами обгортати в try-except і показувати зрозумілі повідомлення користувачу через `wx.MessageBox`.

#### 7.3 Дублікати у recent_files
- Якщо файл вже є у списку - перемістити його на першу позицію
- Зберігати не більше MAX_RECENT_FILES (16) файлів
- Видаляти найстаріші файли якщо список переповнений

### 8. Commit Message
Використати Conventional Commits:
```
feat(files): implement multiple account files support

- Add File menu with New, Open, Recent Files
- Add recent files history (max 16) in settings
- Add "open last file on startup" setting
- Update MainWindow to support file switching
- Show current file name in window title
```

## Відповіді на уточнюючі питання

### 1. Поведінка при відкритті нового файлу
- **Пароль:** Кожен файл має свій власний пароль (як зараз). При відкритті нового файлу запитувати новий пароль.
- **Новий файл:** Створювати порожній файл (без прикладного акаунту), щоб користувач сам додав акаунти.

### 2. Меню структура
- **Розміщення:** Окреме меню "File" на першій позиції (перед "Account").
- **Exit:** Перенести з "Account" в "File" (стандартна практика для desktop додатків).

### 3. Збереження при переключенні
- **Автозбереження:** Не потрібно додатково зберігати, оскільки `AccountsManager` вже зберігає зміни автоматично при кожній операції.

### 4. Назва у заголовку вікна
- **Показувати:** Так, показувати ім'я файлу у заголовку: `"Simple OTP - accounts.json"`

### 5. Recent Files у Settings
- **Очистка:** Додати пункт "Clear History" безпосередньо в підменю Recent Files (не в Settings Dialog).
