import telebot
import re
from telebot import custom_filters, types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyParameters
from telebot.states import State, StatesGroup
from telebot.states.sync.context import StateContext
from telebot.storage import StateRedisStorage
from telebot.states.sync.middleware import StateMiddleware
from config.settings import BOT_TOKEN, REDIS_HOST, REDIS_PORT
from tasks.models import PERIOD, STATUS
from tasks.services.tasks import TaskConnector

# redis_storage = StateRedisStorage(
#     host=REDIS_HOST,
#     port=REDIS_PORT,
# )
# bot = telebot.TeleBot(
#     BOT_TOKEN,
#     state_storage=redis_storage
#     )

from telebot.storage import StateMemoryStorage
state_storage = StateMemoryStorage()  # don't use this in production; switch to redis
bot = telebot.TeleBot(
    BOT_TOKEN,
    state_storage=state_storage,
    use_class_middlewares=True,
    parse_mode="MARKDOWN"
    )
bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.add_custom_filter(custom_filters.IsDigitFilter())
bot.add_custom_filter(custom_filters.TextMatchFilter())
bot.setup_middleware(StateMiddleware(bot))


class MyStates(StatesGroup):
    task = State()
    annotation = State()
    category = State()
    create_category = State()
    category_list = State()
    task_list = State()
    time = State()
    period = State()
    create_finished = State()


def is_valid_time(time: str) -> bool:
    """
    Шаблон ^(?:(?:[01]?\d|2[0-3])[\D]+(?:[0-5]?\d))$:
   - ^(...)$ — начало и конец строки.
   - (?:...) — не захватывающая группа для идущих за ней частей.
   - [01]?\d — позволяющее часам быть от 00 до 19.
   - 2[0-3] — соответствует часам от 20 до 23.
   - [\D]+ — один или несколько нецифровых символов между часами и минутами.
   - (?:[0-5]?\d) — допускает минуты от 00 до 59.
    """

    # pattern = r'^(?:(?:[01]?\d|2[0-3])[\W_]*(?:[0-5]?\d))$'
    # pattern = r'^(?:(?:[01]?\d|2[0-3])[\D]+([0-5]?\d))$'
    pattern = r'^(?:(?:[01]?\d|2[0-3])[\D]+(?:[0-5]?\d))$'

    if re.match(pattern, time):
        return True
    return False


def escape_markdown(text):
    # Экранирование символов Markdown
    return re.sub(r'([*_`\[\]()~>#+\-=|{}.!])', r'\\\1', text)


def yes_no_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton(
            "Да",
            callback_data="create_task_yes"
            ),
        InlineKeyboardButton(
            "Нет",
            callback_data="create_task_no"
            ),
    )
    return markup


def start_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton(
            "Создать задачу",
            callback_data="create_task"
            ),
        InlineKeyboardButton(
            "Мои задачи",
            callback_data="my_tasks"
            ),
        InlineKeyboardButton(
            "Создать категорию",
            callback_data="create_category"
            ),
        InlineKeyboardButton(
            "Мои категории",
            callback_data="my_categories"
            ),
        InlineKeyboardButton(
            "Начать рассылку",
            callback_data="start_sending"
            ),
        InlineKeyboardButton(
            "Остановить рассылку",
            callback_data="stop_sending"
            ),
        InlineKeyboardButton(
            "Статус рассылки",
            callback_data="status"
            ),
    )
    return markup


def help_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton(
            "Старт",
            callback_data="start"
            ),
    )
    return markup


def categories_markup(categories, status='choice'):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    buttons = []
    for category in categories:
        button = InlineKeyboardButton(
                category['name'],
                callback_data=f"category_{status}_{category['id']}"
                )
        buttons.append(button)
    # if status == 'list':
    button = InlineKeyboardButton(
            'Без категории',
            callback_data=f"category_{status}_None"
            )
    buttons.append(button)
    markup.add(*buttons)
    return markup


