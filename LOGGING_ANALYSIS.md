# Аналіз логування в проєкті Simple OTP

## Дата аналізу: 10 жовтня 2025

## Загальна оцінка

**Статус логування: ЧАСТКОВО РЕАЛІЗОВАНО** ⚠️

Базова інфраструктура логування створена і працює, але багато критичних модулів не мають логування.

## Модулі з логуванням ✅

### 1. `simple_otp/core/logger.py`
- ✅ Конфігурація loguru
- ✅ Логування у файл
- ✅ DEBUG рівень
- ✅ Backtrace та diagnose
- ✅ Функція get_log_file_path()

### 2. `simple_otp/__main__.py`
- ✅ Логування запуску програми
- ✅ Ініціалізація компонентів
- ✅ Завантаження налаштувань
- ✅ Виявлення локалі
- ✅ Обробка критичних помилок

### 3. `simple_otp/ui/main_window.py`
- ✅ Ініціалізація вікна
- ✅ Створення UI компонентів
- ✅ Події меню (додавання/видалення акаунтів)
- ✅ Активація елементів списку
- ✅ Відкриття лог-файлу (Options → Open Log File)

### 4. `simple_otp/core/accounts_manager.py`
- ✅ Ініціалізація менеджера
- ✅ Завантаження акаунтів
- ✅ Збереження акаунтів
- ✅ Помилки JSON парсингу
- ✅ Операції з файлами

## Модулі БЕЗ логування ❌

### ВИСОКИЙ ПРІОРИТЕТ 🔴

#### 1. `simple_otp/core/authenticator.py`
**Критичність: ДУЖЕ ВИСОКА**

Відсутнє логування:
- ❌ Спроби автентифікації
- ❌ Успішна автентифікація
- ❌ Невдала автентифікація
- ❌ Кількість спроб введення пароля
- ❌ Перевищення максимальної кількості спроб
- ❌ Відміна користувачем
- ❌ Помилки відкриття файлів

**Рекомендовані точки логування:**
```python
# authenticate()
logger.info(f"Authentication requested for file: {file_path}")
logger.info(f"Authentication successful for: {file_path}")
logger.warning(f"Authentication failed for: {file_path}")

# _request_password_with_retry()
logger.debug(f"Password attempt {attempt}/{max_attempts}")
logger.warning(f"Maximum password attempts exceeded for: {file_path}")
logger.info("User cancelled password entry")
```

#### 2. `simple_otp/ui/file_controller.py`
**Критичність: ДУЖЕ ВИСОКА**

Відсутнє логування:
- ❌ Створення нових файлів
- ❌ Відкриття існуючих файлів
- ❌ Вибір шляху до файлу
- ❌ Встановлення пароля
- ❌ Підтвердження пароля
- ❌ Помилки створення/відкриття файлів
- ❌ Відміна користувачем

**Рекомендовані точки логування:**
```python
# create_new_file()
logger.info("User initiated new file creation")
logger.debug(f"Selected file path: {file_path}")
logger.info(f"New file created successfully: {file_path}")
logger.warning("User cancelled new file creation")

# open_existing_file()
logger.info("User initiated file open")
logger.info(f"Opening file: {file_path}")
logger.info(f"File opened successfully: {file_path}")
```

### СЕРЕДНІЙ ПРІОРИТЕТ 🟡

#### 3. `simple_otp/ui/add_account_dialog.py`
**Критичність: ВИСОКА**

Відсутнє логування:
- ❌ Відкриття діалогу
- ❌ Валідація введених даних
- ❌ Помилки валідації (порожні поля, невірний формат secret)
- ❌ Підтвердження додавання
- ❌ Відміна користувачем

**Рекомендовані точки логування:**
```python
# __init__()
logger.debug("AddAccountDialog opened")

# _on_ok()
logger.debug(f"Validating account data: name={name}, issuer={issuer}")
logger.warning("Validation failed: name is empty")
logger.warning(f"Invalid Base32 secret: {error}")
logger.info(f"Account data validated successfully: {name}")
```

#### 4. `simple_otp/ui/totp_dialog.py`
**Критичність: ВИСОКА**

Відсутнє логування:
- ❌ Відкриття діалогу TOTP
- ❌ Генерація TOTP кодів
- ❌ Копіювання кодів у буфер
- ❌ Автоматичне копіювання
- ❌ Відтворення звуків
- ❌ Оновлення таймера
- ❌ Закриття діалогу

**⚠️ БЕЗПЕКА: НЕ логувати самі TOTP коди!**

**Рекомендовані точки логування:**
```python
# __init__()
logger.info(f"TOTP dialog opened for account: {account.get_display_name()}")

# _on_copy_current()
logger.info("User copied current OTP to clipboard")

# _on_copy_next()
logger.info("User copied next OTP to clipboard")

# _auto_copy_on_update()
logger.debug("Auto-copy triggered on OTP update")

# _on_close()
logger.debug("TOTP dialog closed")
```

#### 5. `simple_otp/ui/password_dialog.py`
**Критичність: СЕРЕДНЯ**

Відсутнє логування:
- ❌ Відкриття діалогу
- ❌ Режим діалогу (з підтвердженням / без)
- ❌ Валідація пароля
- ❌ Невідповідність паролів при підтвердженні
- ❌ Порожній пароль
- ❌ Підтвердження/відміна

**⚠️ БЕЗПЕКА: НЕ логувати самі паролі!**

