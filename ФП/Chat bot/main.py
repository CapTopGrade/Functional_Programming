import spotipy
from spotipy import util
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
import requests


SELECT_ACTION, SELECT_CITY, WEATHER_REPORT = range(3)

SPOTIPY_CLIENT_ID = '88a3bb2ca80a4d7785aaf586728cce5b'
SPOTIPY_CLIENT_SECRET = '20e98d182cae427589dfc87308e11d48'
SPOTIPY_REDIRECT_URI = 'https://t.me/CapTopGrade_PP_bot'

username = 'captopgrade'
scope = 'user-library-read,user-modify-playback-state,user-read-playback-state'

token = util.prompt_for_user_token(username, scope, client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET,
                                   redirect_uri=SPOTIPY_REDIRECT_URI)

if token:
    sp = spotipy.Spotify(auth=token)
    print("Токен успешно получен.")
else:
    print("Не удалось получить токен.")

API_KEY = '56b81f424fb323383eba03bd5f43ddea'
BASE_URL = 'http://api.openweathermap.org/data/2.5/weather'


def get_spotify_object():
    global sp
    token = util.prompt_for_user_token(username, scope, client_id=SPOTIPY_CLIENT_ID,
                                       client_secret=SPOTIPY_CLIENT_SECRET, redirect_uri=SPOTIPY_REDIRECT_URI)

    if token:
        sp = spotipy.Spotify(auth=token)
        print("Токен успешно получен.")
        return sp
    else:
        print("Не удалось получить токен.")
        return None


def get_spotify_recommendations():
    sp = get_spotify_object()

    if sp:
        try:
            mix_of_the_day = 'https://open.spotify.com/playlist/37i9dQZF1E35tfLVW6ueIM?si=0aa3b288892a481c'
            favorite_tracks = 'https://open.spotify.com/collection/tracks'

            recommendations = [
                f'Микс дня: {mix_of_the_day}',
                f'Любимое: {favorite_tracks}'
            ]
            print(f'Recommendations: {recommendations}')
            return recommendations
        except spotipy.SpotifyException as e:
            print(f'Error fetching recommendations: {str(e)}')
            return None
    else:
        return None


def get_weather(city):
    api_key = '56b81f424fb323383eba03bd5f43ddea'
    base_url = 'http://api.openweathermap.org/data/2.5/weather'

    params = {
        'q': city,
        'appid': api_key,
        'units': 'metric',
    }

    try:
        response = requests.get(base_url, params=params)
        data = response.json()

        if response.status_code == 200:
            temperature = data['main']['temp']
            description = data['weather'][0]['description']

            return f"Погода в городе {city}: {description}, температура: {temperature}°C"
        else:
            return "Не удалось получить информацию о погоде. Попробуйте еще раз."

    except Exception as e:
        return f"Произошла ошибка: {e}"


