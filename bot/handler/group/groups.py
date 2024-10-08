import os
from aiogram import Router,F
from aiogram.filters import CommandStart
from aiogram.types import Message,CallbackQuery,FSInputFile
from aiogram.fsm.context import FSMContext

from set_app.settings import DESCR,USERMOD,SAVE_DATA,TEACHER_MOD,PARENTS_MOD

from ...utils.db.class_db import SQLiteCRUD
from ...filters.chat_type import chat_type_filter,create_excel_with_data,get_text_and_language
from ...keyboards.inline.button import CreateInline
from ...states.state_user.state_us import StateUser

group_router = Router()
group_router.message.filter(chat_type_filter(['supergroup']))

db = SQLiteCRUD('./db.sqlite3')

async def send_photo_and_update_state(call, user_id, lg, who, code, main, success_message, reply_markup):
    """Функция для отправки фото и обновления состояния"""
    n = 1
    if who in ['tch','pr']:
        n = 0
    if n:
        await call.message.bot.send_photo(
            chat_id=user_id,
            photo='https://d.newsweek.com/en/full/837076/mcdhapo-ec961.jpg',
            caption=f'{main}\n\n{success_message}\n{f"code: {code}" if code else ""}',
            reply_markup=reply_markup
        )
    else:
        await call.message.bot.send_photo(
            chat_id=user_id,
            photo='https://d.newsweek.com/en/full/837076/mcdhapo-ec961.jpg',
            caption=f'{main}\n\n{success_message}',
            reply_markup=reply_markup
        )
    await call.message.delete()

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
async def check(call:CallbackQuery,state:FSMContext):
    str_text, index,two_id = call.data.split('_')
    user_id = int(index)
    save_data = db.read(SAVE_DATA,where_clause=f'telegram_id = {user_id} AND student_name = "{two_id}"')

    if not save_data:
        # Если нет данных, выход из функции
        await call.message.answer("Данные не найдены.")
        return
    
    teacher = db.read(TEACHER_MOD,where_clause=f'telegram_id = {user_id}')
    parent = db.read(PARENTS_MOD,where_clause=f'telegram_id = {user_id}')

    who = save_data[0][2]
    school = save_data[0][3]
    city = save_data[0][4]
    class_name = save_data[0][5]
    teacher_name = save_data[0][6]
    name = save_data[0][7].split("!")[0]
    student_name = name
    student_number = save_data[0][8]
    teacher_number = save_data[0][9]
    lg = save_data[0][10]
    code = save_data[0][11]
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
        success_message = 'Чек прошел проверку!!!'
        fail_message = 'Чек не прошел проверку!!!\n Пройдите регистрацию заново -> /start'
        lang_index = 2
    else:
        success_message = 'Chek tasdiqlandi!!!'
        fail_message = 'Tekshiruv tasdiqlanmadi!!!\nQayta ro\'yxatdan o\'ting -> /start'
        lang_index = 1
    
    main = db.read(DESCR,where_clause=f'title_id = 1')[0][lang_index]

    if str_text == 'Tr':
        if who == 'Tch_a':
            teacher_id, tch_name, tch_num = teacher[0][0], teacher[0][2], teacher[0][6]
            common_data.update({
                "teacher_name_id": teacher_id,
                'code':code,
                "teacher_name1": tch_name,
                "teacher_number": tch_num,
                "student_name": student_name,
                "student_number": teacher_number
            })
        elif who == 'Pr_a':
            parent_id, pr_name, pr_num = parent[0][0], parent[0][2], parent[0][6]
            common_data.update({
                "parents_id": parent_id,
                'code':code,
                "teacher_name1": pr_name,
                "teacher_number": pr_num,
                "student_name": student_name,
                "student_number": teacher_number
            })
        elif who == 'std':
            common_data.update({
                "teacher_number": teacher_number,
                "student_name": student_name,
                'code':code,
                "teacher_name1": teacher_name,
                "student_number": student_number
            })
        elif who == 'tch':
            common_data["teacher_number"] = teacher_number
            common_data["teacher_name"] = teacher_name
            db.insert(TEACHER_MOD, **common_data)
        else:
            common_data.update({
                "parent_number": teacher_number,
                "parent_name": teacher_name
            })

        db.insert(USERMOD if who in ['std', 'Tch_a', 'Pr_a'] else (TEACHER_MOD if who == 'tch' else PARENTS_MOD), **common_data)

        await state.update_data({'LG':lg,f'{who}_id':user_id,'who':who})
        await send_photo_and_update_state(call, user_id, lg, who, code, main, success_message, CreateInline(add_std='add student', code='Code', adm='Admin'))

    else:
        text = get_text_and_language('start',1)
        await call.message.bot.send_photo(chat_id=user_id,photo='https://d.newsweek.com/en/full/837076/mcdhapo-ec961.jpg',caption=f'{text} \n\n{fail_message}')
    db.delete(SAVE_DATA,where_clause=f'telegram_id = {user_id} AND student_name = "{two_id}"')
    await call.message.edit_reply_markup(reply_markup=None)