**Рекомендовані точки логування:**
```python
# __init__()
logger.debug(f"Password dialog opened (confirmation required: {require_confirmation})")

# _on_ok()
logger.debug("Password validation started")
logger.warning("Password is empty")
logger.warning("Passwords do not match")
logger.debug("Password validated successfully")
logger.info("User confirmed password entry")
logger.info("User cancelled password entry")
```

### НИЗЬКИЙ ПРІОРИТЕТ 🟢

#### 6. `simple_otp/core/settings_manager.py`
**Критичність: СЕРЕДНЯ**

Відсутнє логування:
- ❌ Ініціалізація менеджера
- ❌ Завантаження налаштувань
- ❌ Збереження налаштувань
- ❌ Помилки JSON парсингу
- ❌ Використання дефолтних налаштувань
- ❌ Зміна окремих налаштувань

**Рекомендовані точки логування:**
```python
# load()
logger.debug(f"Loading settings from: {self.settings_file}")
logger.info("Settings loaded successfully")
logger.warning("Settings file corrupted, using defaults")
logger.info("First run detected, creating default settings")

# save()
logger.debug("Saving settings")
logger.info("Settings saved successfully")

# set()
logger.debug(f"Setting changed: {key} = {value}")
```

#### 7. `simple_otp/core/recent_files_manager.py`
**Критичність: НИЗЬКА**

Відсутнє логування:
- ❌ Додавання файлу до списку
- ❌ Видалення файлу зі списку
- ❌ Очищення списку
- ❌ Отримання списку файлів

**Рекомендовані точки логування:**
```python
# add_file()
logger.debug(f"Adding file to recent: {file_path}")
logger.debug(f"File moved to front of recent list: {file_path}")

# remove_file()
logger.debug(f"Removing file from recent: {file_path}")
logger.debug(f"File not in recent list: {file_path}")

# clear_all()
logger.info("Recent files list cleared")
```

#### 8. `simple_otp/ui/settings_dialog.py`
**Критичність: НИЗЬКА**

Відсутнє логування:
- ❌ Відкриття діалогу
- ❌ Завантаження поточних налаштувань
- ❌ Зміна налаштувань
- ❌ Збереження налаштувань
- ❌ Скидання до дефолтних значень
- ❌ Відміна змін

**Рекомендовані точки логування:**
```python
# __init__()
logger.debug("Settings dialog opened")

# _on_ok()
logger.info("User saved settings")
logger.debug("Settings changes applied")

# _on_reset()
logger.info("User reset settings to defaults")

# Destroy()
logger.debug("Settings dialog closed")
```

## Додаткові модулі для розгляду

### `simple_otp/ui/audio_player.py`
- Логування відтворення звуків (успіх/помилка)
- Логування помилок завантаження аудіо файлів

### `simple_otp/core/encryptor.py`
- Логування операцій шифрування/дешифрування (БЕЗ секретів!)
- Логування помилок криптографії

### `simple_otp/models/totp_account.py`
- Логування створення акаунтів
- Логування генерації TOTP (БЕЗ кодів!)
- Логування помилок валідації

## Підсумок і рекомендації

### Поточний стан
- ✅ 4 модулі з логуванням
- ❌ 8+ модулів без логування
- **Покриття логуванням: ~30%**

### Пріоритети впровадження

**Фаза 1 (Критично):**
1. `core/authenticator.py` - автентифікація
2. `ui/file_controller.py` - файлові операції

**Фаза 2 (Важливо):**
3. `ui/add_account_dialog.py` - додавання акаунтів
4. `ui/totp_dialog.py` - відображення TOTP
5. `ui/password_dialog.py` - введення паролів

**Фаза 3 (Бажано):**
6. `core/settings_manager.py` - налаштування
7. `core/recent_files_manager.py` - останні файли
8. `ui/settings_dialog.py` - діалог налаштувань

### Безпекові вимоги 🔒

**НІКОЛИ НЕ логувати:**
- ❌ Паролі користувачів
- ❌ TOTP коди (current/next)
- ❌ Розшифровані секрети
- ❌ Ключі шифрування

**МОЖНА логувати:**
- ✅ Імена акаунтів
- ✅ Постачальники (issuers)
- ✅ Шляхи до файлів
- ✅ Результати операцій (успіх/помилка)
- ✅ Спроби автентифікації (кількість)
- ✅ Параметри TOTP (digits, interval, digest)

### Рекомендований формат логування

```python
# Успішна операція
logger.info(f"Operation completed: {description}")

# Початок операції
logger.debug(f"Starting operation: {description}")

# Попередження
logger.warning(f"Potential issue: {description}")

# Помилка з винятком
logger.opt(exception=True).error(f"Operation failed: {description}")

# Критична помилка
logger.critical(f"Fatal error: {description}")
```

### Наступні кроки

1. ✅ Створити цей документ
2. ⏳ Додати логування у модулі Фази 1
3. ⏳ Додати логування у модулі Фази 2
4. ⏳ Додати логування у модулі Фази 3
5. ⏳ Провести тестування і перевірку логів
6. ⏳ Оновити LOGGING.md з новою інформацією

### Оцінка часу

- Фаза 1: ~1-2 години
- Фаза 2: ~2-3 години
- Фаза 3: ~1-2 години
- **Загалом: 4-7 годин для повного покриття**

## Висновок

Поточна реалізація логування покриває основний flow програми (запуск, головне вікно, робота з акаунтами), але **критично важливі модулі автентифікації та файлових операцій не мають логування**. 

Рекомендується **терміново** додати логування у модулі Фази 1, оскільки це допоможе діагностувати проблеми з автентифікацією та файлами - найпоширеніші джерела помилок у додатках такого типу.
