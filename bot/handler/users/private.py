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
    main = db.read(DESCR,where_clause=f'title_id = {1}')
    save_data = db.read(
        SAVE_DATA,
        where_clause=f'telegram_id = {user_id}'
    )
    student = db.read(
        USERMOD,
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

    if main is not None:
        await message.answer("Ошибка: основная информация отсутствует.")
        return

    if save_data is not None:
        await message.answer('Ваша заявка уже отправлена')

    elif student is not None:
        lg = teacher[0][9]
        if lg == 'ru':
            n = 2
        elif lg == 'uz':
            n = 1
        text = main[0][n]
        await message.answer(
            f'{text}'
        )

    elif teacher is not None:
        lg = main[0][8]
        if lg == 'ru':
            n = 2
        elif lg == 'uz':
            n = 1
        text = main[0][n]
        await state.update_data({'LG':lg})
        await message.answer(
            f'{text}',
            reply_markup=CreateInline(add_std='add students')
        )

    elif parent is not None:
        lg = main[0][8]
        if lg == 'ru':
            n = 2
        elif lg == 'uz':
            n = 1
        text = main[0][n]
        await message.answer(
            f'{text}',
            reply_markup=CreateInline('add Children')
        )

    else:
        text = main[0][1]
        await message.answer(
            f'{text}',
            reply_markup=CreateInline(tch='Teachers',std='Students',pr='Parents')
        )
        await state.set_state(StateUser.who)

@user_private_router.callback_query(F.data=='add_std')
async def std(call:CallbackQuery,state:FSMContext):
    data = await state.get_data()
    lg = data.get('LG')
    if lg == 'ru':
        n = 2
    elif lg == 'uz':
        n = 1
    main = db.read(DESCR,where_clause='title_id = 4')
    des = main[0][n]
    await call.message.answer(
        des,
        reply_markup=CreateBut([p[1] for p in db.read(BUT)],back_ru='Назад')
    )
    await state.set_state(StateUser.school)
    await call.message.delete()

@user_private_router.callback_query(F.data,StateUser.who)
async def tch(call:CallbackQuery,state:FSMContext):
    who = call.data
    user_id = call.from_user.id
    await state.update_data({'who':who,'user_id':user_id})
    await call.message.answer(text='Выберите язык',reply_markup=CreateInline(ru='Ru',uz='Uz'))
    await state.set_state(StateUser.ru)

# ru_start
@user_private_router.callback_query(F.data=='ru',StateUser.ru)
async def cmd_ru(call:CallbackQuery,state:FSMContext):
    await state.update_data({'LG':'ru'})
    main = db.read(DESCR,where_clause='title_id = 4')
    des = main[0][2]
    await call.message.answer(
        des,
        reply_markup=CreateBut([p[1] for p in db.read(BUT)],back_ru='Назад')
    )
    await state.set_state(StateUser.school)
    await call.message.delete()


@user_private_router.callback_query(F.data=='uz',StateUser.ru)
async def cmd_ru(call:CallbackQuery,state:FSMContext):
    await state.update_data({'LG':'uz'})
    main = db.read(DESCR,where_clause='title_id = 4')
    des = main[0][1]
    await call.message.answer(
        des,
        reply_markup=CreateBut([p[2] for p in db.read(BUT)],back_ru='Orqaga')
    )
    await state.set_state(StateUser.school)
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
    await call.message.edit_reply_markup(reply_markup=None)
    await state.set_state(StateUser.comment)

@user_private_router.message(StateUser.comment,F.text)
async def mes1(message:Message,state:FSMContext):
    data = await state.get_data()
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
        text=f'comment from user <a href="{url}"><b>{name}</b></a>:\n{comment}'
    )
    await message.answer(n)
    await state.clear()

@user_private_router.callback_query(F.data=='back_ru',StateUser.school)
async def cmd_ru(call:CallbackQuery,state:FSMContext):
    main = db.read(DESCR,where_clause=f'title_id = {1}')
    text = main[0][1]
    await call.message.answer(
        f'{text}',
        reply_markup=CreateInline(ru='Ru',uz='Uz')
    )
    call.message.edit_reply_markup(reply_markup=None)
    await state.clear()

