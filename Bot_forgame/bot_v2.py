from typing import Final
import telegram
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import pickle
import logging
from telegram import ReplyKeyboardMarkup, KeyboardButton
import emoji
import json
from telegram import ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackContext,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)
class globals:
    level = 'home'
    class send:
        currency = 'none'
        senderHome = 'none'
        reciverHome = 'none'
        amount = 'none'
    
async def send():
    currency = globals.send.currency
    senderHome = globals.send.senderHome
    recieverHome = globals.send.reciverHome
    amount = globals.send.amount
    
    if game_state[senderHome]['resources'][currency] >= amount:
        game_state[senderHome]['resources'][currency] -= amount
        game_state[recieverHome]['resources'][currency] += amount
        response = f'Sent {amount} money from home {senderHome} to home {recieverHome}.'
        await notify_resource_received(context, recieverHome, currency, amount, senderHome)
    else:
        response = f'Not enough money in home {senderHome}.'


    async def notify_resource_received(context: ContextTypes.DEFAULT_TYPE, home: str, resource_type: str, amount: int, sender_home: str):
        # Sends a notification to all players in a home.
        for player_id in game_state[home]['players']:
            try:
                await context.bot.send_message(
                    chat_id=player_id,
                    text=f"Home {sender_home} sent {amount} {resource_type} to your home ({home})!"
                )
            except Exception as e:
                print(f"Failed to send message to {player_id}: {e}")
    return response;
#logging
def setup_logging():
    logging.basicConfig(
        filename='bot_log.txt',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%d-%b-%y %H:%M:%S'
    )
def log_message(message):
    logging.info(message)
def print(message):
    # Call the log_message function to log the message
    log_message(message)
    # Call the original print function to display the message
    __builtins__.print(message)
async def call_keyboard(arg, buttonsPerRow):
    keyboard = []
    row = []
    
    for i, button in enumerate(arg, start=1):
        row.append(KeyboardButton(button))
        if i % buttonsPerRow == 0:
            keyboard.append(row)
            row = []
    
    # Add the last row if it's not empty
    if row:
        keyboard.append(row)

    reply_markup = ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )
    return reply_markup

# Call the setup_logging function to initialize the logging
setup_logging()
TOKEN: Final = '7668282044:AAE7xCzkCa76BmJ0kEQyA_x0B56oSoxs9RY'
BOT_USERNAME: Final = '@dune_death_of_the_emperor_2_bot'
ADMIN_IDS = [934702427, 381252773]
game_state: dict = {}
def check_permissions(user_id: int) -> bool:
    for home in game_state.values():
        if user_id in home['players']:
            return True
    return user_id in ADMIN_IDS
def get_home_by_player(user_id: int) -> str:
    for home in game_state:
        home_state = game_state[home]
        if user_id in home_state["players"]:
            return home
    return "none"

async def home():
    globals.level = 'home'
    return await call_keyboard(['Check My Home', 'Send'], 2)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id
    user_id = update.effective_user.id

    # Create the keyboard

    reply_markup = await home()
    # Send a welcome message with the keyboard
    await update.message.reply_text(
        f'Hi! You are in home {get_home_by_player(user_id)}. Choose an option:',
        reply_markup=reply_markup
    )




async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_message = "Available commands:\n"
    help_message += "/start - Start the bot\n"
    help_message += "/help - Display this help message\n"
    help_message += "/money <amount> <homeName> - Transfer money to another home\n"
    help_message += "/battalions <amount> <homeName> - Transfer battalions to another home\n"
    help_message += "/iic <amount> <homeName> - Transfer IIC to another home\n"
    help_message += "/checkHome - Check your home balance\n\n"
    help_message += "Admin commands:\n"
    help_message += "/give <resource_type> <amount> <homeName> - Give resources to a user's home\n"
    help_message += "/adminCheckHome <homeName> - check values of a home\n"
    help_message += "/marry <homeName1> <homeName2> - Marry two homes\n\n"
    help_message += "Homes and their player IDs:\n\n"

    for home, home_data in game_state.items():
        help_message += f"{home}: Players: {', '.join(map(str, home_data['players']))}\n"

    await update.message.reply_text(help_message)

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("custom")


