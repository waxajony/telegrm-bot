from time import time

from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.filters import CommandStart, Command

#-------------------------##
from fuzzywuzzy import fuzz#
#-------------------------##

from config import DB_NAME, admins
from keyboards.client_inline_keyboards import get_category_list, get_product_list, left_right_k, ads_10
from states.client_states import ClientAdsStates, SearchAds
from utils.database import Database

ads_router = Router()
db = Database(DB_NAME)


@ads_router.message(Command('new_ad'))
async def new_ad_handler(message: Message, state: FSMContext):
    await state.set_state(ClientAdsStates.selectAdCategory)
    await message.answer(
        "Please, choose a category for your ad: ",
        reply_markup=get_category_list()
    )


@ads_router.callback_query(ClientAdsStates.selectAdCategory)
async def select_ad_category(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ClientAdsStates.selectAdProduct)
    await callback.message.edit_text(
        "Please, choose a product type for your ad: ",
        reply_markup=get_product_list(int(callback.data))
    )


@ads_router.callback_query(ClientAdsStates.selectAdProduct)
async def select_ad_product(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ClientAdsStates.insertTitle)
    await state.update_data(ad_product=callback.data)
    await callback.message.answer(
        f"Please, send title for your ad!\n\n"
        f"For example:"
        f"\n\t- iPhone 15 Pro Max 8/256 is on sale"
        f"\n\t- Macbook Pro 13\" M1 8/256 is on sale"
    )
    await callback.message.delete()


@ads_router.message(ClientAdsStates.insertTitle)
async def ad_title_handler(message: Message, state: FSMContext):
    await state.update_data(ad_title=message.text)
    await state.set_state(ClientAdsStates.insertText)
    await message.answer("OK, please, send text(full description) for your ad.")


@ads_router.message(ClientAdsStates.insertText)
async def ad_text_handler(message: Message, state: FSMContext):
    await state.update_data(ad_text=message.text)
    await state.set_state(ClientAdsStates.insertPrice)
    await message.answer("OK, please, send price for your ad (only digits).")


@ads_router.message(ClientAdsStates.insertPrice)
async def ad_price_handler(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(ad_price=int(message.text))
        await state.set_state(ClientAdsStates.insertImages)
        await message.answer("OK, please, send image(s) for your ad.")
    else:
        await message.answer("Please, send only number...")


@ads_router.message(ClientAdsStates.insertImages)
async def ad_photo_handler(message: Message, state: FSMContext):
    if message.photo:
        await state.update_data(ad_photo=message.photo[-1].file_id)
        await state.set_state(ClientAdsStates.insertPhone)
        await message.answer("OK, please, send phone number for contact with your.")
    else:
        await message.answer("Please, send image(s)...")


@ads_router.message(ClientAdsStates.insertPhone)
async def ad_phone_handler(message: Message, state: FSMContext):
    await state.update_data(ad_phone=message.text)
    all_data = await state.get_data()
    try:
        x = db.insert_ad(
            title=all_data.get('ad_title'),
            text=all_data.get('ad_text'),
            price=all_data.get('ad_price'),
            image=all_data.get('ad_photo'),
            phone=all_data.get('ad_phone'),
            u_id=message.from_user.id,
            prod_id=all_data.get('ad_product'),
            date=time()
        )
        if x:
            await state.clear()
            await message.answer("Your ad successfully added!")
        else:
            await message.answer("Something error, please, try again later...")
    except:
        await message.answer("Resend phone please...")


@ads_router.message(Command('ads'))
async def all_ads_handler(message: Message, state: FSMContext):
    all_ads = db.get_my_ads(message.from_user.id)
    if len(all_ads) == 0:
        await message.answer("You've no any ads")
    elif len(all_ads) == 1:
        await message.answer_photo(
            photo=all_ads[0][4],
            caption=f"<b>{all_ads[0][1]}</b>\n\n{all_ads[0][2]}\n\nPrice: ${all_ads[0][3]}",
            parse_mode=ParseMode.HTML
        )
    else:
        await state.set_state(ClientAdsStates.showAllAds)
        await state.update_data(all_ads=all_ads)
        await state.update_data(index=0)
        await message.answer_photo(
            photo=all_ads[0][4],
            caption=f"<b>{all_ads[0][1]}</b>\n\n{all_ads[0][2]}\n\nPrice: ${all_ads[0][3]}\n\n Ad 1 from {len(all_ads)}.",
            parse_mode=ParseMode.HTML,
            reply_markup=left_right_k
        )


@ads_router.callback_query(ClientAdsStates.showAllAds)
async def show_all_ads_handler(callback: CallbackQuery, state: FSMContext):
    all_data = await state.get_data()
    index = all_data.get('index', None)
    all_ads = all_data.get('all_ads', None)

    if callback.data == 'right':
        if index == len(all_ads)-1:
            index = 0
        else:
            index = index + 1
        await state.update_data(index=index)

        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=all_ads[index][4],
                caption=f"<b>{all_ads[index][1]}</b>\n\n{all_ads[index][2]}\n\nPrice: ${all_ads[index][3]}\n\n Ad {index+1} from {len(all_ads)}.",
                parse_mode=ParseMode.HTML
            ),
            reply_markup=left_right_k
        )
    else:
        if index == 0:
            index = len(all_ads) - 1
        else:
            index = index - 1

        await state.update_data(index=index)

        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=all_ads[index][4],
                caption=f"<b>{all_ads[index][1]}</b>\n\n{all_ads[index][2]}\n\nPrice: ${all_ads[index][3]}\n\n Ad {index+1} from {len(all_ads)}.",
                parse_mode=ParseMode.HTML
            ),
            reply_markup=left_right_k
        )