def edit_task_markup(task_id):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton(
            "Показать описание",
            callback_data="annotation_task_{task_id}"
            ),
        InlineKeyboardButton(
            "Редактировать задачу",
            callback_data="edit_task_{task_id}"
            ),
        InlineKeyboardButton(
            "Удалить задачу",
            callback_data="delete_task_{task_id}"
            ),
        InlineKeyboardButton(
            "Настроить отправку",
            callback_data="send_task_{task_id}"
            ),
        InlineKeyboardButton(
            "Изменить статус",
            callback_data="status_task_{task_id}"
            ),
    )
    return markup


def tasks_markup(tasks, status='choice'):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    buttons = []
    for task in tasks:
        button = InlineKeyboardButton(
                task['name'],
                callback_data=f"task_{status}_{task['id']}"
                )
        buttons.append(button)
    markup.add(*buttons)
    return markup


def period_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    buttons = []
    for period in PERIOD:
        button = InlineKeyboardButton(
                period[1],
                # callback_data=f'period_{period[0]}'
                callback_data=f'{period[0]}'
                )
        buttons.append(button)
    markup.add(*buttons)
    return markup


# Handle '/help'
@bot.message_handler(commands=['help'])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        f'Привет, {message.chat.first_name}!\n\
        Этот бот создан для управления задачами.\n\
        Здесь можно настроить рассылку напоминаний о задачах по расписанию.\n\
        Для начала работы нажмите "Старт"',
        reply_markup=help_markup()
        )


# Handle button 'start'
@bot.callback_query_handler(func=lambda call: call.data == "start")
def handle_start_button(call: types.CallbackQuery):
    bot.send_message(
        call.message.chat.id,
        "Пожалуйста, выберите действие:",
        reply_markup=start_markup()
    )


# Handle '/start'
@bot.message_handler(commands=['start'])
def send_start(message):
    bot.send_message(
        message.chat.id,
        "Пожалуйста, выберите действие:",
        reply_markup=start_markup()
        )


@bot.callback_query_handler(func=lambda call: call.data == "create_task")
def handle_create_task(call: types.CallbackQuery, state: StateContext):
    state.set(MyStates.task)
    bot.send_message(call.message.chat.id, "Напишите название задачи")
    # Удаляем сообщение с кнопками после нажатия
    bot.delete_message(call.message.chat.id, call.message.message_id)


@bot.callback_query_handler(func=lambda call: call.data == "my_tasks")
def get_my_tasks(call: types.CallbackQuery, state: StateContext):
    msg = "Ваши задачи:\n"
    tasks = TaskConnector().get_user_tasks(call.message.chat.id)
    for task in tasks:
        msg += task['name']
        if 'annotation' in task and task['annotation']:
            msg += "*Описание:* " + task['annotation']
        status = dict(STATUS).get(task['status'])
        msg += " *Статус:* " + status + "\n"
    bot.send_message(call.message.chat.id, msg)
    # Удаляем сообщение с кнопками после нажатия
    # bot.delete_message(call.message.chat.id, call.message.message_id)


@bot.callback_query_handler(func=lambda call: call.data == "create_category")
def handle_create_category(call: types.CallbackQuery, state: StateContext):
    state.set(MyStates.create_category)
    bot.send_message(call.message.chat.id, "Напишите название категории")
    # Удаляем сообщение с кнопками после нажатия
    bot.delete_message(call.message.chat.id, call.message.message_id)


@bot.callback_query_handler(func=lambda call: call.data == "my_categories")
def get_my_categories(call: types.CallbackQuery, state: StateContext):
    msg = "Ваши категории:\n"
    categories = TaskConnector().get_user_categories(call.message.chat.id)
    bot.send_message(
        call.message.chat.id,
        msg,
        reply_markup=categories_markup(
            categories,
            status='list'
        )
        )
    # Удаляем сообщение с кнопками после нажатия
    # bot.delete_message(call.message.chat.id, call.message.message_id)


# @bot.message_handler(state="*", commands=["cancel"])
# def cancel(message: types.Message, state: StateContext):
#     bot.send_message(message.chat.id, "Информация о задаче очищена")
#     bot.delete_state(message.from_user.id)


@bot.message_handler(state=MyStates.task)
def task_get(message: types.Message, state: StateContext):
    state.set(MyStates.create_category)
    bot.send_message(
        message.chat.id, "Напишите описание задачи",
        reply_parameters=ReplyParameters(message_id=message.message_id),
    )
    state.add_data(task=message.text)


