from aiogram.types import \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

# import channels

# cancel

cancel_btn = KeyboardButton("cancel")
cancel_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(cancel_btn)

inline_kb_empty = InlineKeyboardMarkup()
kb_empty = ReplyKeyboardMarkup()

# start

button1 = KeyboardButton("Разместить вакансию")
button2 = KeyboardButton("Разместить резюме")
button3 = KeyboardButton("Разместить рекламу")
right_keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True).add(button1).row(button3, button2)

# start admin

button4 = KeyboardButton("Отпрвавить сообщение подписчикам")
button5 = KeyboardButton("Список пользователей")
button6 = KeyboardButton("Новые резюме")
button7 = KeyboardButton("Неопубликованные резюме")
right_admin_keyboard = ReplyKeyboardMarkup(row_width=2, 
                                           resize_keyboard=True).add(button1, button3).row(button2, button4).\
                                           row(button5, button6),row(button7)

# approve

def create_approve_kb(resume_id: int, user_id: int):
    inline_btn_approve1 = InlineKeyboardButton("Поддтвердить", callback_data=f"approve{resume_id}_{user_id}_1")
    inline_btn_approve2 = InlineKeyboardButton("Отклонить", callback_data=f"approve{resume_id}_{user_id}_2")
    inline_kb_approve = InlineKeyboardMarkup().add(inline_btn_approve1, inline_btn_approve2)
    return inline_kb_approve

# coose channel

def create_channels_kb(channels: dict, resume_id: int = None, user_id: int = None,
                       price: int = None, publish_channels: str = None):
    inline_kb_channels = InlineKeyboardMarkup()
    for i in channels:
        for j in channels[i]:
            inline_btn_i = InlineKeyboardButton(f"{j[0]}", callback_data=f"channels_{j[0]}")
            inline_kb_channels.row(inline_btn_i)

    if price is not None:
        inline_kb_channels.row(InlineKeyboardButton(f"Оплатить {price}р", 
                        callback_data=f"pay{resume_id}_{user_id}_{price}_{publish_channels}"))

    return inline_kb_channels

# pay

def create_pay_kb(resume_id: int, user_id: int):
    inline_btn_pay1 = InlineKeyboardButton("Оплатить", callback_data=f"pay{resume_id}_{user_id}_1")
    inline_btn_pay2 = InlineKeyboardButton("Отменить", callback_data=f"pay{resume_id}_{user_id}_2")
    inline_kb_pay = InlineKeyboardMarkup().add(inline_btn_pay1, inline_btn_pay2)
    return inline_kb_pay

# send from admin / as - admin send

inline_btn_as1 = InlineKeyboardButton("Отправить", callback_data="asend1")
inline_btn_as2 = InlineKeyboardButton("Отмена", callback_data="asend2")
inline_kb_as = InlineKeyboardMarkup().add(inline_btn_as1, inline_btn_as2)

# rp - resume place / rs - resume send

inline_btn_rp1 = InlineKeyboardButton("Удалёнка", callback_data="place1")
inline_btn_rp2 = InlineKeyboardButton("Москва", callback_data="place2")
inline_btn_rp3 = InlineKeyboardButton("Санкт-Петербург", callback_data="place3")
inline_kb_rp = InlineKeyboardMarkup().add(inline_btn_rp1, inline_btn_rp2, inline_btn_rp3)

inline_btn_resume = InlineKeyboardButton("Отправить свой готовый текст на модерацию", callback_data="resume")
inline_kb_resume = InlineKeyboardMarkup().add(inline_btn_resume)

inline_btn_rs1 = InlineKeyboardButton("Отправить на модерацию", callback_data="end1")
inline_btn_rs2 = InlineKeyboardButton("Отмена", callback_data="end2")
inline_kb_rs = InlineKeyboardMarkup().add(inline_btn_rs1, inline_btn_rs2)

# wp - work place / ws - work send

inline_btn_wp1 = InlineKeyboardButton("Удалёнка", callback_data="wplace1")
inline_btn_wp2 = InlineKeyboardButton("Москва", callback_data="wplace2")
inline_btn_wp3 = InlineKeyboardButton("Санкт-Петербург", callback_data="wplace3")
inline_kb_wp = InlineKeyboardMarkup().add(inline_btn_wp1, inline_btn_wp2, inline_btn_wp3)

inline_btn_work = InlineKeyboardButton("Отправить свой готовый текст на модерацию", callback_data="work")
inline_kb_work = InlineKeyboardMarkup().add(inline_btn_work)

inline_btn_ws1 = InlineKeyboardButton("Отправить", callback_data="wend1")
inline_btn_ws2 = InlineKeyboardButton("Отмена", callback_data="wend2")
inline_kb_ws = InlineKeyboardMarkup().add(inline_btn_ws1, inline_btn_ws2)
