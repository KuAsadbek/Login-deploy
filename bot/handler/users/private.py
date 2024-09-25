import random
from aiogram import Router,F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import CommandStart
from aiogram.types import Message,CallbackQuery,KeyboardButton,ReplyKeyboardMarkup,ContentType,InlineKeyboardButton
from set_app.settings import BUT,DESCR,USERMOD,CHANEL_ID,SAVE_DATA,TEACHER_MOD,PARENTS_MOD

from ...utils.db.class_db import SQLiteCRUD
from ...states.state_user.state_us import StateUser
from ...filters.chat_type import chat_type_filter,MediaFilter
from ...keyboards.inline.button import CreateInline,CreateBut

user_private_router = Router()
user_private_router.message.filter(chat_type_filter(['private']))

db = SQLiteCRUD('./db.sqlite3')

@user_private_router.message(CommandStart())
async def private_start(message:Message,state:FSMContext):
    user_id = message.from_user.id

    main = db.read(DESCR,where_clause=f'title_id = 1')
    teacher = db.read(TEACHER_MOD,where_clause=f'telegram_id = {user_id}')
    parent = db.read(PARENTS_MOD,where_clause=f'telegram_id = {user_id}')
    save_data = db.read(SAVE_DATA,where_clause=f'telegram_id = {user_id}')
    student = db.read(USERMOD,where_clause=f'telegram_id = {user_id}')

    def get_text_and_language(user_record, lg_index):
        lg = user_record[0][lg_index]
        n = 2 if lg == 'ru' else 1
        return main[0][n], lg

    if teacher is not None:
        text,lg = get_text_and_language(teacher,8)
        await state.update_data({'LG':lg,'tch_id':user_id,'who':'Tch_a'})
        await message.answer(f'{text}',reply_markup=CreateInline(add_std='add students'))

    elif parent is not None:
        text,lg = get_text_and_language(parent,8)
        await state.update_data({'LG':lg,'pr_id':user_id,'who':'Pr_a'})
        await message.answer(f'{text}',reply_markup=CreateInline(add_std='add student'))

    elif student is not None:
        text,lg = get_text_and_language(student,7)
        await message.answer(f'{text}')

    elif save_data is not None:
        await message.answer('Ваша заявка уже отправлена')

    else:
        text = main[0][1]
        await message.answer(f'{text}',reply_markup=CreateInline(ru='Ru',uz='Uz'))
        await state.set_state(StateUser.ru)
        await message.delete()

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
        await call.message.delete()
        await state.set_state(StateUser.ru)

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
    await state.update_data({'LG':'ru'})
    main = db.read(DESCR,where_clause='title_id = 9')
    des = main[0][2]
    await call.message.answer(des,reply_markup=CreateInline(tch='Teachers',std='Students',pr='Parents'))
    await state.set_state(StateUser.who)
    await call.message.delete()

@user_private_router.callback_query(F.data,StateUser.who)
async def tch(call:CallbackQuery,state:FSMContext):
    who = call.data
    user_id = call.from_user.id
    main = db.read(DESCR,where_clause='title_id = 4')
    des = main[0][1]
    await state.update_data({'who':who,'user_id':user_id})
    await call.message.answer(text=des,reply_markup=CreateBut([p[2] for p in db.read(BUT)],back_ru='Orqaga'))
    await state.set_state(StateUser.school)
    await call.message.delete()

@user_private_router.callback_query(F.data,StateUser.school)
async def name(call:CallbackQuery,state:FSMContext):
    data = await state.get_data()
    lg = data.get("LG")
    school = call.data
    n = 2 if lg == 'ru' else 1
    main = db.read(DESCR,where_clause='title_id = 5')
    text = main[0][n]
    name = await call.message.answer(text)
    await state.update_data({'school':school,'muc_del':name})
    await state.set_state(StateUser.city)
    await call.message.delete()


@user_private_router.message(F.text,StateUser.city)
async def muc(message:Message,state:FSMContext):
    data = await state.get_data()
    lg = data.get("LG")
    city = message.text
    n = 2 if lg == 'ru' else 1
    main = db.read(DESCR,where_clause='title_id = 8')
    text = main[0][n]
    sent_message = await message.answer(text)
    await state.update_data({'city':city,'name_del':sent_message})
    await state.set_state(StateUser.muc)

@user_private_router.message(F.text,StateUser.muc)
async def name(message:Message,state:FSMContext):
    data = await state.get_data()
    who = data.get('who')
    muc = message.text
    await state.update_data({'muc':muc})
    lg = data.get('LG')
    n = 2 if lg == 'ru' else 1
    if who == 'Tch_a' or who == 'Pr_a':
        main = db.read(DESCR,where_clause='title_id = 3')
        text = main[0][n]
        await message.answer(text=text)
        await state.set_state(StateUser.student_name)
    else:
        main = db.read(DESCR,where_clause='title_id = 10')
        text = main[0][n]
        await message.answer(text=text)
        await state.set_state(StateUser.teacher_name)


