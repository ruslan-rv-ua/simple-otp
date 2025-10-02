# AudioPlayer - Глобальний екземпляр (Singleton Pattern)

## Проблема

Попередньо `AudioPlayer` створювався кожного разу при відкритті `TOTPDialog`:

```python
# Попередня реалізація (неоптимальна)
sounds_dir = Path(__file__).parent.parent / "assets" / "sounds"
try:
    self.audio_player = AudioPlayer(sounds_dir)
except (FileNotFoundError, NotADirectoryError, OSError):
    self.audio_player = None
```

### Недоліки:
1. **Зайве I/O навантаження** - При кожному створенні екземпляру всі WAV файли читаються з диска в пам'ять
2. **Затримки** - Читання файлів може створювати мікро-затримки при відкритті діалогу
3. **Неефективне використання ресурсів** - Багаторазове завантаження тих самих даних

## Рішення

Створено **глобальний екземпляр** `audio_player` в модулі `audio_player.py`, який ініціалізується один раз при імпорті модуля:

```python
# audio_player.py
def _create_audio_player() -> AudioPlayer | None:
    """
    Create global AudioPlayer instance.

    Returns None if sounds directory doesn't exist (graceful degradation).
    """
    sounds_dir = Path(__file__).parent.parent / "assets" / "sounds"
    try:
        return AudioPlayer(sounds_dir)
    except (FileNotFoundError, NotADirectoryError, OSError):
        return None


audio_player = _create_audio_player()
```

## Використання

### У коді додатку

```python
from simple_otp.ui.audio_player import audio_player

class TOTPDialog(wx.Dialog):
    def __init__(self, parent, account: TOTPAccount, password: str):
        # ...
        # Use global audio player instance
        self.audio_player = audio_player
        # ...
    
    def some_method(self):
        if self.audio_player:
            self.audio_player.play("sound.wav")
```

### У тестах (створення власного екземпляру)

Тести продовжують створювати власні екземпляри для ізоляції:

```python
from simple_otp.ui.audio_player import AudioPlayer

def test_something():
    player = AudioPlayer(test_sounds_dir)
    # ...
```

## Переваги нового підходу

1. ✅ **Ефективність** - WAV файли завантажуються один раз при старті додатку
2. ✅ **Швидкість** - Немає затримок при відкритті діалогів
3. ✅ **Простота** - Один імпорт, немає передачі параметрів через ієрархію
4. ✅ **Graceful degradation** - Якщо папка зі звуками не існує, `audio_player = None` (не ламає додаток)
5. ✅ **Зворотна сумісність** - Клас `AudioPlayer` залишився незмінним, можна створювати власні екземпляри

## Альтернативні підходи (не використовуються)

### 1. Singleton Pattern (занадто складно)
```python
class AudioPlayer:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

### 2. Передача через MainWindow (занадто громіздко)
```python
# MainWindow створює і передає через параметри
self.audio_player = AudioPlayer(sounds_dir)
dialog = TOTPDialog(self, account, password, self.audio_player)
```

## Висновок

Глобальний екземпляр - найпростіше і найефективніше рішення для цього випадку, оскільки:
- Аудіоплеєр є "сервісом" додатку (не має стану, пов'язаного з конкретним вікном)
- Звукові файли не змінюються під час роботи
- Всі компоненти використовують одні й ті ж звуки
