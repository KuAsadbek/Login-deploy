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
        lg = teacher[0][7]
        if lg == 'ru':
            n = 2
        elif lg == 'uz':
            n = 1
        text = main[0][n]
        await state.update_data({'LG':lg,'tch_id':user_id})
        await message.answer(
            f'{text}',
            reply_markup=CreateInline(add_std='add students')
        )

    elif parent is not None:
        lg = parent[0][7]
        if lg == 'ru':
            n = 2
        elif lg == 'uz':
            n = 1
        text = main[0][n]
        await state.update_data({'LG':lg,'pr_id':user_id})
        await message.answer(
            f'{text}',
            reply_markup=CreateInline(add_std='add student')
        )

    elif save_data is not None:
        await message.answer('Ваша заявка уже отправлена')

    elif student is not None:
        lg = student[0][7]
        if lg == 'ru':
            n = 2
        elif lg == 'uz':
            n = 1
        text = main[0][n]
        await message.answer(
            f'{text}'
        )

    else:
        text = main[0][1]
        await message.answer(
            f'{text}',
            reply_markup=CreateInline(tch='Teachers',std='Students',pr='Parents')
        )
        await state.set_state(StateUser.who)
        await message.delete()

@user_private_router.callback_query(F.data=='add_std')
async def ste(call:CallbackQuery,state:FSMContext):
    await call.message.answer('напишите уникальную id для вашего ученика')
    await state.set_state(StateUser.un_id)
    await call.message.delete()

@user_private_router.message(F.text,StateUser.un_id)
async def std(message:Message,state:FSMContext):
    un_id = message.text
    if un_id.isdigit() and len(un_id) >= 5 and len(un_id) <= 15:
        data = await state.get_data()
        tch = data.get('tch_id')
        pr_id = data.get('pr_id')
        if tch:
            await state.update_data({'who':'Tch_a','un_id':un_id})
        elif pr_id:
            await state.update_data({'who':'Pr_a','un_id':un_id})        
        lg = data.get('LG')
        if lg == 'ru':
            n = 2
        elif lg == 'uz':
            n = 1
        main = db.read(DESCR,where_clause='title_id = 4')
        des = main[0][n]
        await message.answer(
            des,
            reply_markup=CreateBut([p[n] for p in db.read(BUT)],back_ru='Назад')
        )
        await state.set_state(StateUser.school)
        await message.delete()
    else:
        await message.answer('Ведите только число\nчисло не должно быть меньше 5 и больше 15')
        await message.delete()

# @user_private_router.callback_query(F.data,StateUser.who)
# async def tch(call:CallbackQuery,state:FSMContext):
#     who = call.data
#     user_id = call.from_user.id
#     await state.update_data({'who':who,'user_id':user_id})
#     await call.message.answer(text='Выберите язык',reply_markup=CreateInline(ru='Ru',uz='Uz'))
#     await state.set_state(StateUser.ru)
#     await call.message.delete()

# # ru_start
# @user_private_router.callback_query(F.data=='ru',StateUser.ru)
# async def cmd_ru(call:CallbackQuery,state:FSMContext):
#     await state.update_data({'LG':'ru'})
#     main = db.read(DESCR,where_clause='title_id = 4')
#     des = main[0][2]
#     await call.message.answer(
#         des,
#         reply_markup=CreateBut([p[1] for p in db.read(BUT)],back_ru='Назад')
#     )
#     await state.set_state(StateUser.school)
#     await call.message.delete()


# @user_private_router.callback_query(F.data=='uz',StateUser.ru)
# async def cmd_ru(call:CallbackQuery,state:FSMContext):
#     await state.update_data({'LG':'uz'})
#     main = db.read(DESCR,where_clause='title_id = 4')
#     des = main[0][1]
#     await call.message.answer(
#         des,
#         reply_markup=CreateBut([p[2] for p in db.read(BUT)],back_ru='Orqaga')
#     )
#     await state.set_state(StateUser.school)
#     await call.message.delete()



@user_private_router.callback_query((F.data=='Оставить комментарий') | (F.data == 'Izoh koldiring'))
async def mes(call:CallbackQuery,state:FSMContext):
    data = await state.get_data()
    lg = data.get("LG")
    if lg == 'ru':
        n = 'Ваш комментарий'
    elif lg == 'uz':
        n = 'Izoh'
    com_del = await call.message.answer(n)
    await state.update_data({'com_del':com_del})
    await call.message.delete()
    await state.set_state(StateUser.comment)

