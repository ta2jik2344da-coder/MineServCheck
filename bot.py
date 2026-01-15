import decouple
import aiogram
import dotenv
import asyncio
import inspect

# Mock класс для симуляции сервера Aternos
class MockServer:
    def __init__(self):
        self.status_value = "offline"
        self.name = "Mock Aternos Server"

    async def status(self):
        # Симулируем асинхронный вызов
        await asyncio.sleep(0.5)
        return self.status_value

    async def start(self):
        # Симулируем запуск
        await asyncio.sleep(1)
        self.status_value = "online"

load_dotenv() 
BOT_TOKEN = os.getenv('BOT_TOKEN') 

server = MockServer()
logging.basicConfig(level=logging.INFO)
logging.info(f"Подключился к серверу: {server.name}")

def get_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("🔎 Проверить статус", "▶️ Запустить сервер")
    return keyboard

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply(
        "Привет! Я бот для управления сервером Aternos.\nИспользуйте кнопки ниже:",
        reply_markup=get_keyboard()
    )

# Утилиты, чтобы корректно вызывать sync/async методы сервера
async def call_maybe_async(func, *args, **kwargs):
    """Если func — coroutine function, await её. Иначе запустить в executor (не блокируя loop)."""
    if inspect.iscoroutinefunction(func):
        return await func(*args, **kwargs)
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: func(*args, **kwargs))

async def get_server_status():
    if server is None:
        return None
    status_attr = getattr(server, 'status', None)
    if callable(status_attr):
        return await call_maybe_async(status_attr)
    return status_attr  # возможно строка или property

@dp.message_handler(lambda message: message.text == "🔎 Проверить статус")
async def check_status(message: types.Message):
    if server is None:
        await message.reply("Сервер не инициализирован или не найден.", reply_markup=get_keyboard())
        return
    try:
        status = await get_server_status()
        await message.reply(f"Статус сервера: {status}", reply_markup=get_keyboard())
    except Exception as e:
        logging.exception("Ошибка при получении статуса")
        await message.reply(f"Ошибка: {e}", reply_markup=get_keyboard())

@dp.message_handler(lambda message: message.text == "▶️ Запустить сервер")
async def start_server(message: types.Message):
    if server is None:
        await message.reply("Сервер не инициализирован или не найден.", reply_markup=get_keyboard())
        return
    try:
        status = await get_server_status()
        if status == "offline" or status == "OFFLINE" or status == "off":
            start_attr = getattr(server, 'start', None)
            if start_attr is None or not callable(start_attr):
                await message.reply("Метод запуска сервера не найден.", reply_markup=get_keyboard())
                return
            await call_maybe_async(start_attr)
            await message.reply("Сервер запущен! Ожидайте...", reply_markup=get_keyboard())
        else:
            await message.reply("Сервер уже работает.", reply_markup=get_keyboard())
    except Exception as e:
        logging.exception("Ошибка при попытке запустить сервер")
        await message.reply(f"Ошибка: {e}", reply_markup=get_keyboard())

@dp.message_handler()
async def unknown_message(message: types.Message):
    await message.reply("Неизвестная команда. Используйте кнопки ниже:", reply_markup=get_keyboard())

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
                                                                                                                                                                                            
