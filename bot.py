import telepot
import sqlite3
from telepot.loop import MessageLoop
from telepot.namedtuple import ReplyKeyboardMarkup
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.exception import TelegramError,BotWasKickedError
import json
import time
from pprint import pprint

BOT_USERNAME = 'anjola_test_bot'

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
            #this only applies to Telegram Groups,Channels are made to keep the identities of their members safe,so my bot doesn't know
            #when a person is added,remove, made or unmade an admin in a Channel.
            elif 'new_chat_member' in update['message']:
                new_member_id = update['message']['new_chat_member']['id']
                new_member_username = update['message']['new_chat_member'].get('username')
                # check if it is the bot that was added
                if new_member_username == BOT_USERNAME:
                    print('Hello,I\'m a bot.I was just added')
                # if not then,it is another member
                elif new_member_username:
                    mention = f"[@{new_member_username}](tg://user?id={new_member_id})"
                    print('new member added')
                else:
                    mention = f"[thisuser](tg://user?id={new_member_id})"
                    print('new member added')
            # if a mwember or bot leaves a group
            elif 'left_chat_member' in update['message']:
                left_member_id = update['message']['left_chat_member']['id']
                left_member_username = update['message']['left_chat_member'].get('username')
                # confirm if it was bot that was kicked out
                if left_member_username == BOT_USERNAME:
                    print('Bot was kicked out')
                # if not then,it is another member
                elif left_member_username:
                    mention = f"[@{left_member_username}](tg://user?id={left_member_id})"
                    print('member removed')
                else:
                    mention = f"[thisuser](tg://user?id={left_member_id})"
                    print('member removed')
            # this means group is becoming a super group and both the chat type and group id need to be update
            elif check_key_exists(update,'migrate_to_chat_id'):
                old_chat_id = update['message']['chat']['id']
                new_chat_id = update['message']['migrate_to_chat_id']
                new_chat_type = 'supergroup'
                # do something.......
            # elif update['message']['chat']['type'] == 'supergroup' and 
                
                
                
                
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
        # in a channel
        if update['my_chat_member']['chat']['type'] == 'channel':
            if  check_key_exists(update,'my_chat_member'):
                new_member_chat = check_key_exists(update,'my_chat_member',True)
                #handle removal from group
                if new_member_chat['old_chat_member']['status'] == 'member' and new_member_chat['new_chat_member']['status'] == 'left':
                    print('kicked')
                #handle becoming a member in a group
                elif  new_member_chat['old_chat_member']['status'] == 'left' and new_member_chat['new_chat_member']['status'] == 'member' :
                    print('member')
                #handle becoming an admin
                elif  new_member_chat['old_chat_member']['status'] == 'left' and new_member_chat['new_chat_member']['status'] == 'administrator':
                    print('admin')
                #in this case,the bot admin permissions has been changed so do something about it.
                elif new_member_chat['old_chat_member']['status'] == 'administrator' and new_member_chat['new_chat_member']['status'] == 'administrator':
                    print('modified permission')
        # in a group
        elif update['my_chat_member']['chat']['type'] == 'group':
            output(update,4)
            if  check_key_exists(update,'my_chat_member'):
                new_member_chat = check_key_exists(update,'my_chat_member',True)
                #handle removal from group
                if new_member_chat['old_chat_member']['status'] == 'member' and new_member_chat['new_chat_member']['status'] == 'left':
                    print('kicked')
                #handle becoming a member in a group
                elif  new_member_chat['old_chat_member']['status'] == 'left' and new_member_chat['new_chat_member']['status'] == 'member' :
                    print('member')
                #handle becoming an admin
                elif  new_member_chat['old_chat_member']['status'] == 'left' and new_member_chat['new_chat_member']['status'] == 'administrator':
                    print('admin')
                #in this case,the bot admin permissions has been changed so do something about it.
                elif new_member_chat['old_chat_member']['status'] == 'administrator' and new_member_chat['new_chat_member']['status'] == 'administrator':
                    print('modified permission')
        elif update['my_chat_member']['chat']['type'] == 'supergroup':
            print('supergrrrrppppppp')
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
            #may be a reply to a channel post so we check that.
            if 'reply_to_message' in update['channel_post']:
                #do something to a reply to post.....
                print('reply to text')
            else:
                #do something to the text...such as check for banned words etc.
                print('text was sent')
        # if 'photo' in update['channel_post']:
            # handle photos....and so on like that
            
        
            
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