@user_private_router.message(StateUser.comment,F.text)
async def mes1(message:Message,state:FSMContext):
    data = await state.get_data()
    com_del = data.get('com_del')
    lg = data.get("LG")
    if lg == 'ru':
        n = 'спасибо за коммент'
    elif lg == 'uz':
        n = 'Izoh kildirganigiz uchun harmat'
    comment = message.text
    url = message.from_user.url
    name = message.from_user.full_name
    await message.bot.send_message(
        chat_id=CHANEL_ID,
        text=f'comment from user <a href="{url}"><b>{name}</b></a>:\n{comment}',parse_mode=None
    )
    await message.answer(n)
    await com_del.delete()

# @user_private_router.callback_query(F.data=='back_ru',StateUser.school)
# async def cmd_ru(call:CallbackQuery,state:FSMContext):
#     main = db.read(DESCR,where_clause=f'title_id = {1}')
#     text = main[0][1]
#     await call.message.answer(
#         f'{text}',
#         reply_markup=CreateInline(ru='Ru',uz='Uz')
#     )
#     await call.message.delete()
#     await state.set_state(StateUser.ru)

# @user_private_router.callback_query(F.data,StateUser.school)
# async def name(call:CallbackQuery,state:FSMContext):
#     data = await state.get_data()
#     lg = data.get("LG")
#     school = call.data
#     if lg == 'ru':
#         n = 2
#     elif lg == 'uz':
#         n = 1
#     main = db.read(DESCR,where_clause='title_id = 8')
#     text = main[0][n]
#     name = await call.message.answer(text)
#     await state.update_data({'school':school,'muc_del':name})
#     await state.set_state(StateUser.muc)
#     await call.message.delete()

@user_private_router.message(F.text,StateUser.muc)
async def muc(message:Message,state:FSMContext):
    data = await state.get_data()
    name = data.get('muc_del')
    lg = data.get("LG")
    muc1 = message.text
    
    n = 2 if lg == 'ru' else 1
    main = db.read(DESCR,where_clause='title_id = 3')
    text = main[0][n]
    sent_message = await message.answer(text)
    await state.update_data({'muc':muc1,'name_del':sent_message})
    await state.set_state(StateUser.name)
    await name.delete()

@user_private_router.message(F.text,StateUser.name)
async def name1(message:Message,state:FSMContext):
    data = await state.get_data()
    name_del = data.get('name_del')
    lg = data.get("LG")
    title = message.text
    if lg == 'ru':
        n = 2 
    elif lg == 'uz':
        n = 1
    main = db.read(DESCR,where_clause='title_id = 5')
    city = main[0][n]
    city_del = await message.answer(city)
    await state.update_data({'title':title,'city_del':city_del})
    await state.set_state(StateUser.city)
    await name_del.delete()

@user_private_router.message(F.text,StateUser.city)
async def city1(message:Message,state:FSMContext):
    data = await state.get_data()
    cit_del = data.get('city_del')
    lg = data.get("LG")
    city = message.text

    if lg == 'ru':
        test = 'Отправить контакт'
        n = 2 
    elif lg == 'uz':
        test = 'Kontaktni yuboring'
        n = 1
    main = db.read(DESCR,where_clause='title_id = 6')
    number = main[0][n]

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
    num_del = await message.answer(number,reply_markup=contact_button)
    await state.update_data({'city':city,'num_del':num_del})
    await state.set_state(StateUser.number)
    await cit_del.delete()

@user_private_router.message(F.contains,StateUser.number)
async def num(message:Message,state:FSMContext):
    data = await state.get_data()
    num_del = data.get('num_del')
    lg = data.get("LG")
    num = message.contact.phone_number

    if lg == 'ru':
        bt = 'Оплатить Онляйн'
        bt2 = 'Прийти и заплатить'
        test = 'Пожалуйста, отправьте узбекский номер, который начинается с +998.'
        n = 2 
    elif lg == 'uz':
        bt = 'Onlayn to\'lov'
        bt2 = 'Borib tolash'
        test = '+998 bilan boshlanadigan o\'zbek raqamini yuboring.'
        n = 1
    if num.startswith('+380') and len(num) == 13:
        main = db.read(DESCR,where_clause='title_id = 7')
        py = main[0][n]
        py_del = await message.answer(
            py,
            reply_markup=CreateInline(bt,bt2)
        )
        await state.update_data({'num':num,'py_del':py_del})
        await state.set_state(StateUser.py)
    else:
        # Если номер не из Узбекистана
        py_del = await message.answer(
            test
        )
        await state.update_data({'py_del':py_del})
    await num_del.delete()

# @user_private_router.callback_query((F.data == 'Оплатить Онляйн') | (F.data == 'Onlayn to\'lov'), StateUser.py)
# async def py(call:CallbackQuery,state:FSMContext):
#     data = await state.get_data()
#     py_del = data.get('py_del')
#     lg = data.get("LG")

