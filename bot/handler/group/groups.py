import os
from aiogram import Router,F
from aiogram.filters import CommandStart
from aiogram.types import Message,CallbackQuery,FSInputFile

from set_app.settings import DESCR,USERMOD,SAVE_DATA,TEACHER_MOD,PARENTS_MOD

from ...utils.db.class_db import SQLiteCRUD
from ...filters.chat_type import chat_type_filter,create_excel_with_data
from ...keyboards.inline.button import CreateInline

group_router = Router()
group_router.message.filter(chat_type_filter(['supergroup']))

db = SQLiteCRUD('./db.sqlite3')

@group_router.message(CommandStart())
async def one_cmd(message:Message):
    await message.answer(f'Hi bro you need excel file?',reply_markup=CreateInline('send_excel'))

@group_router.callback_query(F.data=='send_excel')
async def send(call:CallbackQuery):
    if db.read(USERMOD):
        all_users_data = db.read(USERMOD)
        true_users_data = db.read(USERMOD,where_clause='payment = 1')
        false_users_data = db.read(USERMOD,where_clause='payment = 0')
        # Создание файла Excel
        file_path = create_excel_with_data(all_users_data, true_users_data, false_users_data, "user_data.xlsx")

        # Проверка на существование файла
        if file_path and os.path.exists(file_path):
            # Отправка файла
            document = FSInputFile(file_path)
            await call.message.answer_document(document=document, caption='user_data.xlsx')
            os.remove(file_path)
            await call.message.edit_reply_markup(reply_markup=None)
        else:
            await call.message.reply("Произошла ошибка при создании файла.")
    else:
        await call.message.reply("Нет данных.")

@group_router.callback_query(lambda c: c.data and c.data.startswith('Tr_') or c.data.startswith('Fr_'))
async def check(call:CallbackQuery):
    str_text, index = call.data.split('_')
    user_id = int(index)
    save_data = db.read(SAVE_DATA,where_clause=f'telegram_id = {user_id}')
    
    user = save_data[0][1]
    who = save_data[0][2]
    title = save_data[0][3]
    muc = save_data[0][4]
    school = save_data[0][5]
    city = save_data[0][6]
    num = save_data[0][7]
    lg = save_data[0][8]
    py = True

    if lg == 'ru':
            ru = 2
            r = 'Чек прошел проверку!!!'
            u = 'Чек не прошел проверку!!!\n Пройдите регистрацию заново -> /start'
    else:
        ru = 1
        r = 'Chek tasdiqlandi!!!'
        u = 'Tekshiruv tasdiqlanmadi!!!\nQayta ro\'yxatdan o\'ting -> /start'
    
    main = db.read(DESCR,where_clause=f'title_id = 1')
    text = main[0][ru]

    if str_text == 'Tr':
        if who == 'std':
            db.insert(
                USERMOD,
                telegram_id = user,
                full_name = title,
                school = school,
                city = city,
                number = num,
                payment = py,
                language = lg
            )
            db.delete(SAVE_DATA,where_clause=f'telegram_id = {user_id}')        
            await call.message.bot.send_message(
                chat_id=user_id,
                text=f'{text}\n\n{r}'
            )
        elif who == 'tch':
            db.insert(
                TEACHER_MOD,
                telegram_id = user,
                full_name = title,
                school = school,
                class_name = muc,
                city = city,
                number = num,
                payment = py,
                language = lg
            )
            db.delete(SAVE_DATA,where_clause=f'telegram_id = {user_id}')        
            await call.message.bot.send_message(
                chat_id=user_id,
                text=f'{text}\n\n{r}'
            )
        elif who == 'pr':
            db.insert(
                PARENTS_MOD,
                telegram_id = user,
                full_name = title,
                school = school,
                class_name = muc,
                city = city,
                number = num,
                payment = py,
                language = lg
            )
            db.delete(SAVE_DATA,where_clause=f'telegram_id = {user_id}')        
            await call.message.bot.send_message(
                chat_id=user_id,
                text=f'{text}\n\n{r}'
            )
    elif str_text == 'Fr':           

        db.delete(SAVE_DATA,where_clause=f'telegram_id = {user_id}')

        await call.message.bot.send_message(
            chat_id=user_id,
            text=f'{u}'
        )
    await call.message.edit_reply_markup(reply_markup=None)