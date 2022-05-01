# coding=utf-8


from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


admin_keyboard = InlineKeyboardMarkup()

menu_back_button = InlineKeyboardButton("Вернуться в меню", callback_data="back_menu")
del_good_button = InlineKeyboardButton("Удалить товар", callback_data="admin_goods_del")
del_gift_button = InlineKeyboardButton("Удалить раздачу", callback_data="admin_gift_del")
add_good_button = InlineKeyboardButton("Добавить товар", callback_data="admin_goods_add")
del_city_button = InlineKeyboardButton("Удалить город", callback_data="admin_cities_del")
add_city_button = InlineKeyboardButton("Добавить город", callback_data="admin_cities_add")
get_gift_button = InlineKeyboardButton("Посмотреть раздачу", callback_data="admin_gift_get")
show_goods_button = InlineKeyboardButton("Посмотреть товары", callback_data="admin_goods_show")
change_good_button = InlineKeyboardButton("Изменить товар", callback_data="admin_goods_change")
get_cities_button = InlineKeyboardButton("Посмотреть города", callback_data="admin_cities_get")
del_profile_button = InlineKeyboardButton("Удалить профиль", callback_data="admin_profile_del")
update_gift_button = InlineKeyboardButton("Обновить раздачу", callback_data="admin_gift_update")
del_mailing_button = InlineKeyboardButton("Удалить рассылку", callback_data="admin_mailing_del")
get_profile_button = InlineKeyboardButton("Посмотреть профиль", callback_data="admin_profile_get")
get_mailing_button = InlineKeyboardButton("Посмотреть рассылку", callback_data="admin_mailing_get")
start_mailing_button = InlineKeyboardButton("Начать рассылку", callback_data="admin_mailing_start")
get_payments_button = InlineKeyboardButton("Посмотреть платежи", callback_data="admin_payments_get")
change_profile_button = InlineKeyboardButton("Изменить профиль", callback_data="admin_profile_change")
update_mailing_button = InlineKeyboardButton("Обновить рассылку", callback_data="admin_mailing_update")
get_payments_date_button = InlineKeyboardButton("Платежи по дате", callback_data="admin_payments_date_get")
get_payments_period_button = InlineKeyboardButton("Платежи по периоду", callback_data="admin_payments_period_get")

admin_keyboard.add(show_goods_button).add(change_good_button).add(add_good_button, del_good_button).add(
    get_gift_button
).add(update_gift_button, del_gift_button).add(get_cities_button).add(add_city_button, del_city_button).add(
    get_mailing_button
).add(start_mailing_button).add(update_mailing_button, del_mailing_button).add(
    get_profile_button
).add(change_profile_button, del_profile_button).add(get_payments_button).add(
    get_payments_date_button, get_payments_period_button
).add(menu_back_button)