#     if lg == 'ru':
#         test = 'Отправьте чек'
#     elif lg == 'uz':
#         test = 'Tolov Chekini yuboring'
#     py1_del = await call.message.answer(test)
#     await state.update_data({'py1_del':py1_del})
#     await state.set_state(StateUser.py1)
#     await py_del.delete()

# @user_private_router.message(StateUser.py1,MediaFilter())
# async def handle_media(message: Message, state: FSMContext):
#     data = await state.get_data()
#     py1_del = data.get('py1_del')
#     lg = data.get("LG")
#     num = data.get('num')
#     city = data.get('city')
#     title = data.get('title')
#     muc = data.get('muc')
#     school = data.get('school')
#     tch_id = data.get('tch_id')

#     if lg == 'ru':
#         bt = 'Да'
#         bt2 = 'Нет'
#         tex = 'Пожалуйста, отправьте Фото или PDF файл.'
#         if tch_id:
#             test = f'Профиль вашего ученика \n\nИмя: {title}\n\nШкола: {muc}\n\nКлаасс: {school}\n\nГород: {city}\n\nНомер: {num}\n\nваш чек отправить на проверку?'
#         else:
#             test = f'Ваш профиль \n\nИмя: {title}\n\nШкола: {muc}\n\nКлаасс: {school}\n\nГород: {city}\n\nНомер: {num}\n\nваш чек отправить на проверку?'
#     elif lg == 'uz':
#         tex = 'Iltimos, fotosurat yoki PDF faylini yuboring.'
#         bt = 'Ha'
#         bt2 = 'Yok'
#         if tch_id:
#             test = f'Sizning o\'quvchining profilingiz \n\nIsm: {title}\n\nMaktab: {muc}\n\nSnif: {school}\n\nTuman: {city}\n\nTelefon raqam: {num}\n\ntekshirish uchun chekingizni yuboring?'
#         else:
#             test = f'Sizning profilingiz \n\nIsm: {title}\n\nMaktab: {muc}\n\nSnif: {school}\n\nTuman: {city}\n\nTelefon raqam: {num}\n\ntekshirish uchun chekingizni yuboring?'
    
#     if message.content_type == ContentType.PHOTO:

#         url = message.from_user.url
#         photo_id = message.photo[-1].file_id

#         await state.update_data({'photo_id':photo_id,'url':url,'n':1})

#         await message.reply(
#             text=test,
#             reply_markup=CreateInline(bt,bt2)
#         )

#     elif message.content_type == ContentType.DOCUMENT:
#         if message.document.mime_type == 'application/pdf':
#             url = message.from_user.url
#             doc = message.document.file_id
#             await state.update_data({'doc':doc,'url':url,'n':2})

#             await message.reply(
#                 text=test,
#                 reply_markup=CreateInline(bt,bt2)
#             )
#     else:
#         await message.answer(text=tex)
#     await py1_del.delete()

# @user_private_router.callback_query((F.data=='Да') | (F.data == 'Ha'))
# async def yes(call:CallbackQuery,state:FSMContext):
#     data = await state.get_data()
#     lg = data.get("LG")
#     who = data.get("who")
#     n = data.get('n')
#     title = data.get('title')
#     user_id = call.from_user.id
#     school = data.get('school')
#     city = data.get('city')
#     num = data.get('num')
#     muc = data.get('muc')
#     un_id = data.get('un_id')

#     button = InlineKeyboardBuilder()
#     button.add(InlineKeyboardButton(text='Принять',callback_data=f'Tr_{user_id}'))
#     button.add(InlineKeyboardButton(text='Отклонить',callback_data=f'Fr_{user_id}'))
#     button.adjust(2)

#     if lg == 'ru':
#         test = f'Ваш чек отправлено на проверку!'
#         bt = 'Оставить комментарий'
#         ru = 'ru'
#     elif lg == 'uz':
#         bt = 'Izoh koldiring'
#         ru = 'uz'
#         test = f'Chekingiz tekshirish uchun yuborildi!'
#     if n == 1:
#         photo_id = data.get("photo_id")
#         url = data.get('url')
#         if un_id:
#             un = int(un_id)
#             db.insert(
#                 SAVE_DATA,
#                 telegram_id = user_id,
#                 who = who,
#                 full_name = title,
#                 class_name = muc, 
#                 school = school,
#                 city = city,
#                 number = num,
#                 language = ru,
#                 un_id = un
#             )
#         else:
#             db.insert(
#                 SAVE_DATA,
#                 telegram_id = user_id,
#                 who = who,
#                 full_name = title,
#                 class_name = muc, 
#                 school = school,
#                 city = city,
#                 number = num,
#                 language = ru
#             )

        # await call.message.bot.send_photo(
        #         chat_id= CHANEL_ID ,  # ID администратора
        #         photo=photo_id,
        #         caption=f"Чек от пользователя <a href='{url}'><b>{title}</b></a>",
        #         reply_markup=button.as_markup()
        # )
