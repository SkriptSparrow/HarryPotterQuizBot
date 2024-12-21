import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
import random
import os


async def start(update, context) -> None:
    context.chat_data["correct_answers"] = 0

    hallo_img = os.path.join('images', 'quiz.jpeg')
    if update.message:
        user_first_name = update.message.from_user.first_name
    elif update.callback_query:
        user_first_name = update.callback_query.from_user.first_name
    else:
        user_first_name = "Гость"

    welcome_message = (
        f"Приветствую {user_first_name}.Добро пожаловать на викторину по вселенной Гарри Поттера!\n\n"
        "Здесь ты сможешь проверить насколько хорошо ты знаком(а) с книгами и фильмами о мальчике-волшебнике.\n"
        "В этой викторине вопросы разной сложности. Перед тем как дать ответ, необходимо "
        "очень внимательно прочитать вопрос и ознакомиться с вариантами ответов.\n"
        "Желаю тебе удачи!"
    )

    keyboard = [[InlineKeyboardButton("Начать викторину", callback_data='questions')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_photo(
            hallo_img,
            caption=welcome_message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    elif update.callback_query:
        await update.callback_query.message.reply_photo(
            hallo_img,
            caption=welcome_message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )


def load_questions():
    with open("questions_answers.json", "r", encoding="utf-8") as file:
        return json.load(file)


questions_data = load_questions()


async def questions(update, context):
    """Отправляет пользователю вопрос викторины и обрабатывает ответ."""
    if "progress" not in context.chat_data:
        context.chat_data["progress"] = 0  # Инициализация прогресса, если его нет

    progress = context.chat_data["progress"]
    # Увеличиваем прогресс
    context.chat_data["progress"] += 1

    if progress >= len(questions_data):
        await finish(update, context)
        context.chat_data["progress"] = 0  # Сбрасываем прогресс
        return

    current_question = questions_data[progress]
    question_text = current_question["question"]
    options = current_question["options"]
    question_image = current_question["image"]

    keyboard = [
        [InlineKeyboardButton(option, callback_data=str(index))]
        for index, option in enumerate(options)
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Проверка на наличие message в update
    if update.message:
        await update.callback_query.message.reply_photo(
            photo=question_image,
            caption=question_text,
            reply_markup=reply_markup
        )

    elif update.callback_query:
        await update.callback_query.message.reply_photo(
            photo=question_image,
            caption=question_text,
            reply_markup=reply_markup
        )


async def handle_answer(update, context):
    """Проверяет, правильный ли ответ дал пользователь."""
    query = update.callback_query
    await query.answer()  # Подтверждаем получение ответа

    # Получаем текущий прогресс
    progress = context.chat_data.get("progress", 1) - 1
    current_question = questions_data[progress]
    correct_answer = current_question["correct"]

    # Проверяем правильность ответа
    if int(query.data) == correct_answer:
        context.chat_data["correct_answers"] += 1
        random_good_reaction = random.choice(good_reactions)
        await query.message.reply_text(random_good_reaction)
        await questions(update, context)

    else:
        random_bad_reactions = random.choice(bad_reactions)
        await query.message.reply_text(random_bad_reactions)
        await questions(update, context)


good_reactions = [
    "Правильно! Молодец!", "Отлично справляешься!", "Да ты всё знаешь!",
    "И это правильный ответ!", "А ты умник!", "Совершенно верно!",
    "Отличная игра!", "Замечательно!", "Ты истинный фанат!", "Точно в цель!",
    "Блестящий ответ!", "Ты просто мастер!", "Ответ абсолютно правильный!",
    "Это было впечатляюще!", "У тебя талант!", "Супер! Так держать!", "Правильный выбор!",
    "Я бы и сам так не ответил!", "Фантастика! Ты гений!", "Твой интеллект поражает!",
    "На 100% правильно!", "Ты просто космос!", "Я горжусь тобой!", "Ну ты молодец, что сказать!"
]

bad_reactions = [
    "Это неверный ответ.", "Ты был близок.", "Эх, Семён Семёныч...", "А вот и мимо...",
    "К сожалению, не верно", "Пу-пу-пу... не правильно", "Надо лучше стараться.",
    "Кажется, кому-то пора пересмотреть Гарри Поттера.", "Увы, мимо...", "Нет, это не то.",
    "Бывает, не расстраивайся.", "Ну ничего, в следующий раз получится!", "На этот раз не угадали.",
    "Не совсем так...", "Ой-ой, не туда!", "Упс! Это не верно.", "Неправильно, но попытка была хорошей!",
    "К сожалению, нет.", "Придётся ещё раз попробовать!", "Чуть-чуть не хватило!", "Не то, но ты близко!",
    "Не в этот раз."
]


async def finish(update, context):
    final_img = os.path.join('images', 'final.jpg')

    # Проверяем тип обновления
    if update.callback_query:
        query = update.callback_query
        await query.answer()  # Подтверждаем получение callback-запроса
        target_message = query.message
    elif update.message:
        target_message = update.message
    else:
        # Если ни message, ни callback_query нет
        return

    # Очищаем пользовательские данные
    context.user_data.clear()

    # Создаем кнопку для повторного старта
    keyboard = [[InlineKeyboardButton("Start", callback_data='start')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправляем финальное изображение и сообщение
    await target_message.reply_photo(final_img)
    await target_message.reply_text(
        f"Вы ответили правильно на {context.chat_data['correct_answers']} из {len(questions_data)} вопросов!\n"
        "Вы всегда можете вернуться и пройти викторину еще раз!",
        reply_markup=reply_markup
    )


def main() -> None:
    application = Application.builder().token('token').build()

    # Обработчики команд и кнопок
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(start, pattern='^start$'))
    application.add_handler(CallbackQueryHandler(questions, pattern='^questions$'))
    application.add_handler(CallbackQueryHandler(handle_answer, pattern=r'^\d+$'))
    application.run_polling()


if __name__ == '__main__':
    main()
