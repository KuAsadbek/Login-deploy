import random
from aiogram import Router,F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import CommandStart
from aiogram.types import Message,CallbackQuery,KeyboardButton,ReplyKeyboardMarkup,ContentType,InlineKeyboardButton,ReplyKeyboardRemove
from set_app.settings import BUT,DESCR,USERMOD,CHANEL_ID,SAVE_DATA,TEACHER_MOD,PARENTS_MOD

from ...utils.db.class_db import SQLiteCRUD
from ...states.state_user.state_us import StateUser
from ...filters.chat_type import chat_type_filter,MediaFilter,generate_unique_code,get_text_and_language,is_uzbek_number,get_text_and_language_end
from ...keyboards.inline.button import CreateInline,CreateBut

user_private_router = Router()
user_private_router.message.filter(chat_type_filter(['private']))

db = SQLiteCRUD('./db.sqlite3')

@user_private_router.message(CommandStart())
async def private_start(message:Message,state:FSMContext):
    user_id = message.from_user.id

    teacher = db.read(TEACHER_MOD,where_clause=f'telegram_id = {user_id}')
    parent = db.read(PARENTS_MOD,where_clause=f'telegram_id = {user_id}')
    save_data = db.read(SAVE_DATA,where_clause=f'telegram_id = {user_id}')
    student = db.read(USERMOD,where_clause=f'telegram_id = {user_id}')

    if teacher is not None:
        text,lg = get_text_and_language(teacher,8)
        await state.update_data({'LG':lg,'tch_id':user_id,'who':'Tch_a'})
        await message.answer_photo(photo='https://d.newsweek.com/en/full/837076/mcdhapo-ec961.jpg',caption=f'{text}',reply_markup=CreateInline(add_std='add students',code='Code',adm='Admin'))

    elif parent is not None:
        text,lg = get_text_and_language(parent,8)
        await state.update_data({'LG':lg,'pr_id':user_id,'who':'Pr_a'})
        await message.answer_photo(photo='https://d.newsweek.com/en/full/837076/mcdhapo-ec961.jpg',caption=f'{text}',reply_markup=CreateInline(add_std='add student',code='Code',adm='Admin'))

    elif student is not None:
        text,lg = get_text_and_language(student,11)
        await state.update_data({'LG':lg,'std_id':user_id,'who':'std'})
        await message.answer_photo(photo='https://d.newsweek.com/en/full/837076/mcdhapo-ec961.jpg',caption=f'{text}',reply_markup=CreateInline(code='Code',adm='Admin'))

    elif save_data is not None:
        await message.answer('Ваша заявка уже отправлена')

    else:
        text = get_text_and_language('start',1)
        await message.answer_photo(photo='https://d.newsweek.com/en/full/837076/mcdhapo-ec961.jpg',caption=f'{text}',reply_markup=CreateInline(ru='Ru',uz='Uz'))
        await state.set_state(StateUser.ru)
        await message.delete()

@user_private_router.callback_query(F.data == 'adm')
async def adm(call:CallbackQuery,state:FSMContext):
    data = await state.get_data()
    lg = data.get('LG')
    text = {
        'uz':{
            'text':'Admin Telefon raqami -> 941131317'
        },
        'ru':{
            'text':'Admin номер телефон -> 941131317'
        }
    }
    await call.message.answer(f'Username: <a href="https://t.me/Hogwart_admin">Admin</a>\n{text[lg]['text']}')