# SEARCH ADS

@ads_router.message(Command('search_ads'))
async def search_ads(message: Message, state: FSMContext):
    await message.answer('Qidirmoqchi bo`lgan elonni nomini yuboring!')
    await state.set_state(SearchAds.ads_name)

@ads_router.message(SearchAds.ads_name)
async def get_ads_name(message: Message, state: FSMContext):
    ads_name = message.text
    date_len = len(db.get_ads_all())
    ads_id_list = []
    await state.update_data(ads_name=ads_name)
    if date_len == 0:
        await message.answer('NONE')
        await state.clear()
    else:
        for n in range(date_len):
            
            similarity_ratio = fuzz.ratio(db.get_ads_all()[n][1], ads_name)
            
            if similarity_ratio > 50:
                ads_id_list.append(int(db.get_ads_all()[n][0]))

        msg = ''
        
        n = 1
        for ads_id in ads_id_list:
            msg += f"{n}. {db.get_ads_one(ads_id)[1]}\n"
            n += 1
        await message.answer(msg, reply_markup=ads_10)
    await state.set_state(SearchAds.ads_btn)

@ads_router.callback_query(SearchAds.ads_btn)
async def show_all_ads_handler(callback: CallbackQuery, state: FSMContext):
    ads_data = await state.get_data()
    ads_name = ads_data.get('ads_name')

    date_len = len(db.get_ads_all())
    ads_id_list = []
    await state.update_data(ads_name=ads_name)
    if date_len == 0:
        await callback.message.answer('NONE')
        await state.clear()
    else:
        for n in range(date_len):
            
            similarity_ratio = fuzz.ratio(db.get_ads_all()[n][1], ads_name)
            
            if similarity_ratio > 50:
                ads_id_list.append(int(db.get_ads_all()[n][0]))
   
    try:
        ads_id = ads_id_list[int(callback.data)-1]

        ads_info = db.get_ads_one(ads_id)
        ads_caption = f"Nomi: {ads_info[1]}\nMalumot: {ads_info[2]}\nNarxi: {ads_info[3]}\nTEL: {ads_info[5]}"
        await callback.message.answer_photo(photo=db.get_ads_one(ads_id)[4], caption=ads_caption)
    except IndexError:
        await callback.message.answer(f"Qidiruv natijasi: {len(ads_id_list)} ta e'lon")