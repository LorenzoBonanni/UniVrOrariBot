import json
import logging
import yaml
import telegram

from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from DataHandler import DataHandler

year2data = {}
value_label = {}
timetable = None
CONFIG_FILE = "config.yaml"
TOKEN = None

with open(CONFIG_FILE) as conf_file:
    conf = yaml.load(conf_file, Loader=yaml.BaseLoader)
    TOKEN = conf['token']

updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Benvenuto, per iniziare scrivi /settings")


def settings(update, context):
    DataHandler.set_uid(update.effective_chat.id)
    years = DataHandler.get_years()
    button_list = []
    for yearArr in years:
        tmp_arr = []
        cb_data = json.dumps({"anno": yearArr[1]})
        tmp_arr.append(InlineKeyboardButton(yearArr[0], callback_data=cb_data))
        button_list.append(tmp_arr)

    reply_markup = InlineKeyboardMarkup(button_list)
    update.message.reply_text('Anno Accademico:', reply_markup=reply_markup)


def course(year, update, context):
    courses = DataHandler.get_courses(year)
    button_list = []
    for courseArr in courses:
        tmp_arr = []
        cb_data = json.dumps({"corso": courseArr[1]})
        year2data[courseArr[1]] = courseArr[2]
        tmp_arr.append(InlineKeyboardButton(courseArr[0], callback_data=cb_data))
        button_list.append(tmp_arr)
    reply_markup = InlineKeyboardMarkup(button_list)

    context.bot.send_message(chat_id=update.effective_chat.id, text="Corso di Studi:", reply_markup=reply_markup)


def year2(selected_course, update, context):
    year2_data = year2data[selected_course]
    button_list = []

    for year2arr in year2_data:
        value_label[year2arr["valore"]] = year2arr["label"]
        tmp_arr = []
        cb_data = json.dumps({"year2": year2arr["valore"]})
        tmp_arr.append(InlineKeyboardButton(year2arr["label"], callback_data=cb_data))
        button_list.append(tmp_arr)

    reply_markup = InlineKeyboardMarkup(button_list)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Anno di Studio:", reply_markup=reply_markup)


def callback(update, context):
    cqd = json.loads(update.callback_query.data)
    if "anno" in cqd:
        DataHandler.set_year(cqd["anno"], update.effective_chat.id)
        course(cqd["anno"], update, context)
    elif "corso" in cqd:
        DataHandler.set_course(cqd["corso"], update.effective_chat.id)
        year2(cqd["corso"], update, context)
    else:
        DataHandler.set_year2(cqd["year2"], update.effective_chat.id)
        DataHandler.set_txt_curr(value_label[cqd["year2"]], update.effective_chat.id)
        context.bot.send_message(chat_id=update.effective_chat.id, text="Finito.\n" +
                                                                        " inserisci:\n " +
                                                                        "/week per vedere l'oraio settimanale\n" +
                                                                        "/today per vedere l'oraio di oggi\n"
                                 )


def days_between(d1, d2):
    d1 = datetime.strptime(d1, "%d/%m/%Y")
    d2 = datetime.strptime(d2, "%d/%m/%Y")
    return abs((d2 - d1).days)


def today(update, context):
    days = ["LUNEDÌ", "MARTEDÌ", "MERCOLEDÌ", "GIOVEDÌ", "VENERDÌ"]
    data = DataHandler.get_timetable(update.effective_chat.id)
    first_day = data["first_day"]
    day_difference = days_between(first_day, datetime.now().strftime("%d/%m/%Y"))
    if day_difference == 5:
        # convert day difference to respect array positions
        day_difference -= 1
    elif day_difference == 6:
        day_difference -= 1

    text = "*" + days[day_difference] + "*\n"
    for lesson in data["lezioni"]:
        if int(lesson["giorno"]) == day_difference+1:
            text += get_lesson_text(lesson) + "\n\n"
    context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode=telegram.ParseMode.MARKDOWN)


def get_lesson_text(lesson):
    return "*Orario*: " + lesson["ora_inizio"] + " - " + lesson["ora_fine"] + "\n" + \
           "*Insegnamento*: " + lesson["nome_insegnamento"] + "\n" + \
           "*Docente*: " + lesson["docente"] + "\n" + \
           "*Aula*: " + lesson["aula"]


def week(update, context):
    data = DataHandler.get_timetable(update.effective_chat.id)
    days = ["LUNEDÌ", "MARTEDÌ", "MERCOLEDÌ", "GIOVEDÌ", "VENERDÌ"]
    day_number = 0
    day = None
    text = ""
    for lesson in data["lezioni"]:
        if lesson["giorno"] != day_number:
            day = days[int(lesson["giorno"]) - 1]
            day_number = lesson["giorno"]
            text += "*" + day + "*\n"
        text += get_lesson_text(lesson) + "\n\n"
    context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode=telegram.ParseMode.MARKDOWN)


def help(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="/week per vedere l'oraio settimanale\n" +
                                                                    "/today per vedere l'oraio di oggi\n" +
                                                                    "/settings per cambiare anno accademico o corso di studi"
                             )


def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


# start handler
dispatcher.add_handler(CommandHandler('start', start))

# help handler
dispatcher.add_handler(CommandHandler('help', help))

# settings handler
dispatcher.add_handler(CommandHandler('settings', settings))

# today handler
dispatcher.add_handler(CommandHandler('today', today))

# week handler
dispatcher.add_handler(CommandHandler('week', week))

# unknown command handler
dispatcher.add_handler(MessageHandler(Filters.command, unknown))

# callback handler
dispatcher.add_handler((CallbackQueryHandler(callback)))

updater.start_polling()
