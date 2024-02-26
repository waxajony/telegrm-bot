from aiogram.fsm.state import State, StatesGroup


class ClientAdsStates(StatesGroup):
    selectAdCategory = State()
    selectAdProduct = State()
    insertTitle = State()
    insertText = State()
    insertPrice = State()
    insertImages = State()
    insertPhone = State()

    showAllAds = State()

class SearchAds(StatesGroup):
    ads_name = State()
    ads_btn = State()