@user_private_router.callback_query(F.data == 'code')
async def cod(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lg = data.get('LG')
    user_id = call.from_user.id
    who = data.get('who')

    ru = 2 if lg == 'ru' else 1

    main = db.read(DESCR, where_clause=f'title_id = 14')[0][ru]
    messages = {
        'ru': {
            'your_code': 'Студент(ы) с кодом:\n\n{students}',
            'no_students': 'Студентов нет',
        },
        'uz': {
            'your_code': 'O‘quvchi(lar) kodi:\n\n{students}',
            'no_students': 'studentlar mavjud emas',
        }
    }
    lang = messages.get(lg, messages['ru'])

    # Запрашиваем всех студентов в зависимости от роли
    students = []
    if who == 'Tch_a':
        teacher = db.read(TEACHER_MOD, where_clause=f'telegram_id = {user_id}')
        if teacher:
            tch_id = teacher[0][0]
            students = db.read(USERMOD, where_clause=f'teacher_name_id = {tch_id}')
    elif who == 'Pr_a':
        parent = db.read(PARENTS_MOD, where_clause=f'telegram_id = {user_id}')
        if parent:
            parent_id = parent[0][0]
            students = db.read(USERMOD, where_clause=f'parents_id = {parent_id}')
    else:
        user = db.read(USERMOD, where_clause=f'telegram_id = {user_id}')
        if user:
            students.append(user[0])

    # Если студентов нет, выводим сообщение
    if not students:
        await call.message.answer(lang['no_students'])
        await call.message.delete()
        return

    # Разделяем студентов на тех, у кого есть код, и тех, у кого кода нет
    students_with_code = [student for student in students if student[1] != 'null']
    students_without_code = [student for student in students if student[1] == 'null']

    # Форматируем строки для студентов с кодом и без
    student_codes = "\n".join([
        f"{'Имя:' if lg == 'ru' else 'Ismi:'} {student[3]} -> code {student[1]}" 
        for student in students_with_code
    ])
    
    student_codes_not = "\n".join([
        f"{'Имя:' if lg == 'ru' else 'Ismi:'} {student[3]}" 
        for student in students_without_code
    ])

    # Формируем итоговое сообщение
    final_message = ""
    if students_with_code:
        final_message += f"{"Оплачено" if lg == 'ru' else 'Tolov klingan'}:\n\n{student_codes}\n\n"
    if students_without_code:
        final_message += f"{"Не оплачено" if lg == 'ru' else 'Tolov klinmagan'}:\n\n{student_codes_not}\n\n"

    final_message += main

    # Отправляем сообщение пользователю
    await call.message.answer(lang['your_code'].format(students=final_message))
    
    # Удаляем старое сообщение
    await call.message.delete()

@user_private_router.callback_query((F.data=='Оставить комментарий') | (F.data == 'Izoh koldiring'))
async def mes(call:CallbackQuery,state:FSMContext):
    data = await state.get_data()
    lg = data.get("LG")
    if lg == 'ru':
        n = 'Ваш комментарий'
    elif lg == 'uz':
        n = 'Izoh'
    await call.message.answer(n)
    await state.set_state(StateUser.comment)
    await call.message.delete()

@user_private_router.message(StateUser.comment,F.text)
async def mes1(message:Message,state:FSMContext):
    data = await state.get_data()
    lg = data.get("LG")
    user_id = message.from_user.id
    comment = message.text
    url = f'https://t.me/{user_id}' 
    name = message.from_user.full_name or message.from_user.first_name
    if lg == 'ru':
        n = 'спасибо за коммент'
    elif lg == 'uz':
        n = 'Izoh kildirganigiz uchun harmat'
    await message.bot.send_message(chat_id=CHANEL_ID,text=f'Комментарий от пользователя <a href="{url}"><b>{name}</b></a>:\n{comment}')
    await message.answer(n)

@user_private_router.callback_query(F.data=='back_ru',StateUser.school)
async def cmd_ru(call:CallbackQuery,state:FSMContext):
    data = await state.get_data()
    who = data.get('who')
    user_id = call.from_user.id
    main = db.read(DESCR,where_clause=f'title_id = {1}')
    def get_text_and_language(user_record, lg_index):
        lg = user_record[0][lg_index]
        n = 2 if lg == 'ru' else 1
        return main[0][n], lg
    
    if who in ['Tch_a', 'Pr_a']:
        teacher = db.read(TEACHER_MOD, where_clause=f'telegram_id = {user_id}')
        parent = db.read(PARENTS_MOD, where_clause=f'telegram_id = {user_id}')

        if teacher:
            text, lg = get_text_and_language(teacher, 8)
            await state.update_data({'LG': lg, 'tch_id': user_id, 'who': 'Tch_a'})
            await call.message.answer(f'{text}', reply_markup=CreateInline(add_std='add students'))

        elif parent:
            text, lg = get_text_and_language(parent, 8)
            await state.update_data({'LG': lg, 'pr_id': user_id, 'who': 'Pr_a'})
            await call.message.answer(f'{text}', reply_markup=CreateInline(add_std='add student'))

    else:
        text = main[0][1]
        await call.message.answer(f'{text}',reply_markup=CreateInline(ru='Ru',uz='Uz'))
        await state.set_state(StateUser.ru)
        await call.message.delete()

@user_private_router.callback_query(F.data=='add_std')
async def ste(call:CallbackQuery,state:FSMContext):
    data = await state.get_data()
    lg = data.get('LG')
    n = 2 if lg == 'ru' else 1
    main = db.read(DESCR,where_clause='title_id = 4')
    des = main[0][n]
    await call.message.answer(text=des,reply_markup=CreateBut([p[n] for p in db.read(BUT)],back_ru='Orqaga'))
    await state.set_state(StateUser.school)
    await call.message.delete()

# ru_start
@user_private_router.callback_query(F.data,StateUser.ru)
async def cmd_ru(call:CallbackQuery,state:FSMContext):
    ru = call.data
    n = 2 if ru == 'ru' else 1
    await state.update_data({'LG':ru})
    main = db.read(DESCR,where_clause='title_id = 2')[0][n]
    text = {
        'uz':{
            'tch':'O\'qituvchi',
            'std':'O\'quvchi',
            'pr':'Ota - ona'
        },
        'ru':{
            'tch':'Учитель',
            'std':'Студент',
            'pr':'родители'
        }
    }
    await call.message.answer(main,reply_markup=CreateInline(tch=text[ru]['tch'],std=text[ru]['std'],pr=text[ru]['pr']))
    await state.set_state(StateUser.who)
    await call.message.delete()

@user_private_router.callback_query(F.data,StateUser.who)
async def tch(call:CallbackQuery,state:FSMContext):
    data = await state.get_data()
    who = call.data
    user_id = call.from_user.id
    lg = data.get('LG')
    n = 2 if lg == 'ru' else 1
    main = db.read(DESCR,where_clause='title_id = 3')[0][n]
    await state.update_data({'who':who,'user_id':user_id})
    await call.message.answer(text=main,reply_markup=CreateBut([p[n] for p in db.read(BUT)],back_ru='Orqaga'))
    await state.set_state(StateUser.school)
    await call.message.delete()

@user_private_router.callback_query(F.data,StateUser.school)
async def name(call:CallbackQuery,state:FSMContext):
    data = await state.get_data()
    school = call.data
    lg = data.get("LG")
    n = 2 if lg == 'ru' else 1
    main = db.read(DESCR,where_clause='title_id = 4')[0][n]
    del_cit = await call.message.answer(main)
    await state.update_data({'school':school,'del_cit':del_cit.message_id})
    await state.set_state(StateUser.city)
    await call.message.delete()

@user_private_router.message(F.text,StateUser.city)
async def muc(message:Message,state:FSMContext):
    data = await state.get_data()
    del_cit = data.get("del_cit")
    city = message.text
    lg = data.get("LG")
    n = 2 if lg == 'ru' else 1
    main = db.read(DESCR,where_clause='title_id = 5')[0][n]
    del_muc = await message.answer(main)
    await state.update_data({'city':city,'del_muc':del_muc.message_id})
    await message.bot.delete_message(chat_id=message.chat.id,message_id=del_cit)
    await message.delete()
    await state.set_state(StateUser.muc)
    

@user_private_router.message(F.text,StateUser.muc)
async def name(message:Message,state:FSMContext):
    data = await state.get_data()
    del_muc = data.get('del_muc')
    who = data.get('who')
    muc = message.text
    lg = data.get('LG')
    n = 2 if lg == 'ru' else 1
    ho = 7 if who == 'std' else 11
    if who == 'Tch_a' or who == 'Pr_a':
        main = db.read(DESCR,where_clause='title_id = 12')
        text = main[0][n]
        std_name_del = await message.answer(text=text)
        await state.update_data({'muc':muc,'del_std':std_name_del.message_id})
        await state.set_state(StateUser.student_name)
    else:
        main = db.read(DESCR,where_clause=f'title_id = {ho}')
        text = main[0][n]
        tch_name_del = await message.answer(text=text)
        await state.update_data({'muc':muc,'tch_name_del':tch_name_del.message_id})
        await state.set_state(StateUser.teacher_name)
    await message.bot.delete_message(chat_id=message.chat.id,message_id=del_muc)
    await message.delete()
    

@user_private_router.message(F.text,StateUser.teacher_name)
async def nme(message:Message,state:FSMContext):
    data = await state.get_data()
    tch_name_del = data.get('tch_name_del')
    lg = data.get('LG')
    who = data.get('who')
    teacher_name = message.text
    n = 2 if lg == 'ru' else 1
    if who == 'std':
        main = db.read(DESCR,where_clause='title_id = 6')
        text = main[0][n]
        del_std = await message.answer(text=text)
        await state.update_data({'teacher_name':teacher_name,'del_std':del_std.message_id})
        await state.set_state(StateUser.student_name)
    else:
        n, test = (2, 'Отправить контакт') if lg == 'ru' else (1, 'Kontaktni yuboring')
        contact_button = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(
                        text=test, 
                        request_contact=True
                    )
                ]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        main = db.read(DESCR,where_clause='title_id = 8')[0][n]
        del_all = await message.answer(text=main,reply_markup=contact_button)
        await state.update_data({'teacher_name':teacher_name,'del_TT':del_all.message_id})
        await state.set_state(StateUser.number)
    await message.bot.delete_message(chat_id=message.chat.id,message_id=tch_name_del)
    await message.delete()