def start_weather(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(f"В каком городе вы хотите узнать погоду? Введите название города:")
    return SELECT_CITY


def handle_city_input(update: Update, context: CallbackContext) -> None:
    city = update.message.text

    # Получаем информацию о погоде и отправляем результат пользователю
    weather_report = get_weather(city.lower())
    update.message.reply_text(weather_report)

    # Возвращаем пользователя в основное меню
    main_menu(update, context)
    return ConversationHandler.END



def handle_show_weather(update: Update, context: CallbackContext) -> None:
    city = context.user_data.get('selected_city')
    if city:
        weather_report = get_weather(city.lower())
        update.message.reply_text(weather_report)
    else:
        update.message.reply_text('Сначала выберите город.')

    # Сбросить состояние разговора и вернуться в основное меню
    return ConversationHandler.END


def cancel_weather(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Запрос на погоду отменен.')
    return ConversationHandler.END


def weather_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[MessageHandler(Filters.regex(r'Погода'), start_weather)],
        states={
            SELECT_CITY: [MessageHandler(Filters.text & ~Filters.command, handle_city_input)],
            WEATHER_REPORT: [MessageHandler(Filters.regex(r'показать погоду'), handle_show_weather)],
        },
        fallbacks=[MessageHandler(Filters.regex(r'назад'), cancel_weather)],
    )


def play(update: Update, context: CallbackContext) -> None:
    sp = get_spotify_object()

    if sp:
        try:
            # Get a list of available devices
            devices = sp.devices()

            # Check if there are available devices
            if devices['devices']:
                # Use the first available device to start playback
                sp.start_playback(device_id=devices['devices'][0]['id'])
                update.message.reply_text('Воспроизведение музыки начато.')
            else:
                update.message.reply_text(
                    'Нет доступных устройств для воспроизведения. Подключите устройство к вашему аккаунту Spotify.')
        except spotipy.SpotifyException as e:
            update.message.reply_text(f'Ошибка при воспроизведении музыки: {str(e)}')
    else:
        update.message.reply_text('Не удалось начать воспроизведение. Попробуйте еще раз.')

    # После воспроизведения возвращаем пользователя к меню выбора плейлиста
    spotify_menu(update, context)


def pause(update: Update, context: CallbackContext) -> None:
    sp = get_spotify_object()

    if sp:
        sp.pause_playback()
        update.message.reply_text('Воспроизведение музыки поставлено на паузу.')
    else:
        update.message.reply_text('Не удалось поставить воспроизведение на паузу. Попробуйте еще раз.')


def next_track(update: Update, context: CallbackContext) -> None:
    sp = get_spotify_object()

    if sp:
        sp.next_track()
        update.message.reply_text('Следующий трек.')
    else:
        update.message.reply_text('Не удалось переключиться на следующий трек. Попробуйте еще раз.')


def prev_track(update: Update, context: CallbackContext) -> None:
    sp = get_spotify_object()

    if sp:
        sp.previous_track()
        update.message.reply_text('Предыдущий трек.')
    else:
        update.message.reply_text('Не удалось переключиться на предыдущий трек. Попробуйте еще раз.')


def spotify_menu(update: Update, context: CallbackContext) -> int:
    keyboard = [
        ['Микс дня', 'Любимое'],
        ['Главное меню']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text('Выберите плейлист:', reply_markup=reply_markup)

    return ConversationHandler.END  # Завершаем конвертацию после выбора пункта в подменю


def handle_messages(update: Update, context: CallbackContext) -> None:
    text = update.message.text.lower()

    if text == 'главное меню':
        main_menu(update, context)
    elif text == 'spotify':
        spotify_menu(update, context)
    elif text == 'погода':
        context.user_data['current_state'] = 'weather'
        update.message.reply_text('Выберите действие:\n1. Выбор города\n2. Показать погоду\n3. Назад')
    elif text == 'микс дня':
        play_playlist(update, 'https://open.spotify.com/playlist/37i9dQZF1E35tfLVW6ueIM?si=0aa3b288892a481c')
    elif text == 'любимое':
        play_playlist(update, 'https://open.spotify.com/playlist/3o0xN5NEkJ1at9NoVNPS7i')
    elif text == 'play':
        sp.start_playback()
    elif text == 'pause':
        sp.pause_playback()
    elif text == 'next track':
        sp.next_track()
    elif text == 'previous track':
        sp.previous_track()
    elif text == 'playlists':
        spotify_menu(update, context)
    elif text == 'выбор города':
        context.user_data['current_state'] = 'city_selection'
        update.message.reply_text('Введите название города:')
    elif text == 'показать погоду':
        handle_show_weather(update, context)
    elif text == 'назад':
        main_menu(update, context)
    else:
        update.message.reply_text('Неизвестная команда. Используйте /menu для открытия основного меню.')


def playback_buttons(update: Update) -> None:
    # Show buttons for playback controls
    keyboard = [
        [KeyboardButton("Play")],
        [KeyboardButton("Pause")],
        [KeyboardButton("Next track")],
        [KeyboardButton("Previous track")],
        [KeyboardButton("Playlists")],  # Добавляем кнопку для возврата к выбору плейлиста
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text('Управление воспроизведением:', reply_markup=reply_markup)


def play_playlist(update: Update, playlist_url: str) -> None:
    sp = get_spotify_object()

    if sp:
        try:
            playlist_id = get_playlist_id_from_url(playlist_url)
            sp.start_playback(context_uri=f'spotify:playlist:{playlist_id}')
            update.message.reply_text(f'Воспроизведение плейлиста начато: {playlist_url}')
            show_actions_menu(update)  # Показываем меню действий после начала воспроизведения
        except Exception as e:
            update.message.reply_text(f'Ошибка при воспроизведении плейлиста: {str(e)}')
    else:
        update.message.reply_text('Не удалось начать воспроизведение. Попробуйте еще раз.')


def show_actions_menu(update: Update) -> None:
    # Show buttons for playback controls
    keyboard = [
        [KeyboardButton("Play")],
        [KeyboardButton("Pause")],
        [KeyboardButton("Next track")],
        [KeyboardButton("Previous track")],
        [KeyboardButton("Playlists")],  # Добавляем кнопку для возврата к выбору плейлиста
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text('Управление воспроизведением:', reply_markup=reply_markup)


def get_playlist_id_from_url(playlist_url: str) -> str:
    parts = playlist_url.split('/')
    return parts[-1].split('?')[0]


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Привет! Я музыкально-информационный бот. Используй /help для списка команд.')


def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Доступные команды:\n'
                              '/play - начать воспроизведение\n/pause - поставить на паузу\n'
                              '/next - следующий трек\n/prev - предыдущий трек\n'
                              '/menu - открыть основное меню')


def handle_action_selection(update: Update, context: CallbackContext) -> int:
    action = update.message.text.lower()
    if action == 'spotify':
        # Выводим подменю Spotify
        return spotify_menu(update, context)


def main_menu(update: Update, context: CallbackContext) -> int:
    keyboard = [
        [KeyboardButton("Spotify")],
        [KeyboardButton("Погода")],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text('Выберите раздел:', reply_markup=reply_markup)

    return SELECT_ACTION


def main() -> None:
    updater = Updater("6946341086:AAFHUL5wAL_U78UEIKjwBLzAMl-cm3tb3Uw", use_context=True)
    dp = updater.dispatcher
    dp.bot_data["use_context"] = True

    dp.add_handler(weather_handler())

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("Spotify", spotify_menu))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("play", play))
    dp.add_handler(CommandHandler("pause", pause))
    dp.add_handler(CommandHandler("next", next_track))
    dp.add_handler(CommandHandler("prev", prev_track))
    dp.add_handler(CommandHandler("menu", main_menu))
    dp.add_handler(
        MessageHandler(Filters.text & ~Filters.command & ~Filters.regex(r'^/[a-zA-Z0-9_]+'), handle_messages))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