def handle_response(text: str) -> str:
    processed: str = text.lower()

    if 'hello' in processed:
        return 'Hello back!'
    else: 
        return "i don't understand"


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = None;
    message_type: str = update.message.chat.type
    text: str = update.message.text

    text = update.message.text
    user_id = update.effective_user.id
    if text and get_home_by_player(user_id) == 'none':
        response = "You're not in a home, bot will not work for you"
    if text == 'cancel':
        await update.message.reply_text("Returning to homePage", reply_markup=await home())
    elif globals.level == 'sendmoney':
        if text in game_state:
            await update.message.reply_text("Type in the amount:", reply_markup=ReplyKeyboardRemove())
            globals.send.senderHome = get_home_by_player(user_id)
            globals.send.recieverHome = text
            globals.send.currency = 'money'
            globals.level = 'sending'
        else:
            response = "The home doesn't exist"
    elif globals.level == 'sendbattalions':
        if text in game_state:
            await update.message.reply_text("Type in the amount:", reply_markup=ReplyKeyboardRemove())
            globals.send.senderHome = get_home_by_player(user_id)
            globals.send.recieverHome = text
            globals.send.currency = 'battalions'
            globals.level = 'sending'
        else:
            response = "The home doesn't exist"
    elif globals.level == 'sendiic':
        if text in game_state:
            await update.message.reply_text("Type in the amount:", reply_markup=ReplyKeyboardRemove())
            globals.send.senderHome = get_home_by_player(user_id)
            globals.send.recieverHome = text
            globals.send.currency = 'iic'
            globals.level = 'sending'
        else:
            response = "The home doesn't exist"
    elif globals.level == 'send':
        if text == 'Money':
            globals.level = 'sendmoney'
            await update.message.reply_text("Choose an option:", reply_markup=await call_keyboard(['Atreides', 'Harkonnen', 'home3', 'home4', 'home5', 'home6', 'home7', 'cancel'], 2))
        elif text == 'battalions':
            globals.level = 'sendbattalions'
            await update.message.reply_text("Choose an option:", reply_markup=await call_keyboard(['Atreides', 'Harkonnen', 'home3', 'home4', 'home5', 'home6', 'home7', 'cancel'], 2))
        elif text == 'IIC':
            globals.level = 'sendiic'
            await update.message.reply_text("Choose an option:", reply_markup=await call_keyboard(['Atreides', 'Harkonnen', 'home3', 'home4', 'home5', 'home6', 'home7', 'cancel'], 2))
    elif globals.level == 'home':
        if text == "Send":
            await update.message.reply_text("Choose an option:", reply_markup=await call_keyboard(['Money', 'battalions', 'IIC', 'cancel'], 3))
            globals.level = 'send'
        if text == "Check My Home":

            user_id = update.effective_user.id
            user_home = get_home_by_player(user_id)
            marriedTo = game_state[user_home]['marriedTo']
            marriedHome = game_state[user_home]['marriedTo']

            if not user_home:
                response = 'You are not in a home.'
            elif marriedTo != '':
                response = f'Your balance in home {user_home}\
                    (UserID: {user_id}):\nMoney: {game_state[user_home]['resources']['money']}\
                    \nbattalions: {game_state[user_home]['resources']['battalions']}\
                    \nIIC: {game_state[user_home]['resources']['iic']}\
                    \n\nBalance in your spouses home {marriedHome}\
                    \nMoney: {game_state[marriedHome]['resources']['money']}\
                    \nbattalions: {game_state[marriedHome]['resources']['battalions']}\
                    \nIIC: {game_state[marriedHome]['resources']['iic']}'
            else:
                money = game_state[user_home]['resources']['money']
                battalions = game_state[user_home]['resources']['battalions']
                iic = game_state[user_home]['resources']['iic']
                response = f'Your balance in home {user_home} (UserID: {user_id}):\nMoney: {money}\nbattalions: {battalions}\nIIC: {iic}'
    elif globals.level == 'sending':
        sendingAmount = int(text)
        if text:
            globals.send.amount = sendingAmount
            response = await send()
            await update.message.reply_text("Returning to homepage", reply_markup=await home())
    else:
        await update.message.reply_text("I don't understand", reply_markup=await home())
    

    if response:
        print(f'bot: {response}')
        await update.message.reply_text(response)
    
    # Save the game state
    with open('game_state.json', 'w') as f:
        json.dump(game_state, f, indent=4)



async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {Update} caused error {context.error}')


if __name__ == '__main__':
    print(f'starting bot...')

    try:
        with open('game_state.json', 'r') as f:
            game_state = json.load(f)
    except FileNotFoundError:
        game_state = {
            'Atreides': {
                'players': [7351733890, 922110163, 769938480],
                'resources': {'money': 0, 'battalions': 0, 'iic': 0},
                'name': 'h1',
                'marriedTo': '',
            },
            'Harkonnen': {
                'players': [1180138593, 847845907, 811589178],
                'resources': {'money': 0, 'battalions': 0, 'iic': 0},
                'name': 'h2',
                'marriedTo': '',
            },
            'Corrino': {
                'players': [155024765, 381252773],
                'resources': {'money': 0, 'battalions': 0, 'iic': 0},
                'name': 'h3',
                'marriedTo': '',
            },
            'X': {
                'players': [934702427, 829677341],
                'resources': {'money': 0, 'battalions': 0, 'iic': 0},
                'name': 'h4',
                'marriedTo': '',
            },
            'Moritani': {
                'players': [5627575010, 722601638],
                'resources': {'money': 0, 'battalions': 0, 'iic': 0},
                'name': 'h5',
                'marriedTo': '',
            },
            'Richese': {
                'players': [725715119, 868661320],
                'resources': {'money': 0, 'battalions': 0, 'iic': 0},
                'name': 'h6',
                'marriedTo': '',
            },
            'Guild': {
                'players': [1100684513, 885986887],
                'resources': {'money': 0, 'battalions': 0, 'iic': 0},
                'name': 'h7',
                'marriedTo': '',
            },
            'Orden': {
                'players': [1625779485, 981951982],
                'resources': {'money': 0, 'battalions': 0, 'iic': 0},
                'name': 'h8',
                'marriedTo': '',
            },
            'Taliig': {
                'players': [5979739278, 690839140, 811589178],
                'resources': {'money': 0, 'battalions': 0, 'iic': 0},
                'name': 'h9',
                'marriedTo': '',
            },
            'Fenring': {
                'players': [856362708, 880655046, 1342839027],
                'resources': {'money': 0, 'battalions': 0, 'iic': 0},
                'name': 'h10',
                'marriedTo': '',
            },
            
            # Add more homes as needed
        }
    
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_error_handler(error)

    print('polling...')
    app.run_polling(poll_interval=1)
    # with open('game_state.json', 'w') as f:
    # json.dump(game_state, f, indent=4)

