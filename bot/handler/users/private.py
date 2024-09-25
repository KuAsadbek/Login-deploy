from aiogram import Router,F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import CommandStart
from aiogram.types import Message,CallbackQuery,KeyboardButton,ReplyKeyboardMarkup,ContentType,InlineKeyboardButton,ReplyKeyboardRemove
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
    teacher = db.read(
        TEACHER_MOD,
        where_clause=f'telegram_id = {user_id}'
    )
    parent = db.read(
        PARENTS_MOD,
        where_clause=f'telegram_id = {user_id}'
    )
    save_data = db.read(
        SAVE_DATA,
        where_clause=f'telegram_id = {user_id}'
    )
    student = db.read(
        USERMOD,
        where_clause=f'telegram_id = {user_id}'
    )

    if teacher is not None:
        lg = teacher[0][8]
        n = 2 if lg == 'ru' else 1
        text = main[0][n]
        await state.update_data({'LG':lg,'tch_id':user_id,'who':'Tch_a'})
        await message.answer(
            f'{text}',
            reply_markup=CreateInline(add_std='add students')
        )

    elif parent is not None:
        lg = parent[0][8]
        n = 2 if lg == 'ru' else 1
        text = main[0][n]
        await state.update_data({'LG':lg,'pr_id':user_id,'who':'Pr_a'})
        await message.answer(
            f'{text}',
            reply_markup=CreateInline(add_std='add student')
        )

    elif student is not None:
        lg = student[0][7]
        n = 2 if lg == 'ru' else 1
        text = main[0][n]
        await message.answer(
            f'{text}'
        )

    elif save_data is not None:
        await message.answer('Ваша заявка уже отправлена')

    else:
        text = main[0][1]
        await message.answer(
            f'{text}',
            reply_markup=CreateInline(ru='Ru',uz='Uz')
        )
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
    comment = message.text
    url = message.from_user.url
    name = message.from_user.full_name
    if lg == 'ru':
        n = 'спасибо за коммент'
    elif lg == 'uz':
        n = 'Izoh kildirganigiz uchun harmat'
    await message.bot.send_message(
        chat_id=CHANEL_ID,
        text=f'comment from user <a href="{url}"><b>{name}</b></a>:\n{comment}',parse_mode=None
    )
    await message.answer(n)


@user_private_router.callback_query(F.data=='back_ru',StateUser.school)
async def cmd_ru(call:CallbackQuery,state:FSMContext):
    main = db.read(DESCR,where_clause=f'title_id = {1}')
    text = main[0][1]
    await call.message.answer(
        f'{text}',
        reply_markup=CreateInline(ru='Ru',uz='Uz')
    )
    await call.message.delete()
    await state.set_state(StateUser.ru)

@user_private_router.callback_query(F.data=='add_std')
async def ste(call:CallbackQuery,state:FSMContext):
    data = await state.get_data()
    lg = data.get('LG')
    n = 2 if lg == 'ru' else 1
    main = db.read(DESCR,where_clause='title_id = 4')
    des = main[0][n]
    await call.message.answer(
        text=des,
        reply_markup=CreateBut([p[n] for p in db.read(BUT)],back_ru='Orqaga')
    )
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
    await call.message.answer(
        des,
        reply_markup=CreateInline(tch='Teachers',std='Students',pr='Parents')
    )
    await state.set_state(StateUser.who)
    await call.message.delete()

@user_private_router.callback_query(F.data,StateUser.who)
async def tch(call:CallbackQuery,state:FSMContext):
    who = call.data
    user_id = call.from_user.id
    main = db.read(DESCR,where_clause='title_id = 4')
    des = main[0][1]
    await state.update_data({'who':who,'user_id':user_id})
    await call.message.answer(
        text=des,
        reply_markup=CreateBut([p[2] for p in db.read(BUT)],back_ru='Orqaga')
    )
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
        await message.answer(
            text=text
        )
        await state.set_state(StateUser.student_name)
    else:
        main = db.read(DESCR,where_clause='title_id = 10')
        text = main[0][n]
        await message.answer(
            text=text
        )
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
        await message.answer(
            text=text
        )
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

        await message.answer(
            text=text,
            reply_markup=contact_button
        )
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
        await message.answer(
                text=text
            )
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
        await message.answer(
            text=text,
            reply_markup=contact_button
        )
        await state.set_state(StateUser.number)