@user_private_router.message(F.text,StateUser.teacher_name)
async def nme(message:Message,state:FSMContext):
    data = await state.get_data()
    lg = data.get('LG')
    who = data.get('who')
    teacher_name = message.text
    n = 2 if lg == 'ru' else 1
    await state.update_data({'teacher_name':teacher_name})
    if who == 'std':
        main = db.read(DESCR,where_clause='title_id = 3')
        text = main[0][n]
        await message.answer(text=text)
        await state.set_state(StateUser.student_name)
    else:
        n, test = (2, 'Отправить контакт') if lg == 'ru' else (1, 'Kontaktni yuboring')
        main = db.read(DESCR,where_clause='title_id = 6')
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

        await message.answer(text=text,reply_markup=contact_button)
        await state.set_state(StateUser.number)

@user_private_router.message(F.text,StateUser.student_name)
async def name(message:Message,state:FSMContext):
    data = await state.get_data()
    who = data.get('who')
    student_name = message.text
    lg = data.get('LG')
    n, test = (2, 'Отправить контакт') if lg == 'ru' else (1, 'Kontaktni yuboring')
    await state.update_data({'student_name':student_name})
    if who == 'Tch_a' or who == 'Pr_a':
        main = db.read(DESCR,where_clause='title_id = 11')
        text = main[0][n]
        await message.answer(text=text)
        await state.set_state(StateUser.teacher_num)
    else:
        main = db.read(DESCR,where_clause='title_id = 6')
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
        await message.answer(text=text,reply_markup=contact_button)
        await state.set_state(StateUser.number)


@user_private_router.message(F.contact,StateUser.number)
async def num(message:Message,state:FSMContext):
    data = await state.get_data()
    lg = data.get("LG")
    who = data.get('who')
    num = message.contact.phone_number
    n = 2 if lg == 'ru' else 1

    def is_uzbek_number(phone_number):
        return phone_number.startswith('+998') or phone_number.startswith('998')
    
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
        main = db.read(DESCR,where_clause='title_id = 11')
        text = main[0][n]
        await state.update_data({'student_num':num})

        if is_uzbek_number(num):
            await message.answer(text=text)
            await state.set_state(StateUser.teacher_num)
        else:
            await message.answer('error')
    else:
        await state.update_data({'teacher_num':num})
        
        current_texts = texts[lg]
        bt = current_texts["online_payment"]
        bt2 = current_texts["in_person_payment"]
        error_text = current_texts["error_text"]

        main = db.read(DESCR,where_clause='title_id = 7')
        py = main[0][n]
        
        if is_uzbek_number(num):
            await message.answer(py,reply_markup=CreateInline(bt,bt2))
            await state.set_state(StateUser.py)
        else:
            await message.answer(error_text)

@user_private_router.message(F.text | F.contact,StateUser.teacher_num)
async def nur(message:Message,state:FSMContext):
    data = await state.get_data()
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

    def is_valid_phone_number(phone_number):
        return (phone_number.startswith('+998') or phone_number.startswith('998')) and len(phone_number) in [12, 13]

    teacher_num = message.contact.phone_number if message.contact else message.text
        
    if is_valid_phone_number(teacher_num):
        main = db.read(DESCR,where_clause='title_id = 7')
        py = main[0][n]
        await message.answer(py,reply_markup=CreateInline(bt,bt2))
        await state.update_data({'teacher_num':teacher_num})
        await state.set_state(StateUser.py)
    else:
        # Если номер не из Узбекистана
        await message.answer(error_text)


@user_private_router.callback_query((F.data == 'Оплатить Онляйн') | (F.data == 'Onlayn to\'lov'), StateUser.py)
async def py(call:CallbackQuery,state:FSMContext):
    data = await state.get_data()
    lg = data.get("LG")
    test = 'Отправьте чек' if lg == 'ru' else 'Tolov Chekini yuboring'
    await call.message.answer(test)
    await state.set_state(StateUser.py1)

