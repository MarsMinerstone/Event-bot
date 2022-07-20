from aiogram import types
from dispatcher import *
from bot import BotDB
import keyboards as kb
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types.message import ContentType
from commands import *
from config import ADMIN, YOUTOKEN, CHANNEL
# from aiogram.methods import StopPoll
# import asyncio
from channels import channels
import re


# support commands ----------------------------------------
# support commands ----------------------------------------
# support commands ----------------------------------------


def get_start_message(user_id: int):
    if user_id == ADMIN:
        return "Добро пожаловать, администратор"
    else:
        return "Хочу разместить:"


def get_keyboard(user_id: int):
    if user_id == ADMIN:
        return kb.right_admin_keyboard
    else:
        return kb.right_keyboard


def add_username(text: str, username: str):
    if username is not None:
        text += f"\n\n@{username}"
    return text


# start ----------------------------------------
# start ----------------------------------------
# start ----------------------------------------


@dp.message_handler(commands="start")
async def start(message: types.Message):
    if not BotDB.user_exists(message.from_user.id):
        BotDB.add_user(message.from_user.id, message.from_user.username)

    user = message.from_user.id
    
    await bot.send_message(user, get_start_message(user), reply_markup=get_keyboard(user))


# actions with users ----------------------------------------
# actions with users ----------------------------------------
# actions with users ----------------------------------------


@dp.message_handler(Text(contains="Список пользователей", ignore_case=True))
async def get_users(message: types.Message):

    user = message.from_user.id

    if user == ADMIN:
        u_list = list(k[0] for k in list(j for j in BotDB.get_usernames()))
        u_list_str = ""
        for i in u_list:
            if i is not None:
                u_list_str += f"@{i}\n"

        await bot.send_message(user, u_list_str)


# advisory ----------------------------------------
# advisory ----------------------------------------
# advisory ----------------------------------------


@dp.message_handler(Text(contains="Разместить рекламу", ignore_case=True))
async def set_ad(message: types.Message):

    user = message.from_user.id

    await bot.send_message(user, get_advisory())


# cancel ----------------------------------------
# cancel ----------------------------------------
# cancel ----------------------------------------


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    """ Allow user to cancel any action """

    current_state = await state.get_state()
    if current_state is not None:
        await state.finish()

    user = message.from_user.id

    await bot.send_message(user, 'Отменено', reply_markup=get_keyboard(user))


# spam ----------------------------------------
# spam ----------------------------------------
# spam ----------------------------------------


class FormSpam(StatesGroup):
    to_user = State()
    check = State()


@dp.message_handler(Text(contains="Отпрвавить сообщение подписчикам", ignore_case=True))
async def spam_handler(message: types.Message):

    user = message.from_user.id

    if user != ADMIN:
        return

    await FormSpam.to_user.set()

    await bot.send_message(user, "Нажмите «cancel» для остановки", reply_markup=kb.cancel_kb)
    await bot.send_message(user, "Напишите сообщение")


@dp.message_handler(state=FormSpam.to_user)
async def spam_message_handler(message: types.Message, state: FSMContext):

    user = message.from_user.id

    async with state.proxy() as data:
        data['to_user'] = message.text

    await FormSpam.next()
    await bot.send_message(user, f"Сообщение будет выглядеть так: \n\n{data['to_user']}", 
                           reply_markup=kb.inline_kb_as)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('asend'), state=FormSpam.check)
async def process_callback_send_spam(callback_query: types.CallbackQuery, state: FSMContext):

    code = callback_query.data[-1]
    if code.isdigit():
        code = int(code)

    user = callback_query.from_user.id

    async with state.proxy() as data:
        pass

    if code == 1:
        await bot.send_message(user, "Производится отрпавка", reply_markup=get_keyboard(user))

        u_list = BotDB.get_all_users_id()
        c = 0
        for u in u_list:
            c += 1
            try:
                await bot.send_message(u[0], data['to_user'])
                # print("OK")
            except Exception:
                continue
            # await asyncio.sleep(20)

        await bot.send_message(user, f"Сообщение было отправленно {c} пользователям")

    elif code == 2:
        await bot.send_message(user, "Отправка отменена", reply_markup=get_keyboard(user))

    await state.finish()