@user_private_router.message(F.contact,StateUser.number)
async def num(message:Message,state:FSMContext):
    data = await state.get_data()
    lg = data.get("LG")
    who = data.get('who')
    num = message.contact.phone_number
    print(num)
    n = 2 if lg == 'ru' else 1
    if who == 'std':
        main = db.read(DESCR,where_clause='title_id = 11')
        text = main[0][n]

        await state.update_data({'student_num':num})

        if num.startswith('+998') or num.startswith('998'):
            await message.answer(
                text=text
            )
            await state.set_state(StateUser.teacher_num)
        else:
            # Если номер не из Узбекистана
            await message.answer(
                'error'
            )
    else:
        await state.update_data({'teacher_num':num})
        if lg == 'ru':
            bt = 'Оплатить Онляйн'
            bt2 = 'Прийти и заплатить'
            test = 'Пожалуйста, отправьте узбекский номер, который начинается с +998.'
        else:
            bt = 'Onlayn to\'lov'
            bt2 = 'Borib tolash'
            test = '+998 bilan boshlanadigan o\'zbek raqamini yuboring.'
        main = db.read(DESCR,where_clause='title_id = 7')
        py = main[0][n]
        
        if num.startswith('+998') or num.startswith('998'):
            print(num)
            await message.answer(
                py,
                reply_markup=CreateInline(bt,bt2)
            )
            await state.set_state(StateUser.py)
        else:
            # Если номер не из Узбекистана
            await message.answer(
                test
            )