@user_private_router.callback_query(F.data,StateUser.school)
async def name(call:CallbackQuery,state:FSMContext):
    data = await state.get_data()
    lg = data.get("LG")
    school = call.data
    await state.update_data({'school':school})
    if lg == 'ru':
        n = 2
    elif lg == 'uz':
        n = 1
    main = db.read(DESCR,where_clause='title_id = 8')
    text = main[0][n]
    await call.message.answer(text)
    await state.set_state(StateUser.muc)
    await call.message.delete()

@user_private_router.message(F.text,StateUser.muc)
async def muc(message:Message,state:FSMContext):
    data = await state.get_data()
    lg = data.get("LG")
    muc1 = message.text
    await state.update_data({'muc':muc1})
    if lg == 'ru':
        n = 2
    elif lg == 'uz':
        n = 1
    main = db.read(DESCR,where_clause='title_id = 3')
    text = main[0][n]
    await message.answer(text)
    await state.set_state(StateUser.name)
    await message.delete()

@user_private_router.message(F.text,StateUser.name)
async def name1(message:Message,state:FSMContext):
    data = await state.get_data()
    lg = data.get("LG")
    title = message.text
    await state.update_data({'title':title})
    if lg == 'ru':
        n = 2 
    elif lg == 'uz':
        n = 1
    main = db.read(DESCR,where_clause='title_id = 5')
    city = main[0][n]
    await message.answer(city)
    await state.set_state(StateUser.city)

@user_private_router.message(F.text,StateUser.city)
async def city1(message:Message,state:FSMContext):
    data = await state.get_data()
    lg = data.get("LG")
    city = message.text
    await state.update_data({'city':city})

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
    await message.answer(number,reply_markup=contact_button)
    await state.set_state(StateUser.number)

@user_private_router.message(F.contains,StateUser.number)
async def num(message:Message,state:FSMContext):
    data = await state.get_data()
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
        await state.update_data({'num':num})
        main = db.read(DESCR,where_clause='title_id = 7')
        py = main[0][n]
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

@user_private_router.callback_query((F.data == 'Оплатить Онляйн') | (F.data == 'Onlayn to\'lov'), StateUser.py)
async def py(call:CallbackQuery,state:FSMContext):
    data = await state.get_data()
    lg = data.get("LG")

    if lg == 'ru':
        test = 'Отправьте чек'
    elif lg == 'uz':
        test = 'Tolov Chekini yuboring'
    await call.message.answer(test)
    await state.set_state(StateUser.py1)
    await call.message.delete()

@user_private_router.message(StateUser.py1,MediaFilter())
async def handle_media(message: Message, state: FSMContext):
    data = await state.get_data()
    lg = data.get("LG")
    num = data.get('num')
    city = data.get('city')
    title = data.get('title')
    muc = data.get('muc')
    school = data.get('school')

    if lg == 'ru':
        bt = 'Да'
        bt2 = 'Нет'
        tex = 'Пожалуйста, отправьте Фото или PDF файл.'
        test = f'Ваш профиль \n\nИмя: {title}\n\nШкола: {muc}\n\nКлаасс: {school}\n\nГород: {city}\n\nНомер: {num}\n\nваш чек отправить на проверку?'
    elif lg == 'uz':
        tex = 'Iltimos, fotosurat yoki PDF faylini yuboring.'
        bt = 'Ha'
        bt2 = 'Yok'
        test = f'Sizning profilingiz \n\nIsm: {title}\n\nMaktab: {muc}\n\nSnif: {school}\n\nTuman: {city}\n\nTelefon raqam: {num}\n\ntekshirish uchun chekingizni yuboring?'
    
    if message.content_type == ContentType.PHOTO:

        url = message.from_user.url
        photo_id = message.photo[-1].file_id

        await state.update_data({'photo_id':photo_id,'url':url,'n':1})

        await message.reply(
            text=test,
            reply_markup=CreateInline(bt,bt2)
        )

    elif message.content_type == ContentType.DOCUMENT:
        if message.document.mime_type == 'application/pdf':
            url = message.from_user.url
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
    who = data.get("who")    
    n = data.get('n')
    title = data.get('title')
    user_id = call.from_user.id
    school = data.get('school')
    city = data.get('city')
    num = data.get('num')
    muc = data.get('muc')
    print('vpt:',who)

    button = InlineKeyboardBuilder()
    button.add(InlineKeyboardButton(text='Принять',callback_data=f'Tr_{user_id}'))
    button.add(InlineKeyboardButton(text='Отклонить',callback_data=f'Fr_{user_id}'))
    button.adjust(2)

    if lg == 'ru':
        test = f'Ваш чек отправлено на проверку!'
        bt = 'Оставить комментарий'
        ru = 'ru'
    elif lg == 'uz':
        bt = 'Izoh koldiring'
        ru = 'uz'
        test = f'Chekingiz tekshirish uchun yuborildi!'
    if n == 1:
        photo_id = data.get("photo_id")
        url = data.get('url')

        db.insert(
            SAVE_DATA,
            telegram_id = user_id,
            who = who,
            full_name = title,
            class_name = muc, 
            school = school,
            city = city,
            number = num,
            language = ru
        )

        await call.message.bot.send_photo(
                chat_id= CHANEL_ID ,  # ID администратора
                photo=photo_id,
                caption=f"Чек от пользователя <a href='{url}'><b>{title}</b></a>",
                reply_markup=button.as_markup()
        )
    elif n == 2:
        doc = data.get('doc')
        db.insert(
                SAVE_DATA,
                telegram_id = user_id,
                who = who,
                full_name = title,
                class_name = muc,
                school = school,
                city = city,
                number = num,
                language = ru
            )

        await call.message.bot.send_document(
            chat_id= CHANEL_ID ,
            document=doc,
            caption=f"PDF файл от пользователя <a href='{url}'><b>{title}</b></a>",
            reply_markup=button.as_markup()
        )
    await call.message.answer(test,reply_markup=CreateInline(bt))
    await call.message.edit_reply_markup(reply_markup=None)