@user_private_router.message(F.text,StateUser.student_name)
async def name(message:Message,state:FSMContext):
    data = await state.get_data()
    del_std = data.get('del_std')
    student_name = message.text
    who = data.get('who')
    lg = data.get('LG')
    n, test = (2, 'Отправить контакт') if lg == 'ru' else (1, 'Kontaktni yuboring')
    if who == 'Tch_a' or who == 'Pr_a':
        main = db.read(DESCR,where_clause='title_id = 13')
        text = main[0][n]
        del_Tp = await message.answer(text=text)
        await state.set_state(StateUser.teacher_num)
        await state.update_data({'student_name':student_name,'del_tch_n':del_Tp.message_id})
    else:
        main = db.read(DESCR,where_clause='title_id = 8')
        text = main[0][n]
        contact_button = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(
                        text=test, 
                        request_contact=True
                    )
                ]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        del_TT = await message.answer(text=text,reply_markup=contact_button)
        await state.update_data({'student_name':student_name,'del_TT':del_TT.message_id})
        await state.set_state(StateUser.number)
    await message.bot.delete_message(chat_id=message.chat.id,message_id=del_std)
    await message.delete()


@user_private_router.message(F.contact,StateUser.number)
async def num(message:Message,state:FSMContext):
    data = await state.get_data()
    del_TT = data.get('del_TT')
    num = message.contact.phone_number
    lg = data.get("LG")
    who = data.get('who')
    n = 2 if lg == 'ru' else 1

    texts = {
        "ru": {
            "online_payment": "Оплатить Онляйн",
            "in_person_payment": "Прийти и заплатить",
            "error_text": "Пожалуйста, отправьте узбекский номер, который начинается с +998.",
        },
        "uz": {
            "online_payment": "Onlayn to'lov",
            "in_person_payment": "Borib tolash",
            "error_text": "+998 bilan boshlanadigan o'zbek raqamini yuboring.",
        }
    }

    if who == 'std':
        main = db.read(DESCR,where_clause='title_id = 9')
        text = main[0][n]

        if is_uzbek_number(num):
            del_tch_n = await message.answer(text=text,reply_markup=ReplyKeyboardRemove())
            await state.set_state(StateUser.teacher_num)
        else:
            await message.answer('error')
        await state.update_data({'student_num':num,'del_tch_n':del_tch_n.message_id})
    else:
        await state.update_data({'teacher_num':num})
        
        current_texts = texts[lg]
        bt = current_texts["online_payment"]
        bt2 = current_texts["in_person_payment"]
        error_text = current_texts["error_text"]

        main = db.read(DESCR,where_clause='title_id = 10')
        py = main[0][n]
        
        if is_uzbek_number(num):
            del_dp = await message.answer(py,reply_markup=CreateInline(bt,bt2))
            await state.set_state(StateUser.py)
        else:
            await message.answer(error_text)
        await state.update_data({'student_num':num,'del_dp':del_dp.message_id})
    await message.bot.delete_message(chat_id=message.chat.id,message_id=del_TT)
    await message.delete()
    

