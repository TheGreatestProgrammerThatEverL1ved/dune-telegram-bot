from typing import Final
import telegram
from telegram import _update, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import pickle

TOKEN: Final = '7668282044:AAE7xCzkCa76BmJ0kEQyA_x0B56oSoxs9RY'
BOT_USERNAME: Final = '@dune_death_of_the_emperor_2_bot'

ADMIN_IDS = [934702427]
game_state: dict = {
    'home1': {
        'players': [934702427],
        'resources': {'money': 0, 'batallions': 0, 'iic': 0},
        'name': 'h1',
    },
    'home2': {
        'players': [1048394283],
        'resources': {'money': 0, 'batallions': 0, 'iic': 0},
        'name': 'h2',
    },
    # Add more homes as needed
}

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
        # return home_state.name
        # if user_id in home_state["players"].values():
        #     return home
    return "none"

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    await update.message.reply_text('Hi!')



# ... (Rest of the code)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_message = "Available commands:\n"
    help_message += "/start - Start the bot\n"
    help_message += "/help - Display this help message\n"
    help_message += "/custom - Execute a custom command\n"
    help_message += "/money <amount> <home_name> - Transfer money to another home\n"
    help_message += "/batallions <amount> <home_name> - Transfer batallions to another home\n"
    help_message += "/iic <amount> <home_name> - Transfer IIC to another home\n"
    help_message += "/checkHome - Check your home balance\n"
    help_message += "/give <resource_type> <amount> <user_id> - Give resources to a user\n"
    help_message += "/homes - Display home names and their player IDs\n"
    help_message += "\nHomes and their player IDs:\n"

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

    if '/money' in text:
        amount = int(text.split()[1])
        sender_id = update.message.chat.id
        receiver_home = text.split()[2]

        sender_home = get_home_by_player(sender_id)
        if sender_home is None:
            response = 'You are not in a home.'
        elif receiver_home not in game_state:
            response = f'Home {receiver_home} does not exist.'
        else:
            if game_state[sender_home]['resources']['money'] >= amount:
                game_state[sender_home]['resources']['money'] -= amount
                game_state[receiver_home]['resources']['money'] += amount
                response = f'Sent {amount} money from home {sender_home} to home {receiver_home}.'
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
        else:
            if game_state[sender_home]['resources']['batallions'] >= amount:
                game_state[sender_home]['resources']['batallions'] -= amount
                game_state[receiver_home]['resources']['batallions'] += amount
                response = f'Sent {amount} batallions from home {sender_home} to home {receiver_home}.'
            else:
                response = f'Not enough batallions in home {sender_home}.'

    elif '/iic' in text:
        amount = int(text.split()[1])
        sender_id = update.message.chat.id
        receiver_home = text.split()[2]

        sender_home = get_home_by_player(sender_id)
        if sender_home is None:
            response = 'You are not in a home.'
        elif receiver_home not in game_state:
            response = f'Home {receiver_home} does not exist.'
        else:
            if game_state[sender_home]['resources']['iic'] >= amount:
                game_state[sender_home]['resources']['iic'] -= amount
                game_state[receiver_home]['resources']['iic'] += amount
                response = f'Sent {amount} IIC from home {sender_home} to home {receiver_home}.'
            else:
                response = f'Not enough IIC in home {sender_home}.'

    elif '/checkHome' in text:
        user_id = update.message.chat.id
        user_home = get_home_by_player(user_id)

        if not user_home:
            response = 'You are not in a home.'
        else:
            money = game_state[user_home]['resources']['money']
            batallions = game_state[user_home]['resources']['batallions']
            iic = game_state[user_home]['resources']['iic']
            response = f'Your balance in home {user_home} (UserID: {user_id}):\nMoney: {money}\nBatallions: {batallions}\nIIC: {iic}'

    elif '/test' in text:
        user_id = update.message.chat.id
        response = get_home_by_player(1048394283)
    elif '/give' in text:
        if not check_permissions(update.message.chat.id):
            response = 'You are not an admin.'
        else:
            resource_type = text.split()[1]
            amount = int(text.split()[2])
            sender_id = update.message.chat.id
            receiver_id = int(text.split()[3])

            sender_home = get_home_by_player(sender_id)
            receiver_home = get_home_by_player(receiver_id)

            if sender_home is None:
                response = 'You are not in a home.'
            elif not receiver_home:
                response = f'User {receiver_id} is not in a home.'
            elif resource_type == 'money':
                # if game_state[sender_home]['resources']['money'] >= amount:
                    # game_state[sender_home]['resources']['money'] -= amount
                    game_state[receiver_home]['resources']['money'] += amount
                    response = f'Gave {amount} money from home {sender_home} to user {receiver_id}.'
                # else:
                #     response = f'Not enough money in home {sender_home}.'
            elif resource_type == 'batallions':
                # if game_state[sender_home]['resources']['batallions'] >= amount:
                #     game_state[sender_home]['resources']['batallions'] -= amount
                    game_state[receiver_home]['resources']['batallions'] += amount
                    response = f'Gave {amount} batallions from home {sender_home} to user {receiver_id}.'
                # else:
                #     response = f'Not enough batallions in home {sender_home}.'
            elif resource_type == 'iic':
                # if game_state[sender_home]['resources']['iic'] >= amount:
                #     game_state[sender_home]['resources']['iic'] -= amount
                    game_state[receiver_home]['resources']['iic'] += amount
                    response = f'Gave {amount} IIC from home {sender_home} to user {receiver_id}.'
                # else:
                #     response = f'Not enough IIC in home {sender_home}.'
            else:
                response = 'Invalid resource type. Use "money", "batallions", or "iic".'

    else:
        response = 'Invalid command.'

    print('bot:', response)
    await update.message.reply_text(response)

    with open('game_state.pkl', 'wb') as f:
        pickle.dump(game_state, f)



async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {Update} caused error {context.error}')


if __name__ == '__main__':
    print(f'starting bot...')

    try:
        with open('game_state.pkl', 'rb') as f:
            game_state = pickle.load(f)
    except FileNotFoundError:
        game_state = {
            'home1': {
                'players': [934702427],
                'resources': {'money': 0, 'batallions': 0, 'iic': 0},
                'name': 'h1',
            },
            'home2': {
                'players': [1048394283],
                'resources': {'money': 0, 'batallions': 0, 'iic': 0},
                'name': 'h2',
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