@user_private_router.callback_query((F.data=='Нет') | (F.data == 'Yoq'))
async def net(call:CallbackQuery,state:FSMContext):
    data = await state.get_data()
    lg = data.get("LG")
    if lg == 'ru':
        test = f'Желаете пройти регистрацию заново?\n Нажмите суда -> /start'
    elif lg == 'uz':
        test = f'Tekshiruv tasdiqlanmadi!!!\nQayta ro\'yxatdan o\'ting -> /start'
    await call.message.answer(test)
    await call.message.edit_reply_markup(reply_markup=None)

@user_private_router.callback_query((F.data=='Прийти и заплатить') | (F.data == 'Borib tolash'),StateUser.py)
async def py(call:CallbackQuery,state:FSMContext):
    data = await state.get_data()
    num = data.get('num')
    city = data.get('city')
    title = data.get('title')
    school = data.get('school')
    lg = data.get("LG")
    if lg == 'ru':
        bt = 'Да'
        bt2 = 'Нет'
        test = f'Ваш профиль \n\nИмя: {title}\n\nКлаасс: {school}\n\nГород: {city}\n\nНомер: {num}\n\nи ваш чек отправить на проверку?'
    elif lg == 'uz':
        bt = 'Ha'
        bt2 = 'Yok'
        test = f'Sizning profilingiz \n\nIsm: {title}\n\nSnif: {school}\n\nTuman: {city}\n\nTelefon raqam: {num}\n\ntekshirish uchun chekingizni yuboring?'
    await call.message.answer(
        text=test,
        reply_markup=CreateInline(yees=bt,net=bt2)
    )
# ru_end
@user_private_router.callback_query(F.data=='yees')
async def tes(call:CallbackQuery,state:FSMContext):
    data = await state.get_data()
    num = data.get('num')
    city = data.get('city')
    title = data.get('title')
    school = data.get('school')
    py = False
    user_id = call.from_user.id
    lg = data.get("LG")
    if lg == 'ru':
        n = 2
        ru ='ru'
    elif lg == 'uz':
        n = 1
        ru ='ru'
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
    main = db.read(DESCR,where_clause=f'title_id = {1}')
    test = main[0][n]
    await call.message.answer(
        f'{test}'
    )
    await call.message.edit_reply_markup(reply_markup=None)


@user_private_router.callback_query(F.data=='net')
async def net(call:CallbackQuery,state:FSMContext):
    data = await state.get_data()
    lg = data.get("LG")
    if lg == 'ru':
        test = f'Tekshiruv tasdiqlanmadi!!!\nQayta ro\'yxatdan o\'ting -> /start'
    elif lg == 'uz':
        test = f'Желаете пройти регистрацию заново?\n Нажмите суда -> /start'
    await call.message.answer(test)
    await call.message.edit_reply_markup(reply_markup=None)