@user_private_router.message(F.text | F.contact,StateUser.teacher_num)
async def nur(message:Message,state:FSMContext):
    data = await state.get_data()
    del_tch_n = data.get('del_tch_n')
    lg = data.get('LG')
    
    texts = {
        "ru": {
            "online_payment": "Оплатить Онляйн",
            "in_person_payment": "Прийти и заплатить",
            "error_text": "Пожалуйста, отправьте узбекский номер, который начинается с +998.",
            "n": 2
        },
        "uz": {
            "online_payment": "Onlayn to'lov",
            "in_person_payment": "Borib tolash",
            "error_text": "+998 bilan boshlanadigan o'zbek raqamini yuboring.",
            "n": 1
        }
    }

    current_texts = texts[lg]
    bt = current_texts["online_payment"]
    bt2 = current_texts["in_person_payment"]
    error_text = current_texts["error_text"]
    n = current_texts["n"]

    teacher_num = message.contact.phone_number if message.contact else message.text
        
    if is_uzbek_number(teacher_num):
        main = db.read(DESCR,where_clause='title_id = 10')
        py = main[0][n]
        del_dp = await message.answer(py,reply_markup=CreateInline(bt,bt2))
        await state.update_data({'teacher_num':teacher_num,'del_dp':del_dp.message_id})
        await state.set_state(StateUser.py)
    else:
        # Если номер не из Узбекистана
        await message.answer(error_text)
    await message.bot.delete_message(chat_id=message.chat.id,message_id=del_tch_n)
    await message.delete()

    
