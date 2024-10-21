import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import ReplyKeyboardMarkup
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.exception import TelegramError,BotWasKickedError
import json
import time
from pprint import pprint


def handle_messages(update):
    if 'message' in update:
        try:
            # Handle normal messages
            output(update,4)
            
            chat_type = update['message']['chat']['type']
            chat_id = update['message']['chat']['id']
            
            if chat_type == 'private':
                TelegramBot.sendMessage(chat_id,"This is a private chat.")
                
            #check if there is a new member added....
            #this only applies to Telegram Groups,Channels arre made to keep the identities of their members safe,so my bot doesn't know
            #when a person is added,remove, made or unmade an admin in a Channel.
            elif 'new_chat_member' in update['message']:
                new_member_id = update['message']['new_chat_member']['id']
                new_member_username = update['message']['new_chat_member'].get('username')
                if new_member_username:
                    mention = f"[@{new_member_username}](tg://user?id={new_member_id})"
                else:
                    mention = f"[thisuser](tg://user?id={new_member_id})"
                TelegramBot.sendMessage(chat_id, f"Welcome,{mention}!.")
                
            else:
                TelegramBot.sendMessage(chat_id, "This is not a private chat.")
                
        except BotWasKickedError:
            print("Bot was kicked from the chat. Handling accordingly.")
            
        except TelegramError as e:
            # Handle the group-to-supergroup migration error....this necessary especially when there's a change in the group..
            # such as new member, new admin,new moderator or the bot was made moderator or admin of sort
            error_data = e.args[2]  # Extract error data from the exception
            if 'migrate_to_chat_id' in error_data['parameters']:
                new_chat_id = error_data['parameters']['migrate_to_chat_id']
                print(f"Group chat was migrated to supergroup. New chat ID: {new_chat_id}")
                
                # Use the new chat ID to send the message
                TelegramBot.sendMessage(new_chat_id, "This is a supergroup now!")
            else:
                # Handle other types of TelegramErrors
                print(f"Error occurred: {e}")
                
    # Handle TelegramBot's  member status updates
    elif 'my_chat_member' in update:
        output(update,4)
        if update['my_chat_member']['chat']['type'] == 'channel':
            # update = json.loads(update)
            if  check_key_exists(update,'new_chat_member'):
                print(check_key_exists(update,'new_chat_member',True))
        # output(update,4)
        # TelegramBot.sendMessage(update['my_chat_member']['chat']['id'], "Bot's status has been updated.")
        #once chat member status is update.....another message is sent to the group or channel "bla bla has joined the gc....something like that"
   
    #handle channel post,usually only admins with privileges can send channel post
    elif 'channel_post' in update:
        output(update,4)
        #code to check if bot has admin acces for modifying channel posts
        
        #gain access to the channel post itself
        #post may be a normal message 
        if 'text' in update['channel_post']:
            #do something to the text...such as check for banned words etc.
            print('text was sent')
            
        #may be a reply to a channel post
        elif 'reply_to_message' in update['channel_post']:
            #do something to a reply to post.....
            print('reply to text')
            
    else:
        # Handle other types of updates or ignore them
        print("Unhandled update type: ", update)


def output(data,i):
    output = json.dumps(data,indent=i)
    print(output)
    
def check_key_exists(data, key, getValue=False):
    if isinstance(data, dict):
        # Check if the key exists and is not empty
        if key in data and data[key] is not None:
            if getValue:
                return data[key]  # Return the value if requested
            else:
                return True  # Return True if key exists
        # Recursively check in nested dictionaries
        for sub_key, sub_value in data.items():
            if isinstance(sub_value, (dict, list)):
                result = check_key_exists(sub_value, key, getValue)
                if result:  # If key is found, stop further checks
                    return result
    elif isinstance(data, list):
        # If it's a list, iterate through the list
        for item in data:
            result = check_key_exists(item, key, getValue)
            if result:  # If key is found, stop further checks
                return result
    return None if getValue else False  # Return False or None if key not found


def handle_message_with_kb_markup(msg):
    content_type,chat_type,chat_id = telepot.glance(msg)
    if content_type == 'text':
        if msg['text'] == '/start':
            #Define the custom keyboard
            keyboard = ReplyKeyboardMarkup(
                keyboard= [
                    ['Option1','Option2'],
                    ['OptionA','OptionB']
                ],
                resize_keyboard = True #resize the keyboard to fit screen size
                
            )
            TelegramBot.sendMessage(chat_id,'choose an option:',reply_markup=keyboard)
        else:
            TelegramBot.sendMessage(chat_id,"You text is.......")
    

def handle_message_with_inline_markup(msg):
    content_type, chat_type, chat_id = telepot.glance(msg, flavor= 'chat')
    
    if content_type == 'text':
        if msg['text'] == '/start':
            # Define the inline keyboard
            inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Button 1', callback_data='button1')], #call back data is link to query_data in handle_callback_query(msg)
                [InlineKeyboardButton(text='Button 2', callback_data='button2')]
            ])
            TelegramBot.sendMessage(chat_id, "Choose an inline button:", reply_markup=inline_keyboard)

        else:
            TelegramBot.sendMessage(chat_id, f"You said: {msg['text']}")




# Handling  callback queries from inline keyboard...receives response from inline keyboards
def handle_callback_query(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')  #they're different message flavors .... chat,callback_query,inline_query
    TelegramBot.answerCallbackQuery(query_id, text=f"You pressed {query_data}")
    


token = "7548196461:AAFyx8Vm_Y6ijunGg9oSv3A5DuiJTYEoK-A"
TelegramBot = telepot.Bot(token)

def get_updates():
    offset = None
    while True:
        updates = TelegramBot.getUpdates(offset=offset, timeout=10)  # Fetch updates
        for update in updates:
            handle_messages(update)  # Process each update
            print('____________________________________')
            print('____________________________________')
            print('____________________________________')
            offset = update['update_id'] + 1  # Acknowledge update to prevent reprocessing
        time.sleep(10) 


get_updates()