# work ----------------------------------------
# work ----------------------------------------
# work ----------------------------------------


class FormWork(StatesGroup):
    wplace = State()
    spec = State()
    task = State()
    exp = State()
    conditions = State()
    wcontacts = State()
    end_work = State()

    full_work = State()


@dp.message_handler(Text(contains="Разместить вакансию", ignore_case=True))
async def set_work_handler(message: types.Message):

    user = message.from_user.id

    await FormWork.wplace.set()

    await bot.send_message(user, "Нажмите «cancel» для остановки", reply_markup=kb.cancel_kb)
    await bot.send_message(user, "Где вам нужен работник?", reply_markup=kb.inline_kb_wp)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('wplace'), state=FormWork.wplace)
async def process_callback_work_kb(callback_query: types.CallbackQuery, state: FSMContext):

    code = callback_query.data[-1]
    if code.isdigit():
        code = int(code)

    user = callback_query.from_user.id

    a = {1: "Удалёнка", 2: "Москва", 3: "Санкт-Петербург"}

    async with state.proxy() as data:
        data['wplace'] = a.get(code)

    await FormWork.next()
    await bot.send_message(user,
                           "Должность / специалист\n"
                           "(например: дизайнер, копирайтер, вебмастер и тд)\n",
                           reply_markup=kb.inline_kb_work)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('work'), state=FormWork.spec)
async def full_work_handler(callback_query: types.CallbackQuery, state: FSMContext):

    user = callback_query.from_user.id

    await FormWork.full_work.set()

    await bot.send_message(user, "Пришлите свой готовый текст")


@dp.message_handler(state=FormWork.full_work)
async def process_full_work(message: types.Message, state: FSMContext):

    user = message.from_user.id

    async with state.proxy() as data:
        data['full_work'] = message.text

    work_text = f"*ВАКАНСИЯ* \n\n{data['wplace']} \n\n{data['full_work']}"

    u = message.from_user.username

    await bot.send_message(ADMIN, add_username(work_text, u))

    await bot.send_message(user, "Вакансия успешно отправлена администратору", reply_markup=get_keyboard(user))

    await state.finish()


@dp.message_handler(state=FormWork.spec)
async def process_cpec(message: types.Message, state: FSMContext):

    user = message.from_user.id

    async with state.proxy() as data:
        data['spec'] = message.text

    await FormWork.next()

    await bot.send_message(user, "Задачи / что нужно сделать\n(например: \n"
                        "- оформить группу \n"
                        "- написать продающие тексты \n"
                        "- создать сайт и тд)")


@dp.message_handler(state=FormWork.task)
async def process_task(message: types.Message, state: FSMContext):

    user = message.from_user.id

    async with state.proxy() as data:
        data['task'] = message.text

    await FormWork.next()

    await bot.send_message(user, "Требования / опыт, особые умения и тп \n"
                        "(например: \n"
                        "- умение верстать приложения \n"
                        "- врожденная грамотность и тд)")


@dp.message_handler(state=FormWork.exp)
async def process_exp(message: types.Message, state: FSMContext):

    user = message.from_user.id

    async with state.proxy() as data:
        data['exp'] = message.text

    await FormWork.next()

    await bot.send_message(user, "Условия (оплата, оформление и тп)")


@dp.message_handler(state=FormWork.conditions)
async def process_conditions(message: types.Message, state: FSMContext):

    user = message.from_user.id

    async with state.proxy() as data:
        data['conditions'] = message.text

    await FormWork.next()

    await bot.send_message(user, "Укажите контакты (желательно ТГ)")