@user_private_router.callback_query((F.data == 'Оплатить Онляйн') | (F.data == 'Onlayn to\'lov'), StateUser.py)
async def rech(call:CallbackQuery,state:FSMContext):
    data = await state.get_data()
    del_dp = data.get('del_dp')
    lg = data.get('LG')
    text = {
        'uz':{
            'pay':'Musobaqada qatnashish narxi: 70 000 so\'m',
            'usr':'Atojonov Otajon',
            'card':'Karta nomer: 8600-4904-1188-3994',
            'check':'Check yuborish'
        },
        'ru':{
            'pay':'Стоимость участия в конкурсе: 70 000 сомов',
            'usr':'Atojonov Otajon',
            'card':'Номер карты: 8600-4904-1188-3994',
            'check':'Отправить чек'
        }
    }
    await call.message.answer(text=f"{text[lg]['pay']}\n\nuser: {text[lg]['usr']}\n{text[lg]['card']}",reply_markup=CreateInline(text[lg]['check']))
    await state.set_state(StateUser.look)
    await call.message.bot.delete_message(chat_id=call.message.chat.id,message_id=del_dp)
    await call.message.delete()

@user_private_router.callback_query((F.data == 'Отправить чек') | (F.data == 'Check yuborish'), StateUser.look)
async def py(call:CallbackQuery,state:FSMContext):
    data = await state.get_data()
    lg = data.get("LG")
    test = 'Отправьте чек' if lg == 'ru' else 'Tolov Chekini yuboring'
    del_check = await call.message.answer(test,reply_markup=ReplyKeyboardRemove())
    await state.update_data({'del_check':del_check.message_id})
    await state.set_state(StateUser.py1)
    await call.message.delete()

@user_private_router.message(StateUser.py1,MediaFilter())
async def handle_media(message: Message, state: FSMContext):
    data = await state.get_data()
    del_check = data.get('del_check')
    
    lg = data.get("LG")
    who = data.get('who')
    school = data.get('school')
    city = data.get('city')
    muc = data.get('muc')
    teacher_name = data.get('teacher_name')
    student_name = data.get('student_name')
    student_num = data.get('student_num')
    teacher_num = data.get('teacher_num')
    url = message.from_user.url

    texts = {
        "ru": {
            "ask_file": "Пожалуйста, отправьте Фото или PDF файл.",
            "bt_yes": "Да",
            "bt_no": "Нет",
        },
        "uz": {
            "ask_file": "Iltimos, fotosurat yoki PDF faylini yuboring.",
            "bt_yes": "Ha",
            "bt_no": "Yoq",
        }
    }
    if who == 'std':
        profile_text = (f"{'Ваш профиль' if lg == 'ru' else 'Sizning profilingiz'}\n\n"
                        f"{'Имя учителя' if lg == 'ru' else 'Ustozingiz ismi'}: {teacher_name}\n"
                        f"{'Имя' if lg == 'ru' else 'Ism'}: {student_name}\n"
                        f"{'Школа' if lg == 'ru' else 'Maktab'}: {muc}\n"
                        f"{'Класс' if lg == 'ru' else 'Sinif'}: {school}\n"
                        f"{'Город' if lg == 'ru' else 'Tuman'}: {city}\n"
                        f"{'Номер учителя' if lg == 'ru' else 'Ustozingiz telefon raqami'}: {teacher_num}\n"
                        f"{'Номер' if lg == 'ru' else 'Telefon raqam'}: {student_num}\n"
                        f"{'Правильно ли вы ввели свои данные?' if lg == 'ru' else 'Ma\'lumotlaringgiz to\'g\'ri kiritilganmi ?'}")
    elif who in ['Tch_a','Pr_a']:
        profile_text = (f"{'Профиль вашего ученика' if lg == 'ru' else 'Okuvchini profili'}\n\n"
                        f"{'Имя' if lg == 'ru' else 'Ism'}: {student_name}\n"
                        f"{'Школа' if lg == 'ru' else 'Maktab'}: {muc}\n"
                        f"{'Класс' if lg == 'ru' else 'Sinif'}: {school}\n"
                        f"{'Город' if lg == 'ru' else 'Tuman'}: {city}\n"
                        f"{'Номер' if lg == 'ru' else 'Telefon raqam'}: {teacher_num}\n"
                        f"{'Правильно ли вы ввели свои данные?' if lg == 'ru' else 'Ma\'lumotlaringgiz to\'g\'ri kiritilganmi ?'}")
    else:
        profile_text = (f"{'Ваш профиль' if lg == 'ru' else 'Sizning profilingiz'}\n\n"
                        f"{'Имя' if lg == 'ru' else 'Ism'}: {teacher_name}\n"
                        f"{'Школа' if lg == 'ru' else 'Maktab'}: {muc}\n"
                        f"{'Класс' if lg == 'ru' else 'Sinif'}: {school}\n"
                        f"{'Город' if lg == 'ru' else 'Tuman'}: {city}\n"
                        f"{'Номер' if lg == 'ru' else 'Telefon raqam'}: {teacher_num}\n"
                        f"{'Правильно ли вы ввели свои данные?' if lg == 'ru' else 'Ma\'lumotlaringgiz to\'g\'ri kiritilganmi ?'}")

    current_texts = texts[lg]
    bt = current_texts["bt_yes"]
    bt2 = current_texts["bt_no"]
    ask_file_text = current_texts["ask_file"]

    final_text = f"{profile_text}"

    if message.content_type == ContentType.PHOTO:
        photo_id = message.photo[-1].file_id
        await state.update_data({'photo_id': photo_id, 'url': url, 'n': 1})
        await message.reply(text=final_text, reply_markup=CreateInline(bt, bt2))
        await state.set_state(StateUser.yep1)

    elif message.content_type == ContentType.DOCUMENT:
        if message.document.mime_type == 'application/pdf':
            doc = message.document.file_id
            await state.update_data({'doc': doc, 'url': url, 'n': 2})
            await message.reply(text=final_text, reply_markup=CreateInline(bt, bt2))
            await state.set_state(StateUser.yep1)

    elif message.document.mime_type == 'image/png' or message.document.mime_type == 'image/jpn':
            png_id = message.document.file_id
            await state.update_data({'photo_id': png_id, 'url': url, 'n': 1})  # Обработка как фотографии
            await message.reply(text=final_text, reply_markup=CreateInline(bt, bt2))
            await state.set_state(StateUser.yep1)
    else:
        await message.answer(text=ask_file_text)
    await message.bot.delete_message(chat_id=message.chat.id, message_id=del_check)