@user_private_router.message(F.text | F.contact,StateUser.teacher_num)
async def nur(message:Message,state:FSMContext):
    data = await state.get_data()
    lg = data.get('LG')
    if lg == 'ru':
        bt = 'Оплатить Онляйн'
        bt2 = 'Прийти и заплатить'
        test = 'Пожалуйста, отправьте узбекский номер, который начинается с +998.'
        n = 2 
    else:
        bt = 'Onlayn to\'lov'
        bt2 = 'Borib tolash'
        test = '+998 bilan boshlanadigan o\'zbek raqamini yuboring.'
        n = 1

    if message.contact:
        teacher_num = message.contact.phone_number
    elif message.text:
        teacher_num = message.text
        
    if teacher_num.startswith('+998') or teacher_num.startswith('998') and len(teacher_num) == 13 or len(teacher_num) == 12:
        main = db.read(DESCR,where_clause='title_id = 7')
        py = main[0][n]
        await message.answer(
            py,
            reply_markup=CreateInline(bt,bt2)
        )
        await state.update_data({'teacher_num':teacher_num})
        await state.set_state(StateUser.py)
    else:
        # Если номер не из Узбекистана
        await message.answer(
            test
        )


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

    if lg == 'ru':
        bt = 'Да'
        bt2 = 'Нет'
        tex = 'Пожалуйста, отправьте Фото или PDF файл.'
        if who == 'std':
            test = f'Ваш профиль \n\nИмя учителя: {teacher_name}\n\nИмя: {student_name}\n\nШкола: {muc}\n\nКлаасс: {school}\n\nГород: {city}\n\nНомер учителя: {teacher_num}\n\nНомер: {student_num}\n\nваш чек отправить на проверку?'
        elif who == 'Tch_a' or who == 'Pr_a':
            test = '361 line i\'m laziness'
        else:
            test = f'Ваш профиль\n\nИмя: {teacher_name}\n\nШкола: {muc}\n\nКлаасс: {school}\n\nГород: {city}\n\nНомер: {teacher_num}\n\nваш чек отправить на проверку?'
    elif lg == 'uz':
        tex = 'Iltimos, fotosurat yoki PDF faylini yuboring.'
        bt = 'Ha'
        bt2 = 'Yok'
        if who == 'std':
            test = f'Sizning profilingiz \n\nUztozingizni Ismi: {teacher_name} \n\nIsm: {student_name}\n\nMaktab: {muc}\n\nSnif: {school}\n\nTuman: {city}\n\nTelefon raqam: {student_num}\n\nUztozingizni telefon nomeri: {teacher_num}\n\ntekshirish uchun chekingizni yuboring?'
        else:
            test = f'Sizning profilingiz \n\nIsm: {teacher_name}\n\nMaktab: {muc}\n\nSnif: {school}\n\nTuman: {city}\n\nTelefon raqam: {teacher_name}\n\ntekshirish uchun chekingizni yuboring?'
    
    if message.content_type == ContentType.PHOTO:
        photo_id = message.photo[-1].file_id
        await state.update_data({'photo_id':photo_id,'url':url,'n':1})
        await message.reply(
            text=test,
            reply_markup=CreateInline(bt,bt2)
        )
    elif message.content_type == ContentType.DOCUMENT:
        if message.document.mime_type == 'application/pdf':
            doc = message.document.file_id
            await state.update_data({'doc':doc,'url':url,'n':2})
            await message.reply(
                text=test,
                reply_markup=CreateInline(bt,bt2)
            )
    else:
        await message.answer(text=tex)


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

    common_data = {
        "telegram_id": user_id,
        'who':who,
        "school": school,
        "city": city,
        "class_name": muc,
        "language": lg
    }

    n = data.get('n')

    button = InlineKeyboardBuilder()
    button.add(InlineKeyboardButton(text='Принять',callback_data=f'Tr_{user_id}'))
    button.add(InlineKeyboardButton(text='Отклонить',callback_data=f'Fr_{user_id}'))
    button.adjust(2)

    if lg == 'ru':
        test = f'Ваш чек отправлено на проверку!'
        bt = 'Оставить комментарий'
    elif lg == 'uz':
        bt = 'Izoh koldiring'
        test = f'Chekingiz tekshirish uchun yuborildi!'
    if who == 'std':
            name = student_name
            common_data["student_name"] = student_name
            common_data["teacher_name"] = teacher_name
            common_data["teacher_number"] = teacher_num
            common_data["student_number"] = student_num
            db.insert(SAVE_DATA, **common_data)
    elif who == 'Tch_a' or who == 'Pr_a':
            name = student_name
            common_data["teacher_number"] = teacher_num
            common_data["student_name"] = student_name
            db.insert(SAVE_DATA, **common_data)
    else:
        name = teacher_name
        common_data["teacher_number"] = teacher_num
        common_data["teacher_name"] = teacher_name
        db.insert(SAVE_DATA, **common_data)
    if n == 1:
        photo_id = data.get("photo_id")
        await call.message.bot.send_photo(
                chat_id= CHANEL_ID ,  # ID администратора
                photo=photo_id,
                caption=f"Чек от пользователя <a href='{url}'><b>{name}</b></a>",
                reply_markup=button.as_markup()
        )
    else:
        doc = data.get('doc')
        await call.message.bot.send_document(
            chat_id= CHANEL_ID ,
            document=doc,
            caption=f"PDF файл от пользователя <a href='{url}'><b>{name}</b></a>",
            reply_markup=button.as_markup()
        )
    await call.message.answer(test,reply_markup=CreateInline(bt))
    await call.message.delete()


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
        if who == 'std':
            test = f'Ваш профиль \n\nИмя учителя: {teacher_name}\n\nИмя: {student_name}\n\nШкола: {muc}\n\nКлаасс: {school}\n\nГород: {city}\n\nНомер учителя: {teacher_num}\n\nНомер: {student_num}\n\nваш чек отправить на проверку?'
        else:
            test = f'Ваш профиль \n\nИмя: {teacher_name}\n\nШкола: {muc}\n\nКлаасс: {school}\n\nГород: {city}\n\nНомер: {teacher_num}\n\nваш чек отправить на проверку?'
    elif lg == 'uz':
        bt = 'Ha'
        bt2 = 'Yok'
        if who == 'std':
            test = f'Sizning profilingiz \n\nUztozingizni Ismi: {teacher_name} \n\nIsm: {student_name}\n\nMaktab: {muc}\n\nSnif: {school}\n\nTuman: {city}\n\nTelefon raqam: {student_num}\n\nUztozingizni telefon nomeri: {teacher_num}\n\ntekshirish uchun chekingizni yuboring?'
        else:
            test = f'Sizning profilingiz \n\n Ism: {teacher_name}\n\nMaktab: {muc}\n\nSnif: {school}\n\nTuman: {city}\n\nTelefon raqam: {teacher_num}\n\ntekshirish uchun chekingizni yuboring?'
    await call.message.answer(
        text=test,
        reply_markup=CreateInline(yees=bt,neet=bt2)
    )
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
    py = False
    user_id = call.from_user.id

    lg = data.get("LG")
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
        "payment": py,
        "language": ru
    }

    if who == 'std':
        common_data["student_name"] = student_name
        common_data["teacher_name1"] = teacher_name
        common_data["teacher_number"] = teacher_num
        common_data["student_number"] = student_num
        db.insert(USERMOD, **common_data)
    elif who == 'Tch_a':
        teacher_id = teacher[0][0]
        tch_name = teacher[0][2]
        tch_num = teacher[0][6]
        common_data["teacher_name_id"] = teacher_id
        common_data["teacher_name1"] = tch_name
        common_data["teacher_number"] = tch_num
        common_data["student_name"] = student_name
        common_data["student_number"] = teacher_num
        db.insert(USERMOD, **common_data)
    elif who == 'Pr_a':
        parent_id = parent[0][0]
        pr_name = parent[0][2]
        pr_num = parent[0][6]
        common_data["parents_id"] = parent_id
        common_data["teacher_name1"] = pr_name
        common_data["teacher_number"] = pr_num
        common_data["student_name"] = student_name
        common_data["student_number"] = teacher_num
        db.insert(USERMOD, **common_data)
    elif who == 'tch':
        common_data["teacher_name"] = teacher_name
        common_data["teacher_number"] = teacher_num
        db.insert(TEACHER_MOD, **common_data)
    elif who == 'pr':
        common_data["parent_name"] = teacher_name
        common_data["parent_number"] = teacher_num
        db.insert(PARENTS_MOD, **common_data)
        
    main = db.read(DESCR,where_clause=f'title_id = 1')
    test = main[0][n]
    await call.message.answer(
        f'{test}'
    )
    await state.clear()
    await call.message.delete()


@user_private_router.callback_query(F.data=='neet',StateUser.yep)
async def net(call:CallbackQuery,state:FSMContext):
    data = await state.get_data()
    lg = data.get("LG")
    if lg == 'ru':
        test = f'Tekshiruv tasdiqlanmadi!!!\nQayta ro\'yxatdan o\'ting -> /start'
    elif lg == 'uz':
        test = f'Желаете пройти регистрацию заново?\n Нажмите суда -> /start'
    await call.message.answer(test)
    await state.clear()
    await call.message.delete()