@dp.message_handler(state=FormWork.wcontacts)
async def process_contacts_work(message: types.Message, state: FSMContext):

    user = message.from_user.id

    async with state.proxy() as data:
        data['wcontacts'] = message.text

    await FormWork.next()

    await bot.send_message(user, f"Место\n{data['wplace']}\n\n"
                                 f"Должность\n{data['spec']}\n\n"
                                 f"Задачи\n{data['task']}\n\n"
                                 f"Требования\n{data['exp']}\n\n"
                                 f"Условия\n{data['conditions']}\n\n"
                                 f"Контакты\n{data['wcontacts']}\n\n",
                           reply_markup=kb.inline_kb_ws)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('wend'), state=FormWork.end_work)
async def finished_work_handler(callback_query: types.CallbackQuery, state: FSMContext):

    code = callback_query.data[-1]
    if code.isdigit():
        code = int(code)

    user = callback_query.from_user.id

    async with state.proxy() as data:
        pass

    if code == 1:
        fin_text = "*ВАКАНСИЯ*\n\n"\
                    f"Место\n{data['wplace']}\n\n"\
                    f"Должность\n{data['spec']}\n\n"\
                    f"Задачи\n{data['task']}\n\n"\
                    f"Требования\n{data['exp']}\n\n"\
                    f"Условия\n{data['conditions']}\n\n"\
                    f"Контакты\n{data['wcontacts']}"

        u = callback_query.from_user.username

        await bot.send_message(ADMIN, add_username(fin_text, u))

        await bot.send_message(user,
                               "Вакансия успешно отправлена администратору", 
                               reply_markup=get_keyboard(user))

    elif code == 2:
        await bot.send_message(user, "Вакансия удалена", reply_markup=get_keyboard(user))

    await state.finish()


# resume ----------------------------------------
# resume ----------------------------------------
# resume ----------------------------------------


class Form(StatesGroup):
    place = State()
    name = State()
    deal = State()
    unique = State()
    work = State()
    port = State()
    contacts = State()
    end_resume = State()

    full_resume = State()


@dp.message_handler(Text(contains="Разместить резюме", ignore_case=True))
async def set_resume(message: types.Message):

    user = message.from_user.id

    await Form.place.set()

    await bot.send_message(user, "Нажмите «cancel» для остановки",
                                   reply_markup=kb.cancel_kb)

    await bot.send_message(user,
                                   "Где вы хотите работать?",
                                   reply_markup=kb.inline_kb_rp)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('place'), state=Form.place)
async def process_callback_resume_kb(callback_query: types.CallbackQuery, state: FSMContext):

    code = callback_query.data[-1]
    if code.isdigit():
        code = int(code)

    a = {1: "Удалёнка", 2: "Москва", 3: "Санкт-Петербург"}

    user = callback_query.from_user.id

    async with state.proxy() as data:
        data['place'] = a.get(code)

    await Form.next()
    await bot.send_message(user, "Как вас зовут?", reply_markup=kb.inline_kb_resume)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('resume'), state=Form.name)
async def full_resume_handler(callback_query: types.CallbackQuery, state: FSMContext):

    user = callback_query.from_user.id

    await Form.full_resume.set()

    await bot.send_message(user, "Пришлите свой готовый текст")


@dp.message_handler(state=Form.full_resume)
async def process_full_resume(message: types.Message, state: FSMContext):

    user = message.from_user.id

    async with state.proxy() as data:
        data['full_resume'] = message.text

    # resume_text = f"{data['place']} \n\n{data['full_resume']}"
    resume_text = f"{data['full_resume']}"

    u = message.from_user.username

    # await bot.send_message(ADMIN, add_username(resume_text, u))
    resume_id = BotDB.create_resume(user, resume_text)

    await bot.send_message(user, f"Резюме №{resume_id} успешно добавлено в базу", reply_markup=get_keyboard(user))

    await state.finish()


@dp.message_handler(state=Form.name)
async def process_name(message: types.Message, state: FSMContext):

    user = message.from_user.id

    async with state.proxy() as data:
        data['name'] = message.text

    await Form.next()
    await bot.send_message(user, "Чем Вы занимаетесь?\n(например: я - сторисмейкер; дизайнер; копирайтер и т.д.)")