@bot.message_handler(state=MyStates.create_category)
def task_category(message: types.Message, state: StateContext):
    # state.set(MyStates.annotation)
    categories = TaskConnector().get_user_categories(message.chat.id)
    state.add_data(annotation=message.text)
    if categories:
        bot.send_message(
            message.chat.id,
            "Выберите категорию",
            reply_parameters=ReplyParameters(message_id=message.message_id),
            reply_markup=categories_markup(categories, status='choice')
        )
    else:
        bot.send_message(
            message.chat.id,
            "У вас пока нет категорий.  Задача будет создана без категории.",
            reply_parameters=ReplyParameters(message_id=message.message_id),
        )
        # create_task(message, state, None)
    state.set(MyStates.period)


@bot.callback_query_handler(
        func=lambda call: call.data.startswith("category_choice_")
        )
def handle_category_selection(call: types.CallbackQuery, state: StateContext):
    category_id = call.data.split("_")[2]
    if category_id == 'None':
        category_id = None
    state.add_data(category=category_id)

    # message = call.message
    # create_task(message, state, category_id)
    bot.send_message(
        call.message.chat.id,
        "Создать задачу?",
        # reply_parameters=ReplyParameters(message_id=call.message.message_id),
        reply_markup=yes_no_markup()
    )
    state.set(MyStates.create_finished)
    # Удаляем сообщение с кнопками после нажатия
    bot.delete_message(call.message.chat.id, call.message.message_id)


@bot.callback_query_handler(
        func=lambda call: call.data.startswith("category_list_")
        )
def handle_category_list(call: types.CallbackQuery, state: StateContext):
    category_id = call.data.split("_")[2]
    if category_id == 'None':
        category_id = None
    state.set(MyStates.category_list)
    state.add_data(category_list=category_id)

    message = call.message
    list_task(message, state, category_id)
    state.set(MyStates.category)


def list_task(message: types.Message, state: StateContext, category_id):
    """"
    Выводит список задач в указанной категории
    """
    tasks = TaskConnector().list_tasks(
        chat_id=message.chat.id,
        category_id=category_id
    )
    msg = ""
    if len(tasks):
        if 'category__name' in tasks[0] and tasks[0]['category__name']:
            msg = "Задачи в категории: " + tasks[0]['category__name']
        else:
            msg = "Задачи без категории: "
    else:
        msg = "Нет задач в данной категории."

    bot.send_message(
        message.chat.id,
        msg,
        reply_markup=tasks_markup(tasks, status='list')
        )


@bot.callback_query_handler(
        func=lambda call: call.data.startswith("task_list_")
        )
def handle_tasks_list(call: types.CallbackQuery, state: StateContext):
    task_id = call.data.split("_")[2]
    state.set(MyStates.task_list)
    state.add_data(task_list=task_id)

    message = call.message
    msg = f"*Задача* task_id={task_id}"
    print("msg=", msg, "call.message.chat.id=", call.message.chat.id)
    bot.send_message(
        call.message.chat.id,
        # msg,
        "Пожалуйста, выберите действие:",
        reply_markup=edit_task_markup(task_id)
        )


# @bot.message_handler(state=MyStates.period)
@bot.callback_query_handler(
        # func=lambda call: call.data in ['DAILY', 'WEEKLY', 'MONTHLY', 'YEARLY', 'CUSTOM_DAY']
        func=lambda call: call.data in [period[0] for period in PERIOD]
)
def get_time(call: types.CallbackQuery, state: StateContext):
    print('get_period')
    print("call.data=", call.data)
    state.set(MyStates.period)
    period = call.data
    state.add_data(period=period)

    bot.send_message(
        call.message.chat.id,
        'Введите время, в которое следует напоминать о задаче в формате "чч:мм". Часы: 0-23, минуты: 0-59, между ними может быть любой разделитель, кроме цифр.',
        # reply_markup=keyboard
        )
    state.set(MyStates.time)


