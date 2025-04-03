from typing import Final
import telegram
from telegram import _update, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import pickle
import logging
import json


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

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    await update.message.reply_text('Hi!')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_message = "Available commands:\n"
    help_message += "/start - Start the bot\n"
    help_message += "/help - Display this help message\n"
    help_message += "/money <amount> <homeName> - Transfer money to another home\n"
    help_message += "/batallions <amount> <homeName> - Transfer batallions to another home\n"
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
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    if message_type == 'group':
        if BOT_USERNAME in text: 
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
        else:
            return
    else: 
        response: str = handle_response(text)

    async def notification(home, response):
        # Sends a notification to all players in a home.
        for player_id in game_state[home]['players']:
            try:
                await context.bot.send_message(
                    chat_id=player_id,
                    text=response
                )
            except Exception as e:
                print(f"Failed to send message to {player_id}: {e}")

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

    async def send_message(recieverId, message):
        bot = Bot(token=BOT_TOKEN)
        await bot.send_message(chat_id=recieverId, text=message)


    if '/money' in text:
        amount = int(text.split()[1])
        sender_id = update.message.chat.id
        receiver_home = text.split()[2]


        sender_home = get_home_by_player(sender_id)
        if sender_home is None:
            response = 'You are not in a home.'
        elif receiver_home not in game_state:
            response = f'Home {receiver_home} does not exist.'
        elif amount <= 0:
            response = 'Amount must be greater than 0.'
        else:
            if game_state[sender_home]['resources']['money'] >= amount:
                game_state[sender_home]['resources']['money'] -= amount
                game_state[receiver_home]['resources']['money'] += amount
                response = f'Sent {amount} money from home {sender_home} to home {receiver_home}.'
                await notify_resource_received(context, receiver_home, 'money', amount, sender_home)
            else:
                response = f'Not enough money in home {sender_home}.'

    elif '/batallions' in text:
        amount = int(text.split()[1])
        sender_id = update.message.chat.id
        receiver_home = text.split()[2]

        sender_home = get_home_by_player(sender_id)
        if sender_home is None:
            response = 'You are not in a home.'
        elif receiver_home not in game_state:
            response = f'Home {receiver_home} does not exist.'
        elif amount <= 0:
            response = 'Amount must be greater than 0.'
        else:
            if game_state[sender_home]['resources']['batallions'] >= amount:
                game_state[sender_home]['resources']['batallions'] -= amount
                game_state[receiver_home]['resources']['batallions'] += amount
                response = f'Sent {amount} batallions from home {sender_home} to home {receiver_home}.'
                await notify_resource_received(context, receiver_home, 'batallions', amount, sender_home)
            else:
                response = f'Not enough batallions in home {sender_home}.'

    elif '/iic' in text or '/IIC' in text:
        amount = int(text.split()[1])
        sender_id = update.message.chat.id
        receiver_home = text.split()[2]

        sender_home = get_home_by_player(sender_id)
        if sender_home is None:
            response = 'You are not in a home.'
        elif receiver_home not in game_state:
            response = f'Home {receiver_home} does not exist.'
        elif amount <= 0:
            response = 'Amount must be greater than 0.'
        else:
            if game_state[sender_home]['resources']['iic'] >= amount:
                game_state[sender_home]['resources']['iic'] -= amount
                game_state[receiver_home]['resources']['iic'] += amount
                response = f'Sent {amount} IIC from home {sender_home} to home {receiver_home}.'
                await notify_resource_received(context, receiver_home, 'iic', amount, sender_home)
            else:
                response = f'Not enough IIC in home {sender_home}.'
    elif '/adminCheckHome' in text:
        if not check_permissions(update.message.chat.id):
            response = 'You are not an admin.'
        else:
            home = text.split()[1]

            if home not in game_state:
                response = f'Home {home} does not exist.'
            else:
                home_data = game_state[home]
                response = f'Home {home} data:\n'
                response += f'Players: {", ".join(map(str, home_data["players"]))}\n'
                response += f'Money: {home_data["resources"]["money"]}\n'
                response += f'Batallions: {home_data["resources"]["batallions"]}\n'
                response += f'IIC: {home_data["resources"]["iic"]}\n'
                response += f'Married to: {home_data["marriedTo"]}'

    elif '/checkHome' in text or '/checkhome' in text:
        user_id = update.message.chat.id
        user_home = get_home_by_player(user_id)
        marriedTo = game_state[user_home]['marriedTo']
        marriedHome = game_state[user_home]['marriedTo']

        if not user_home:
            response = 'You are not in a home.'
        elif marriedTo != '':
            response = f'Your balance in home {user_home}\
                (UserID: {user_id}):\nMoney: {game_state[user_home]['resources']['money']}\
                \nBatallions: {game_state[user_home]['resources']['batallions']}\
                \nIIC: {game_state[user_home]['resources']['iic']}\
                \n\nBalance in your spouses home {marriedHome}\
                \nMoney: {game_state[marriedHome]['resources']['money']}\
                \nBatallions: {game_state[marriedHome]['resources']['batallions']}\
                \nIIC: {game_state[marriedHome]['resources']['iic']}'
        else:
            money = game_state[user_home]['resources']['money']
            batallions = game_state[user_home]['resources']['batallions']
            iic = game_state[user_home]['resources']['iic']
            response = f'Your balance in home {user_home} (UserID: {user_id}):\nMoney: {money}\nBatallions: {batallions}\nIIC: {iic}'

    elif '/test' in text:
        user_id = update.message.chat.id
        response = f'home: {game_state[get_home_by_player(user_id)]}'
    elif '/give' in text:
        if not check_permissions(update.message.chat.id):
            response = 'You are not an admin.'
        else:
            command_parts = text.split()
            if len(command_parts) != 4:
                response = 'Invalid command format. Use: /give <resource_type> <amount> <homeName>'
            else:
                resource_type = command_parts[1]
                amount = int(command_parts[2])
                receiver_home = command_parts[3]

                if resource_type not in ['money', 'batallions', 'iic']:
                    response = 'Invalid resource type. Use "money", "batallions", or "iic".'
                elif receiver_home not in game_state:
                    response = f'Home {receiver_home} does not exist.'
                else:
                    if resource_type == 'money':
                        game_state[receiver_home]['resources']['money'] += amount
                        response = f'Gave {amount} money to home {receiver_home}.'
                        await notify_resource_received(context, receiver_home, 'money', amount, 'Admin')
                    elif resource_type == 'batallions':
                        game_state[receiver_home]['resources']['batallions'] += amount
                        response = f'Gave {amount} batallions to home {receiver_home}.'
                        await notify_resource_received(context, receiver_home, 'batallions', amount, 'Admin')
                    elif resource_type == 'iic':
                        game_state[receiver_home]['resources']['iic'] += amount
                        response = f'Gave {amount} IIC to home {receiver_home}.'
                        await notify_resource_received(context, receiver_home, 'iic', amount, 'Admin')
    elif '/marry' in text or '/Marry' in text:
        home1 = text.split()[1]
        home2 = text.split()[2]
        if not check_permissions(update.message.chat.id):
            response = 'You are not an admin.'
        elif home1 not in game_state or home2 not in game_state:
            response = 'Invalid home name(-s).'
        elif game_state[home1]['marriedTo'] != '':
            response = '{home1} is already married'
        elif game_state[home2]['marriedTo'] != '':
            response = '{home2} is already married'
        else: 
            game_state[home1]['marriedTo'] = home2
            game_state[home2]['marriedTo'] = home1
            await notification(home1, f'{home1} and {home2} have been married.')
            await notification(home2, f'{home2} and {home1} have been married.')
            response = f'{home1} and {home2} have been married.'

    else:
        response = 'Invalid command.'

    print(f'bot:, {response}')
    await update.message.reply_text(response)
    # if response4reciever:
    #     await update.message.receiver_id.reply_text(response4reciever)
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
                'resources': {'money': 0, 'batallions': 0, 'iic': 0},
                'name': 'h1',
                'marriedTo': '',
            },
            'Harkonnen': {
                'players': [1180138593, 847845907],
                'resources': {'money': 0, 'batallions': 0, 'iic': 0},
                'name': 'h2',
                'marriedTo': '',
            },
            'Corrino': {
                'players': [155024765, 381252773],
                'resources': {'money': 0, 'batallions': 0, 'iic': 0},
                'name': 'h3',
                'marriedTo': '',
            },
            'X': {
                'players': [934702427, 829677341],
                'resources': {'money': 0, 'batallions': 0, 'iic': 0},
                'name': 'h4',
                'marriedTo': '',
            },
            'Moritani': {
                'players': [5627575010, 722601638],
                'resources': {'money': 0, 'batallions': 0, 'iic': 0},
                'name': 'h5',
                'marriedTo': '',
            },
            'Richese': {
                'players': [725715119, 868661320],
                'resources': {'money': 0, 'batallions': 0, 'iic': 0},
                'name': 'h6',
                'marriedTo': '',
            },
            'Guild': {
                'players': [1100684513, 885986887],
                'resources': {'money': 0, 'batallions': 0, 'iic': 0},
                'name': 'h7',
                'marriedTo': '',
            },
            'Orden': {
                'players': [1625779485, 981951982],
                'resources': {'money': 0, 'batallions': 0, 'iic': 0},
                'name': 'h8',
                'marriedTo': '',
            },
            'Taliig': {
                'players': [5979739278, 690839140],
                'resources': {'money': 0, 'batallions': 0, 'iic': 0},
                'name': 'h9',
                'marriedTo': '',
            },
            'Fenring': {
                'players': [856362708, 880655046],
                'resources': {'money': 0, 'batallions': 0, 'iic': 0},
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
    app.run_polling(poll_interval=5)
    # with open('game_state.json', 'w') as f:
    # json.dump(game_state, f, indent=4)