@user_private_router.callback_query((F.data=='Да') | (F.data == 'Ha'),StateUser.yep1)
async def yes(call:CallbackQuery,state:FSMContext):
    data = await state.get_data()

    lg = data.get("LG")
    who = data.get('who')
    school = data.get('school')
    city = data.get('city')
    muc = data.get('muc')
    teacher_name = data.get('teacher_name')
    student_name = data.get('student_name')
    student_num = data.get('student_num')
    teacher_num = data.get('teacher_num')
    user_id = call.from_user.id
    url = data.get('url')
    n = data.get('n')

    save_data = db.read(SAVE_DATA,where_clause=f'telegram_id = {user_id} AND student_name = "{student_name}"')

    if save_data:
        unique_suffix = f"{user_id}!{random.randint(1000, 9999)}"  # Добавление user_id и случайного числа
        std_name = f'{student_name}!{unique_suffix}'
    else:
        std_name = f'{student_name}!del'
    
    comm = {
        3:'A',
        4:'B',
        5:'C',
        6:'D',
        7:'E',
    }
    index = int(''.join(filter(str.isdigit, school)))
    code = f"{comm[index]}-100"
    if who in ['Tch_a','Pr_a','std']:
        unique_code = generate_unique_code(code)
    else:
        unique_code = ''

    common_data = {
        "telegram_id": user_id,
        'code':unique_code if unique_code else '',
        "who": who,
        "school": school,
        "city": city,
        "class_name": muc,
        "language": lg,
        "student_name": std_name if std_name else '',
        "teacher_name": teacher_name if teacher_name else '',
        "student_number": student_num if student_num else '',
        "teacher_number": teacher_num if teacher_num else '',
    }

    button = InlineKeyboardBuilder()
    button.add(InlineKeyboardButton(text='Принять',callback_data=f'Tr_{user_id}_{std_name}'))
    button.add(InlineKeyboardButton(text='Отклонить',callback_data=f'Fr_{user_id}_{std_name}'))
    button.adjust(2)

    texts = {
        "ru": {
            "confirmation": "Ваш чек отправлено на проверку!",
            "leave_comment": "Оставить комментарий",
        },
        "uz": {
            "confirmation": "Chekingiz tekshirish uchun yuborildi!",
            "leave_comment": "Izoh koldiring",
        }
    }
    current_texts = texts[lg]

    db.insert(SAVE_DATA, **common_data)

    if n == 1:
        photo_id = data.get("photo_id")
        await call.message.bot.send_photo(chat_id= CHANEL_ID ,
                photo=photo_id,
                caption=f"Чек от пользователя <a href='{url}'><b>{student_name or teacher_name}</b></a>",
                reply_markup=button.as_markup()
        )
    else:
        doc = data.get('doc')
        await call.message.bot.send_document(
            chat_id= CHANEL_ID ,
            document=doc,
            caption=f"PDF файл от пользователя <a href='{url}'><b>{student_name or teacher_name}</b></a>",
            reply_markup=button.as_markup()
        )
    await call.message.answer(current_texts["confirmation"], reply_markup=CreateInline(current_texts["leave_comment"]))
    await call.message.delete()