@user_private_router.message(StateUser.py1,MediaFilter())
async def handle_media(message: Message, state: FSMContext):
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
    url = message.from_user.url

    texts = {
        "ru": {
            "ask_file": "Пожалуйста, отправьте Фото или PDF файл.",
            "confirm_text": "ваш чек отправить на проверку?",
            "bt_yes": "Да",
            "bt_no": "Нет",
            "student_profile": f"Ваш профиль \n\nИмя учителя: {teacher_name}\n\nИмя: {student_name}\n\nШкола: {muc}\n\nКласс: {school}\n\nГород: {city}\n\nНомер учителя: {teacher_num}\n\nНомер: {student_num}\n\n",
            "teacher_profile": f"Ваш профиль\n\nИмя: {student_name}\n\nШкола: {muc}\n\nКласс: {school}\n\nГород: {city}\n\nНомер: {teacher_num}\n\n"
        },
        "uz": {
            "ask_file": "Iltimos, fotosurat yoki PDF faylini yuboring.",
            "confirm_text": "tekshirish uchun chekingizni yuboring?",
            "bt_yes": "Ha",
            "bt_no": "Yok",
            "student_profile": f"Sizning profilingiz \n\nUztozingizni Ismi: {teacher_name}\n\nIsm: {student_name}\n\nMaktab: {muc}\n\nSinif: {school}\n\nTuman: {city}\n\nTelefon raqam: {student_num}\n\nUztozingizni telefon nomeri: {teacher_num}\n\n",
            "teacher_profile": f"Sizning profilingiz \n\nIsm: {teacher_name}\n\nMaktab: {muc}\n\nSinif: {school}\n\nTuman: {city}\n\nTelefon raqam: {teacher_num}\n\n"
        }
    }

    current_texts = texts[lg]
    bt = current_texts["bt_yes"]
    bt2 = current_texts["bt_no"]
    ask_file_text = current_texts["ask_file"]

    if who == 'std':
        profile_text = current_texts["student_profile"]
    else:
        profile_text = current_texts["teacher_profile"]

    final_text = f"{profile_text}{current_texts['confirm_text']}"

    if message.content_type == ContentType.PHOTO:
        photo_id = message.photo[-1].file_id
        await state.update_data({'photo_id': photo_id, 'url': url, 'n': 1})
        await message.reply(text=final_text, reply_markup=CreateInline(bt, bt2))

    elif message.content_type == ContentType.DOCUMENT:
        if message.document.mime_type == 'application/pdf':
            doc = message.document.file_id
            await state.update_data({'doc': doc, 'url': url, 'n': 2})
            await message.reply(text=final_text, reply_markup=CreateInline(bt, bt2))
    else:
        await message.answer(text=ask_file_text)


@user_private_router.callback_query((F.data=='Да') | (F.data == 'Ha'))
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
        std_name = student_name

    common_data = {
        "telegram_id": user_id,
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

@user_private_router.callback_query((F.data=='Нет') | (F.data == 'Yoq'))
async def net(call:CallbackQuery,state:FSMContext):
    data = await state.get_data()
    lg = data.get("LG")
    if lg == 'ru':
        test = f'Желаете пройти регистрацию заново?\n Нажмите суда -> /start'
    else:
        test = f'Tekshiruv tasdiqlanmadi!!!\nQayta ro\'yxatdan o\'ting -> /start'
    await call.message.answer(test)
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
                        f"{'ваш чек отправить на проверку?' if lg == 'ru' else 'Tekshirish uchun chekingizni yuboring?'}")
    else:
        profile_text = (f"{'Ваш профиль' if lg == 'ru' else 'Sizning profilingiz'}\n\n"
                        f"{'Имя' if lg == 'ru' else 'Ism'}: {teacher_name}\n"
                        f"{'Школа' if lg == 'ru' else 'Maktab'}: {muc}\n"
                        f"{'Класс' if lg == 'ru' else 'Sinif'}: {school}\n"
                        f"{'Город' if lg == 'ru' else 'Tuman'}: {city}\n"
                        f"{'Номер' if lg == 'ru' else 'Telefon raqam'}: {teacher_num}\n"
                        f"{'ваш чек отправить на проверку?' if lg == 'ru' else 'Tekshirish uchun chekingizni yuboring?'}")

    await call.message.answer(text=profile_text,reply_markup=CreateInline(yees=bt,neet=bt2))
    await state.set_state(StateUser.yep)
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

    n,ru = (2,'ru') if lg == 'ru' else (1,'uz')

    teacher = db.read(
        TEACHER_MOD,
        where_clause=f'telegram_id = {user_id}'
    )
    parent = db.read(
        PARENTS_MOD,
        where_clause=f'telegram_id = {user_id}'
    )

    common_data = {
        "telegram_id": user_id,
        "school": school,
        "class_name": muc,
        "city": city,
        "payment": False,  # Платеж не выполнен
        "language": ru
    }


    if who == 'std':
        common_data.update({
            "student_name": student_name,
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
    main = db.read(DESCR,where_clause=f'title_id = 1')
    test = main[0][n]
    await call.message.answer(f'{test}')
    await state.clear()

@user_private_router.callback_query(F.data=='neet',StateUser.yep)
async def net(call:CallbackQuery,state:FSMContext):
    data = await state.get_data()
    lg = data.get("LG")
    if lg == 'ru':
        test = f'Желаете пройти регистрацию заново?\n Нажмите суда -> /start'
    elif lg == 'uz':
        test = f'Tekshiruv tasdiqlanmadi!!!\nQayta ro\'yxatdan o\'ting -> /start'
    await call.message.answer(test)
    await state.clear()
    await call.message.delete()