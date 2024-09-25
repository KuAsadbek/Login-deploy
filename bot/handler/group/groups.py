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
    await message.delete()

@group_router.callback_query(F.data=='send_excel')
async def send(call:CallbackQuery):
    if db.read(USERMOD):
        Students = db.read(USERMOD)
        Teacher = db.read(TEACHER_MOD)
        Parents = db.read(PARENTS_MOD)

        file_path = create_excel_with_data(Students=Students,Teacher=Teacher,Parents=Parents,file_name= "user_data.xlsx")

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
    save_data = db.read(
        SAVE_DATA,
        where_clause=f'telegram_id = {user_id}'
    )
    teacher = db.read(
        TEACHER_MOD,
        where_clause=f'telegram_id = {user_id}'
    )
    parent = db.read(
        PARENTS_MOD,
        where_clause=f'telegram_id = {user_id}'
    )
    who = save_data[0][2]
    school = save_data[0][3]
    city = save_data[0][4]
    class_name = save_data[0][5]
    teacher_name = save_data[0][6]
    student_name = save_data[0][7]
    student_number = save_data[0][8]
    teacher_number = save_data[0][9]
    lg = save_data[0][10]
    py = True

    common_data = {
        "telegram_id": user_id,
        "school":school,
        "city": city,
        "class_name":class_name,
        'payment':py,
        "language": lg
    }

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
        if who == 'Tch_a':
            teacher_id = teacher[0][0]
            tch_name = teacher[0][2]
            tch_num = teacher[0][6]
            common_data["teacher_name_id"] = teacher_id
            common_data["teacher_name1"] = tch_name
            common_data["teacher_number"] = tch_num
            common_data["student_name"] = student_name
            common_data["student_number"] = teacher_number
            db.insert(USERMOD, **common_data)
        elif who == 'Pr_a':
            parent_id = parent[0][0]
            pr_name = parent[0][2]
            pr_num = parent[0][6]
            common_data["parents_id"] = parent_id
            common_data["teacher_name1"] = pr_name
            common_data["teacher_number"] = pr_num
            common_data["student_name"] = student_name
            common_data["student_number"] = teacher_number
            db.insert(USERMOD, **common_data)
        elif who == 'std':
            common_data["teacher_number"] = teacher_number
            common_data["student_name"] = student_name
            common_data["teacher_name"] = teacher_name
            common_data["student_number"] = student_number
            db.insert(USERMOD, **common_data)
        elif who == 'tch':
            common_data["teacher_number"] = teacher_number
            common_data["teacher_name"] = teacher_name
            db.insert(TEACHER_MOD, **common_data)
        else:
            common_data["teacher_number"] = teacher_number
            common_data["teacher_name"] = teacher_name
            db.insert(PARENTS_MOD, **common_data)

        await call.message.bot.send_message(
            chat_id=user_id,
            text=f'{text}\n\n{r}'
        )
    else:           
        await call.message.bot.send_message(
            chat_id=user_id,
            text=f'{u}'
        )
    db.delete(SAVE_DATA,where_clause=f'telegram_id = {user_id}')
    await call.message.edit_reply_markup(reply_markup=None)
















# @group_router.callback_query(lambda c: c.data and c.data.startswith('Tr_') or c.data.startswith('Fr_'))
# async def check(call:CallbackQuery):
#     str_text, index = call.data.split('_')
#     user_id = int(index)
#     save_data = db.read(SAVE_DATA,where_clause=f'telegram_id = {user_id}')
#     teacher = db.read(
#         TEACHER_MOD,
#         where_clause=f'telegram_id = {user_id}'
#     )
#     parent = db.read(
#         PARENTS_MOD,
#         where_clause=f'telegram_id = {user_id}'
#     )
#     user = save_data[0][1]
#     who = save_data[0][2]
#     title = save_data[0][3]
#     muc = save_data[0][4]
#     school = save_data[0][5]
#     city = save_data[0][6]
#     num = save_data[0][7]
#     lg = save_data[0][8]
#     un_id = save_data[0][9]
#     py = True

#     if lg == 'ru':
#             ru = 2
#             r = 'Чек прошел проверку!!!'
#             u = 'Чек не прошел проверку!!!\n Пройдите регистрацию заново -> /start'
#     else:
#         ru = 1
#         r = 'Chek tasdiqlandi!!!'
#         u = 'Tekshiruv tasdiqlanmadi!!!\nQayta ro\'yxatdan o\'ting -> /start'
    
#     main = db.read(DESCR,where_clause=f'title_id = 1')
#     text = main[0][ru]

#     if str_text == 'Tr':
#         if who == 'Tch_a':
#             teacher_id = teacher[0][0]
#             db.insert(
#                 USERMOD,
#                 teacher_id = teacher_id,
#                 telegram_id = un_id,
#                 full_name = title,
#                 school = school,
#                 city = city,
#                 number = num,
#                 payment = py,
#                 language = lg
#             )
#             await call.message.bot.send_message(
#                 chat_id=user_id,
#                 text=f'{text}\n\n{r}'
#             )
#         elif who == 'Pr_a':
#             parent_id = parent[0][0]
#             db.insert(
#                 USERMOD,
#                 parents_id = parent_id,
#                 telegram_id = un_id,
#                 full_name = title,
#                 school = school,
#                 city = city,
#                 number = num,
#                 payment = py,
#                 language = lg
#             )
#             await call.message.bot.send_message(
#                 chat_id=user_id,
#                 text=f'{text}\n\n{r}'
#             )
#         elif who == 'std':
#             db.insert(
#                 USERMOD,
#                 telegram_id = user,
#                 full_name = title,
#                 school = school,
#                 city = city,
#                 number = num,
#                 payment = py,
#                 language = lg
#             )
#             await call.message.bot.send_message(
#                 chat_id=user_id,
#                 text=f'{text}\n\n{r}'
#             )
#         elif who == 'tch':
#             db.insert(
#                 TEACHER_MOD,
#                 telegram_id = user,
#                 full_name = title,
#                 school = school,
#                 class_name = muc,
#                 city = city,
#                 number = num,
#                 payment = py,
#                 language = lg
#             )
#             await call.message.bot.send_message(
#                 chat_id=user_id,
#                 text=f'{text}\n\n{r}'
#             )
#         elif who == 'pr':
#             db.insert(
#                 PARENTS_MOD,
#                 telegram_id = user,
#                 full_name = title,
#                 school = school,
#                 class_name = muc,
#                 city = city,
#                 number = num,
#                 payment = py,
#                 language = lg
#             )
#             await call.message.bot.send_message(
#                 chat_id=user_id,
#                 text=f'{text}\n\n{r}'
#             )
#         db.delete(SAVE_DATA,where_clause=f'telegram_id = {user_id}')        
#     elif str_text == 'Fr':           

#         db.delete(SAVE_DATA,where_clause=f'telegram_id = {user_id}')

#         await call.message.bot.send_message(
#             chat_id=user_id,
#             text=f'{u}'
#         )
#     await call.message.edit_reply_markup(reply_markup=None)