@user_private_router.callback_query((F.data=='Нет') | (F.data=='Yoq'),StateUser.yep1)
async def net(call:CallbackQuery,state:FSMContext):
    text = get_text_and_language('start',1)
    await call.message.answer_photo(photo='https://d.newsweek.com/en/full/837076/mcdhapo-ec961.jpg',caption=f'{text}',reply_markup=CreateInline(ru='Ru',uz='Uz'))
    await state.set_state(StateUser.ru)
    await call.message.delete()

@user_private_router.callback_query((F.data=='Прийти и заплатить') | (F.data == 'Borib tolash'),StateUser.py)
async def py(call:CallbackQuery,state:FSMContext):
    data = await state.get_data()

    lg = data.get("LG")
    who = data.get('who')
    school = data.get('school')
    city = data.get('city')
    muc = data.get('muc')
    teacher_name = data.get('teacher_name')
    student_name = data.get('student_name')
    student_num = data.get('student_num')
    teacher_num = data.get('teacher_num')

    if lg == 'ru':
        bt = 'Да'
        bt2 = 'Нет'
    else:
        bt = 'Ha'
        bt2 = 'Yo\'q'
    
    if who == 'std':
        profile_text = (f"{'Ваш профиль' if lg == 'ru' else 'Sizning profilingiz'}\n\n"
                        f"{'Имя учителя' if lg == 'ru' else 'Ustozingiz ismi'}: {teacher_name}\n"
                        f"{'Имя' if lg == 'ru' else 'Ism'}: {student_name}\n"
                        f"{'Школа' if lg == 'ru' else 'Maktab'}: {muc}\n"
                        f"{'Класс' if lg == 'ru' else 'Sinif'}: {school}\n"
                        f"{'Город' if lg == 'ru' else 'Tuman'}: {city}\n"
                        f"{'Номер учителя' if lg == 'ru' else 'Ustozingiz telefon raqami'}: {teacher_num}\n"
                        f"{'Номер' if lg == 'ru' else 'Telefon raqam'}: {student_num}\n"
                        f"{'Правильно ли вы ввели свои данные?' if lg == 'ru' else 'Ma\'lumotlaringgiz to\'g\'ri kiritilganmi ?'}")
    elif who in ['Tch_a','Pr_a']:
        profile_text = (f"{'Профиль вашего ученика' if lg == 'ru' else 'Okuvchini profili'}\n\n"
                        f"{'Имя' if lg == 'ru' else 'Ism'}: {student_name}\n"
                        f"{'Школа' if lg == 'ru' else 'Maktab'}: {muc}\n"
                        f"{'Класс' if lg == 'ru' else 'Sinif'}: {school}\n"
                        f"{'Город' if lg == 'ru' else 'Tuman'}: {city}\n"
                        f"{'Номер' if lg == 'ru' else 'Telefon raqam'}: {teacher_num}\n"
                        f"{'Правильно ли вы ввели свои данные?' if lg == 'ru' else 'Ma\'lumotlaringgiz to\'g\'ri kiritilganmi ?'}")
    else:
        profile_text = (f"{'Ваш профиль' if lg == 'ru' else 'Sizning profilingiz'}\n\n"
                        f"{'Имя' if lg == 'ru' else 'Ism'}: {teacher_name}\n"
                        f"{'Школа' if lg == 'ru' else 'Maktab'}: {muc}\n"
                        f"{'Класс' if lg == 'ru' else 'Sinif'}: {school}\n"
                        f"{'Город' if lg == 'ru' else 'Tuman'}: {city}\n"
                        f"{'Номер' if lg == 'ru' else 'Telefon raqam'}: {teacher_num}\n"
                        f"{'Правильно ли вы ввели свои данные?' if lg == 'ru' else 'Ma\'lumotlaringgiz to\'g\'ri kiritilganmi ?'}")

    await call.message.answer(text=profile_text,reply_markup=CreateInline(yees=bt,neet=bt2))
    await state.set_state(StateUser.yep)
    await call.message.delete()