@dp.message_handler(state=Form.deal)
async def process_deal(message: types.Message, state: FSMContext):

    async with state.proxy() as data:
        data['deal'] = message.text
    await Form.next()

    user = message.from_user.id

    await bot.send_message(user, "Чем Вы уникальны?\n(например: проходил(а) курсы по повышению мастерства;"
                        " имею опыт работы 100 лет и т.п.)")


@dp.message_handler(state=Form.unique)
async def process_unique(message: types.Message, state: FSMContext):

    user = message.from_user.id

    async with state.proxy() as data:
        data['unique'] = message.text

    await Form.next()

    await bot.send_message(user, "Что Вы предлагаете людям и на каких условиях?\n(например: предлагаю за отзыв "
                        "оформить страницу; за 5К/мес буду дизайнить и т.п.)")


@dp.message_handler(state=Form.work)
async def process_work(message: types.Message, state: FSMContext):

    user = message.from_user.id

    async with state.proxy() as data:
        data['work'] = message.text

    await Form.next()

    await bot.send_message(user, "Есть ли портфолио? (прикрепить ссылку)")


@dp.message_handler(state=Form.port)
async def process_port(message: types.Message, state: FSMContext):

    user = message.from_user.id

    async with state.proxy() as data:
        data['port'] = message.text

    await Form.next()

    await bot.send_message(user, "Укажите контакты (желательно ТГ)")


@dp.message_handler(state=Form.contacts)
async def process_contacts_resume(message: types.Message, state: FSMContext):

    user = message.from_user.id

    async with state.proxy() as data:
        data['contacts'] = message.text

    await bot.send_message(user, f"Место\n{data['place']}\n\n"
                                 f"Имя\n{data['name']}\n\n"
                                 f"Занятие\n{data['deal']}\n\n"
                                 f"Уникальность\n{data['unique']}\n\n"
                                 f"Предлагаю\n{data['work']}\n\n"
                                 f"Портфолио\n{data['port']}\n\n"
                                 f"Контакты\n{data['contacts']}\n\n"
                                 f"Внимание, Размещение резюме на наших каналах платно.",
                           reply_markup=kb.inline_kb_rs)

    await Form.next()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('end'), state=Form.end_resume)
async def finished_resume_handler(callback_query: types.CallbackQuery, state: FSMContext):

    code = callback_query.data[-1]
    if code.isdigit():
        code = int(code)

    user = callback_query.from_user.id

    async with state.proxy() as data:
        pass

    if code == 1:
        fin_text = "*РЕЗЮМЕ*\n\n"\
                    f"Место\n{data['place']}\n\n"\
                    f"Имя\n{data['name']}\n\n"\
                    f"Занятие\n{data['deal']}\n\n"\
                    f"Уникальность\n{data['unique']}\n\n"\
                    f"Предлагаю\n{data['work']}\n\n"\
                    f"Портфолио\n{data['port']}\n\n"\
                    f"Контакты\n{data['contacts']}"

        u = callback_query.from_user.username

        await bot.send_message(ADMIN, add_username(fin_text, u))

        await bot.send_message(user, "Резюме успешно отправлено Администратору", reply_markup=get_keyboard(user))

    elif code == 2:
        await bot.send_message(user, "Резюме удалено", reply_markup=get_keyboard(user))

    await state.finish()


# resume checkout ----------------------------------------
# resume checkout ----------------------------------------
# resume checkout ----------------------------------------


class FormComment(StatesGroup):
    resume_user = State()


@dp.message_handler(Text(contains="Список резюме", ignore_case=True))
async def resume_check(message: types.Message, flag: int = 0):

    user = message.from_user.id

    if user != ADMIN and flag == 0:
        return

    result = BotDB.get_last_resume()
    if result is not None:
        text = f"Резюме №{result[0]} \n\n{result[2]}"

        if flag == 0:     
            await bot.send_message(ADMIN, text, reply_markup=kb.create_approve_kb(result[0], result[1]))
            
        elif flag == 1:
            await message.edit_text(text, reply_markup=kb.create_approve_kb(result[0], result[1]))
    else:
        await bot.send_message(ADMIN, "Список резюме пока пуст")

    