# @bot.callback_query_handler(func=lambda call: True)
# def handle_time(call: types.CallbackQuery, state: StateContext):
@bot.message_handler(state=MyStates.time)
def check_time_(message: types.Message, state: StateContext):
    print('time_get')
    # time = state.data().data.get("time")
    time = message.text
    if is_valid_time(time):
        bot.send_message(
            message.chat.id, "Время установлено корректно",
            reply_parameters=ReplyParameters(message_id=message.message_id),
        )
        state.set(MyStates.create_finished)
        state.add_data(time=time)
    else:
        bot.send_message(
            message.chat.id, "Время введено некорректно. Попробуйте еще раз.",
            reply_parameters=ReplyParameters(message_id=message.message_id),
        )
        bot.send_message(
            message.chat.id,
            'Введите время, в которое следует напоминать о задаче в формате "чч:мм". Часы: 0-23, минуты: 0-59, между ними может быть любой разделитель, кроме цифр.',
        )
        time = message.text
        if is_valid_time(time):
            state.set(MyStates.create_finished)
            state.add_data(time=time)
        else:
            bot.send_message(
                message.chat.id,
                "Время рассылки не установлено. Попробуйте сначала.",
            )
            state.delete()


def create_task(message: types.Message, state: StateContext, task, annotation, category_id):
    """Создает задачу с указанной категорией."""
    task = TaskConnector().create_task(
        chat_id=message.chat.id,
        name=task,
        annotation=annotation,
        category=category_id
    )
    return task


@bot.callback_query_handler(
        # func=lambda state: state == MyStates.create_finished
        func=lambda call: call.data in ["create_task_yes", "create_task_no"]
)
def task_creation(call: types.CallbackQuery, state: StateContext):
# @bot.message_handler(state=MyStates.create_finished)
# def create_task_finished(message: types.Message, state: StateContext):
    print("call.data=", call.data)
    msg = ""
    if call.data == "create_task_yes":
        with state.data() as data:
            task = data.get("task")
            annotation = data.get("annotation")
            category_id = data.get("category")
            msg = (
                f"Задача: {task}\n"
                f"Описание: {annotation}\n"
                f"category_id: {category_id}\n"
            )
            try:
                task = create_task(call.message, state, task, annotation, category_id)
                if task:
                    msg += "Задача успешно создана!"
                else:
                    msg += "Задача не создана."
            except Exception as e:
                msg = f"Ошибка при создании задачи {e}"
        bot.send_message(
            call.message.chat.id,
            escape_markdown(msg),
            reply_parameters=ReplyParameters(message_id=call.message.message_id),
        )
    state.delete()


@bot.message_handler(state=MyStates.create_category)
def create_category(message: types.Message, state: StateContext):
    name = message.text
    try:
        category = TaskConnector().create_category(
            chat_id=message.chat.id,
            name=name,
        )
        msg = (
            f"Создана категория: *{name}*\n"
        )
    except Exception as e:
        msg = f"Ошибка при создании категориии {e}"
    bot.send_message(
        message.chat.id, msg,
        reply_parameters=ReplyParameters(message_id=message.message_id),
    )
    state.delete()

# @bot.message_handler(state=MyStates.period)
# def finish(message: types.Message, state: StateContext):
#     print('finish')
#     period = message.text

#     # Получаем данные из хранилища состояний
#     with bot.get_data(message.from_user.id) as data:
#         name = data.get("name")
#         annotation = data.get("annotation")
#         time = data.get("time")
#         period = data.get("period")
#         msg = f"Thank you for sharing! Here is a summary of your information:\n" \
#           f"Name: {name}\n" \
#           f"annotation: {annotation}\n" \
#           f"time: {time}\n" \
#           f"period: {period}"

#     bot.send_message(message.chat.id, msg)

    # Очищаем состояния после завершения
    # bot.delete_state(message.from_user.id)

@bot.message_handler(commands=['test'])
def send_test(message):
    bot.send_message(
        message.chat.id,
        "Введите периодичность рассылки напоминаний (test)",
        reply_parameters=ReplyParameters(message_id=message.message_id),
        reply_markup=period_markup()
    )


def run_bot():
    bot.infinity_polling()