# ru_end
@user_private_router.callback_query(F.data=='yees',StateUser.yep)
async def tes(call:CallbackQuery,state:FSMContext):
    data = await state.get_data()

    lg = data.get("LG")
    who = data.get('who')
    school = data.get('school')
    city = data.get('city')
    muc = data.get('muc')
    teacher_name = data.get('teacher_name')
    student_name = data.get('student_name')
    student_num = data.get('student_num')
    teacher_num = data.get('teacher_num')
    user_id = call.from_user.id

    common_data = {
        "telegram_id": user_id,
        "school": school,
        "class_name": muc,
        "city": city,
        "payment": False,  # Платеж не выполнен
        "language": lg
    }
    unique_code = 'null'

    if who == 'std':
        common_data.update({
            "student_name": student_name,
            'code':unique_code,
            "teacher_name1": teacher_name,
            "teacher_number": teacher_num,
            "student_number": student_num
        })
        db.insert(USERMOD, **common_data)
    elif who == 'Tch_a':
        teacher = db.read(TEACHER_MOD, where_clause=f'telegram_id = {user_id}')
        if teacher:
            common_data.update({
                "teacher_name_id": teacher[0][0],
                'code':unique_code,
                "teacher_name1": teacher[0][2],
                "teacher_number": teacher[0][6],
                "student_name": student_name,
                "student_number": teacher_num
            })
            db.insert(USERMOD, **common_data)
    elif who == 'Pr_a':
        parent = db.read(PARENTS_MOD, where_clause=f'telegram_id = {user_id}')
        if parent:
            common_data.update({
                "parents_id": parent[0][0],
                'code':unique_code,
                "teacher_name1": parent[0][2],
                "teacher_number": parent[0][6],
                "student_name": student_name,
                "student_number": teacher_num
            })
            db.insert(USERMOD, **common_data)
    elif who == 'tch':
        common_data.update({
            "teacher_name": teacher_name,
            "teacher_number": teacher_num
        })
        db.insert(TEACHER_MOD, **common_data)
    elif who == 'pr':
        common_data.update({
            "parent_name": teacher_name,
            "parent_number": teacher_num
        })
        db.insert(PARENTS_MOD, **common_data)
    
    teacher = db.read(TEACHER_MOD, where_clause=f'telegram_id = {user_id}')
    parent = db.read(PARENTS_MOD, where_clause=f'telegram_id = {user_id}')
    student = db.read(USERMOD,where_clause=f'telegram_id = {user_id}')
    if teacher is not None:
        text,lg = get_text_and_language_end(teacher,8)
        await state.update_data({'LG':lg,'tch_id':user_id,'who':'Tch_a'})
        await call.message.answer_photo(photo='https://d.newsweek.com/en/full/837076/mcdhapo-ec961.jpg',caption=f'{text}',reply_markup=CreateInline(add_std='add students',code='Code',adm='Admin'))

    elif parent is not None:
        text,lg = get_text_and_language_end(parent,8)
        await state.update_data({'LG':lg,'pr_id':user_id,'who':'Pr_a'})
        await call.message.answer_photo(photo='https://d.newsweek.com/en/full/837076/mcdhapo-ec961.jpg',caption=f'{text}',reply_markup=CreateInline(add_std='add student',code='Code',adm='Admin'))

    elif student is not None:
        text,lg = get_text_and_language_end(student,7)
        await state.update_data({'LG':lg,'std_id':user_id,'who':'std'})
        await call.message.answer_photo(photo='https://d.newsweek.com/en/full/837076/mcdhapo-ec961.jpg',caption=f'{text}',reply_markup=CreateInline(code='Code',adm='Admin'))
    await call.message.delete()

@user_private_router.callback_query(F.data=='neet',StateUser.yep)
async def net(call:CallbackQuery,state:FSMContext):
    text = get_text_and_language('start',1)
    await call.message.answer_photo(photo='https://d.newsweek.com/en/full/837076/mcdhapo-ec961.jpg',caption=f'{text}',reply_markup=CreateInline(ru='Ru',uz='Uz'))
    await state.set_state(StateUser.ru)
    await call.message.delete()