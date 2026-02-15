from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.ext import CallbackQueryHandler
import logging
import random
import telegram

from dbhelper_2 import DBHelper
import utils

questions = [
    'Кто нарисовал эту картину? Выбери ответ.',
    'Кто художник этой картины? Выбери ответ.',
    'Красивая картина! А кто её художник? Выбери ответ.',
]
logger = logging.getLogger(__name__)


class Bot:
    download_enable = False

    def __init__(self, token, type_proxy=None, ip=None):
        request_kwargs = None
        if type_proxy and ip:
            request_kwargs = {type_proxy: ip}

        if request_kwargs:
            self.updater = Updater(token, request_kwargs=request_kwargs)
        else:
            self.updater = Updater(token=token)

        self.dp = self.updater.dispatcher

        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO,
        )

        self.dp.add_handler(CommandHandler("game", self.game))
        self.dp.add_handler(CommandHandler("scores", self.user_results))
        self.dp.add_handler(CallbackQueryHandler(self.check_answer))
        self.dp.add_handler(CommandHandler("im", self.download_image, pass_args=True))
        self.dp.add_handler(CommandHandler("help", self.user_help))
        self.dp.add_handler(MessageHandler(Filters.photo, self.image_handler))

        self.dp.add_error_handler(self.error)

    def download_image(self, bot, update, args):
        """Разрешение/запрещение загрузки изображений в БД."""
        if not args:
            update.message.reply_text("Используй: /im + | /im - | /im статус")
            return

        if args[0] == '+':
            self.download_enable = True
            update.message.reply_text("Загрузка изображений разрешена.")
        elif args[0] == '-':
            self.download_enable = False
            update.message.reply_text("Загрузка изображений запрещена.")
        elif args[0] == 'статус':
            update.message.reply_text("Текущий статус: " + str(self.download_enable))
        else:
            update.message.reply_text("Неверная команда!")

    def game(self, bot, update):
        db_worker = DBHelper()

        utils.count_rows()
        rows_count = utils.get_rows_count()
        if rows_count <= 0:
            update.message.reply_text("В базе пока нет картин для игры.")
            db_worker.close_connect()
            return

        picture_info = db_worker.select_single_pic_infos(utils.get_rand_num())
        if not picture_info:
            update.message.reply_text("Не удалось получить картину. Попробуй ещё раз.")
            db_worker.close_connect()
            return

        f = db_worker.select_author_name(utils.get_rand_num())
        wrong_answers = f[0][0]
        for _ in range(2):
            f = db_worker.select_author_name(utils.get_rand_num())
            wrong_answers += ", " + f[0][0]

        reply_markup = utils.generate_markup(picture_info[0][2], wrong_answers)

        bot.send_photo(chat_id=update.message.chat_id, photo=picture_info[0][1])
        update.message.reply_text(random.choice(questions), reply_markup=reply_markup)

        user_info = {
            'user_id': update.message.chat_id,
            'right_answers': utils.get_right_answers(),
            'wrong_answers': utils.get_wrong_answers(),
            'current_answer': picture_info[0][2],
        }
        utils.set_user_game(chat_id=update.message.chat_id, user_info=user_info)

        db_worker.close_connect()

    def check_answer(self, bot, update):
        query = update.callback_query

        answer = utils.get_answer_for_user(query.message.chat_id)
        if not answer:
            bot.send_message(chat_id=query.message.chat_id, text="Чтобы начать игру, введи команду /game")
            return

        if query.data == answer['current_answer']:
            bot.edit_message_text(
                text="Верно! Художник картины *{}*. \nВведи /game для следующего вопроса.".format(query.data),
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                parse_mode=telegram.ParseMode.MARKDOWN,
            )
            answer['right_answers'] = answer.get('right_answers', 0) + 1
            utils.set_user_game(chat_id=query.message.chat_id, user_info=answer)
        else:
            bot.edit_message_text(
                text="*Неверно*, художник этой картины не {}. Попробуй ещё раз! \nВведи /game для следующего вопроса.".format(query.data),
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                parse_mode=telegram.ParseMode.MARKDOWN,
            )
            answer['wrong_answers'] = answer.get('wrong_answers', 0) + 1
            utils.set_user_game(chat_id=query.message.chat_id, user_info=answer)

    def user_results(self, bot, update):
        answer = utils.get_answer_for_user(update.message.chat.id)
        if not answer:
            update.message.reply_text("Пока нет статистики. Начни игру командой /game")
            return

        update.message.reply_text(
            "Правильных ответов - " + str(answer["right_answers"]) +
            "\nНеправильных ответов - " + str(answer["wrong_answers"])
        )

    def user_help(self, bot, update):
        update.message.reply_text(
            'Игра "Угадай художника".\n'
            'Доступные команды:\n'
            '/game - начать игру\n'
            '/scores - общая статистика\n'
            '/help - доступные команды и описание бота\n\n'
            'feedback - @ykv_svr'
        )

    def image_handler(self, bot, update):
        if self.download_enable is True:
            if not update.message.caption:
                update.message.reply_text("Добавь подпись с именем художника.")
                return

            db_worker = DBHelper()
            author_name = update.message.caption.title()

            db_worker.insert_single_to_pic_infos(
                file_id=str(update.message.photo[-1].file_id),
                author_name=author_name,
            )

            update.message.reply_text("Изображение успешно добавлено.")
            db_worker.close_connect()
        else:
            update.message.reply_text("Добавление изображений запрещено!")

    def error(self, bot, update, error):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update, error)

    def run(self):
        self.updater.start_polling()