#     elif n == 2:
#         doc = data.get('doc')
#         if un_id:
#             un = int(un_id)
#             db.insert(
#                     SAVE_DATA,
#                     telegram_id = user_id,
#                     who = who,
#                     full_name = title,
#                     class_name = muc,
#                     school = school,
#                     city = city,
#                     number = num,
#                     language = ru,
#                     un_id = un
#                 )
#         else:
#             db.insert(
#                     SAVE_DATA,
#                     telegram_id = user_id,
#                     who = who,
#                     full_name = title,
#                     class_name = muc,
#                     school = school,
#                     city = city,
#                     number = num,
#                     language = ru
#                 )

        # await call.message.bot.send_document(
        #     chat_id= CHANEL_ID ,
        #     document=doc,
        #     caption=f"PDF файл от пользователя <a href='{url}'><b>{title}</b></a>",
        #     reply_markup=button.as_markup()
        # )
#     await call.message.answer(test,reply_markup=CreateInline(bt))
#     await call.message.delete()

@user_private_router.callback_query((F.data=='Нет') | (F.data == 'Yoq'))
async def net(call:CallbackQuery,state:FSMContext):
    data = await state.get_data()
    lg = data.get("LG")
    if lg == 'ru':
        test = f'Желаете пройти регистрацию заново?\n Нажмите суда -> /start'
    elif lg == 'uz':
        test = f'Tekshiruv tasdiqlanmadi!!!\nQayta ro\'yxatdan o\'ting -> /start'
    await call.message.answer(test)
    await call.message.delete()

@user_private_router.callback_query((F.data=='Прийти и заплатить') | (F.data == 'Borib tolash'),StateUser.py)
async def py(call:CallbackQuery,state:FSMContext):
    data = await state.get_data()
    num = data.get('num')
    who = data.get('who')
    city = data.get('city')
    title = data.get('title')
    school = data.get('school')
    lg = data.get("LG")
    if lg == 'ru':
        bt = 'Да'
        bt2 = 'Нет'
        test = f'Ваш профиль \n\nwho:{who} \n\nИмя: {title}\n\nКлаасс: {school}\n\nГород: {city}\n\nНомер: {num}\n\nи ваш чек отправить на проверку?'
    elif lg == 'uz':
        bt = 'Ha'
        bt2 = 'Yok'
        test = f'Sizning profilingiz \n\nwho:{who} \n\nIsm: {title}\n\nSnif: {school}\n\nTuman: {city}\n\nTelefon raqam: {num}\n\ntekshirish uchun chekingizni yuboring?'
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
    num = data.get('num')
    who = data.get('who')
    muc = data.get('muc')
    city = data.get('city')
    title = data.get('title')
    school = data.get('school')
    un_id = data.get('un_id')
    py = False
    user_id = call.from_user.id
    print(who,type(who))

    lg = data.get("LG")
    if lg == 'ru':
        n = 2
        ru ='ru'
    elif lg == 'uz':
        n = 1
        ru ='ru'
    if who.strip() == 'tch':
        db.insert(
                TEACHER_MOD,
                telegram_id = user_id,
                full_name = title,
                school = school,
                class_name = muc,
                city = city,
                number = num,
                payment = py,
                language = lg
            )
    elif who.strip() == 'pr':
            db.insert(
                PARENTS_MOD,
                telegram_id = user_id,
                full_name = title,
                school = school,
                class_name = muc,
                city = city,
                number = num,
                payment = py,
                language = lg
            )
    elif who.strip() == 'Tch_a':

        teacher = db.read(
            TEACHER_MOD,
            where_clause=f'telegram_id = {user_id}'
        )

        un = int(un_id)
        teacher_id = teacher[0][0]
        db.insert(
            USERMOD,
            teacher_id = teacher_id,
            telegram_id = un,
            full_name = title,
            school = school,
            city = city,
            number = num,
            payment = py,
            language = lg
        )
    elif who.strip() == 'Pr_a':

        parent = db.read(
            PARENTS_MOD,
            where_clause=f'telegram_id = {user_id}'
        )

        un = int(un_id)
        parent_id = parent[0][0]
        db.insert(
            USERMOD,
            parents_id = parent_id,
            telegram_id = un,
            full_name = title,
            school = school,
            city = city,
            number = num,
            payment = py,
            language = lg
        )
    else:
        db.insert(
            USERMOD, 
            telegram_id=user_id, 
            full_name=title, 
            school=school, 
            city=city, 
            number=str(num), 
            payment=py, 
            language=ru
        )
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