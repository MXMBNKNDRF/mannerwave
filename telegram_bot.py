from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
import requests
from bs4 import BeautifulSoup

# Ваши функции для получения данных о скидках
def get_steam_discounts():
    url = "https://store.steampowered.com/api/featuredcategories"
    response = requests.get(url)
    data = response.json()
    discounts = data.get('specials', {}).get('items', [])
    results = []
    for item in discounts:
        game = {
            "title": item['name'],
            "price": item['final_price'] / 100,
            "link": f"https://store.steampowered.com/app/{item['id']}",
            "image": item['header_image']
        }
        results.append(game)
    return results

def get_epic_discounts():
    url = "https://www.epicgames.com/store/en-US/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    discounts = []
    
    for game in soup.select('.css-1myhtyb'):
        title = game.select_one('.css-1vljfa4').text
        price = game.select_one('.css-0').text if game.select_one('.css-0') else "Free"
        link = "https://www.epicgames.com" + game.select_one('a')['href']
        image = game.select_one('img')['src']
        discounts.append({"title": title, "price": price, "link": link, "image": image})
    
    return discounts

# Команды бота
def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [
            InlineKeyboardButton("Steam", callback_data='steam'),
            InlineKeyboardButton("Epic Store", callback_data='epic'),
            InlineKeyboardButton("Оба магазина", callback_data='both')
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Выберите магазин для получения уведомлений о скидках:', reply_markup=reply_markup)

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    choice = query.data
    user_id = query.from_user.id

    context.user_data['choice'] = choice
    query.edit_message_text(text=f"Вы выбрали: {choice}")

    send_discounts(context, user_id, choice)

def send_discounts(context: CallbackContext, user_id: int, choice: str) -> None:
    if choice == 'steam':
        discounts = get_steam_discounts()
    elif choice == 'epic':
        discounts = get_epic_discounts()
    elif choice == 'both':
        discounts = get_steam_discounts() + get_epic_discounts()

    for discount in discounts:
        context.bot.send_photo(
            chat_id=user_id,
            photo=discount['image'],
            caption=f"{discount['title']}\nЦена: {discount['price']}\n[Ссылка]({discount['link']})",
            parse_mode='Markdown'
        )

def main() -> None:
    updater = Updater("TELEGRAM_API_KEY")

    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