@dp.callback_query_handler(lambda c: c.data and c.data.startswith('approve'))
async def process_callback_resume_check(callback_query: types.CallbackQuery, state: FSMContext):

    resumeid_userid_code = callback_query.data.replace("approve", "")

    resumeid, userid, code = resumeid_userid_code.split("_")

    if code.isdigit():
        code = int(code)

    if code == 1:                         
        BotDB.update_approved(resumeid)

        text = f"Резюме №{resumeid} готово к оплате \n\nВыберите каналы, в котором хотите опубликовать резюме: \n"

        for i in channels:
            text += f"{i}:\n"
            for j in channels[i]:
                text += f"{j[0]}: {j[2]}р \n"

        # await bot.send_message(userid, text, reply_markup=kb.create_pay_kb(resumeid, userid))
        await bot.send_message(userid, text, reply_markup=kb.create_channels_kb(channels))

        await resume_check(callback_query.message, 1)

    elif code == 2:                                               
        await FormComment.resume_user.set()

        await state.update_data(resume_user=f"{resumeid}_{userid}")

        BotDB.delete_disapproved(resumeid)

        await callback_query.message.edit_text("Отклонено", reply_markup=kb.inline_kb_empty)
        await bot.send_message(ADMIN, "Напишите сообщение для этого пользователя:", 
                               reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=FormComment.resume_user)
async def comment(message: types.Message, state: FSMContext):

    async with state.proxy() as data:
        resumeid, userid = data['resume_user'].split("_")

    await bot.send_message(userid, f"Резюме №{resumeid} \n\nКомментарий от администратора: \n{message.text} \
                                   \n\nСоздайте резюме заново")

    await bot.send_message(ADMIN, "Сообщение было отправленно", reply_markup=get_keyboard(ADMIN))

    await state.finish()

    await resume_check(message)


# resume pay ----------------------------------------
# resume pay ----------------------------------------
# resume pay ----------------------------------------


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('channels'))
async def process_callback_choose_channels(callback_query: types.CallbackQuery):

    userid = callback_query.from_user.id

    code = callback_query.data.replace("channels_", "")

    text, info = callback_query.message.text.split(":", 1)

    if f"✅{code}:" in info:
        info = info.replace(f"✅{code}:", f"{code}:")
    else:
        info = info.replace(f"{code}:", f"✅{code}:")

    a = info.split("\n")   # price counting
    price = 0
    for i in a:
        if "✅" in i:
            p = re.compile("\d+р")
            addiction = int(p.search(i).group().replace("р", ""))
            price += addiction

    p = re.compile("№\d")
    resumeid = int(p.search(text).group().replace("№", ""))

    new_text = f"{text}:{info}"

    await callback_query.message.edit_text(new_text, reply_markup=kb.create_channels_kb(channels, resumeid, userid, price))


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('pay'))
async def process_callback_resume_pay(callback_query: types.CallbackQuery):

    resumeid_userid_price = callback_query.data.replace("pay", "")

    resumeid, userid, price = resumeid_userid_price.split("_")
    price = int(price)*100

    # if code.isdigit():
    #     code = int(code)

    # if code == 1:
    await bot.send_invoice(chat_id=userid, title=f"Оплата резюме №{resumeid}", \
        description="После оплаты, ваше резюме появится в каналах", \
        payload=f"resume_pay__{resumeid}", provider_token=YOUTOKEN, currency="RUB", start_parameter="event_bot", \
        prices=[{"label": "Руб", "amount": price}])

    # elif code == 2:
    #     pass


@dp.pre_checkout_query_handler()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def process_pay(message: types.Message):

    payload, resumeid = message.successful_payment.invoice_payload.split("__")

    if resumeid.isdigit():
        resumeid = int(resumeid)

    if payload == "resume_pay":
        BotDB.update_published(resumeid)

        text = BotDB.get_resume_by_id(resumeid)[2]

        await bot.send_message(CHANNEL, text)
