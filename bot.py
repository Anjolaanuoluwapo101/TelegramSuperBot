import telepot
import sqlite3
from telepot.loop import MessageLoop
from telepot.namedtuple import ReplyKeyboardMarkup
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.exception import TelegramError,BotWasKickedError
import json
import time
import requests
from pprint import pprint
from bot_dependency.BotDatabase import BotDatabase


class TelegramBotHandler:
    def __init__(self, token, bot_username):
        self.token = token
        self.base_url = f'https://api.telegram.org/bot{self.token}'
        self.bot = telepot.Bot(self.token)
        self.bot_username = bot_username
        self.db = BotDatabase()  # Initialize the database
        self.db.create_tables()  # Create necessary tables
        
    def get_updates(self):
        """
        Continuously polls for updates from Telegram and processes each one.
        Offset ensures no update is processed more than once.
        """
        offset = None
        while True:
            updates = self.bot.getUpdates(offset=offset, timeout=10)
            for update in updates:
                self.handle_messages(update)
                print('____________________________________')
                offset = update['update_id'] + 1  # Mark update as acknowledged
            time.sleep(10)
            
            # ignore for now...
            # chat_id = -1002497259720  # Replace with the chat ID you want to send the poll to
            # question = "What's 2 + 2?"
            # options = json.dumps(["1", "2", "3", "4"])
            # correct_option_id = 3  # Index of the correct answer

            # self.create_quiz_poll(chat_id, question, options, correct_option_id, is_anonymous=False, allows_multiple_answers=False)


    def handle_messages(self, update):
        """
        Main method for handling incoming messages and events.
        Processes based on update content type (message, my_chat_member, channel_post).
        """
        if 'message' in update:
            try:
                self.output(update, 4)  # Display message in JSON format for debugging
                
                chat_id = update['message']['chat']['id']
                chat_type = update['message']['chat']['type']
                user_id = update['message']['from']['id']
                
                self.get_user_status(chat_id,user_id)
                
                
                if chat_type == 'private':
                    # self.handle_message_with_inline_markup(update['message'])
                    # hanlde new sign up
                    if self.check_key_exists(update,'text'):
                        text = self.check_key_exists(update,'text',True)
                        if text == "/new_user":
                            # create a new entry in the Users table
                            # but first check if the command hasn' been called before
                            user_id = update['message']['from']['id']
                            if self.db.prevent_unnecessary_new_user(user_id) == None:
                                if self.db.add_user(user_id):
                                    self.bot.sendMessage(user_id,'You have been registered successfully')
                                else:
                                    self.bot.sendMessage(user_id,'Error occured while registering you')
                            else:
                                self.bot.sendMessage(user_id,"Already registered.Add Bot to Group(Make Admin) or Channel")
                            # we only need the user id for now
                            
                
                elif 'new_chat_member' in update['message']:
                    self.handle_new_member(update)
                    
                elif 'left_chat_member' in update['message']:
                    self.handle_left_member(update)
                    
                elif self.check_key_exists(update, 'migrate_to_chat_id'):
                    self.handle_group_migration(update)
                    
            except BotWasKickedError:
                print("Bot was kicked from the chat. Handling accordingly.")
                
            except TelegramError as e:
                self.handle_telegram_error(e)
        # handle membership status changes of the bot itself
        elif 'my_chat_member' in update:
            self.handle_member_status(update)
        
        elif 'channel_post' in update:
            self.handle_channel_post(update)
        
        else:
            print("Unhandled update type: ", update)

    def handle_new_member(self, update):
        """
        Handles the event of a new member joining the group.
        Checks if the new member is the bot itself or another user.
        """
        new_member_id = update['message']['new_chat_member']['id']
        new_member_username = update['message']['new_chat_member'].get('username')
        
        if new_member_username == self.bot_username:
            
            print("Hello, I'm a bot. I was just added")
        else:
            mention = f"[@{new_member_username}](tg://user?id={new_member_id})" if new_member_username else f"[thisuser](tg://user?id={new_member_id})"
            print('New member added:', mention)

    def handle_left_member(self, update):
        """
        Handles the event of a member leaving the group.
        Checks if the bot itself or another user has left.
        """
        left_member_id = update['message']['left_chat_member']['id']
        left_member_username = update['message']['left_chat_member'].get('username')
        
        if left_member_username == self.bot_username:
            print("Bot was kicked out")
        else:
            mention = f"[@{left_member_username}](tg://user?id={left_member_id})" if left_member_username else f"[thisuser](tg://user?id={left_member_id})"
            print('Member removed:', mention)

    def handle_group_migration(self, update):
        """
        Handles group-to-supergroup migration and updates chat ID accordingly.
        """
        old_chat_id = update['message']['chat']['id']
        new_chat_id = update['message']['migrate_to_chat_id']
        new_chat_type = 'supergroup'
        print(f"Group migrated to supergroup. Old ID: {old_chat_id}, New ID: {new_chat_id}")

    def handle_telegram_error(self, error):
        """
        Handles general Telegram errors and checks if it's related to group-to-supergroup migration.
        """
        error_data = error.args[2]
        if 'migrate_to_chat_id' in error_data['parameters']:
            new_chat_id = error_data['parameters']['migrate_to_chat_id']
            print(f"Group chat migrated to supergroup. New chat ID: {new_chat_id}")
            self.bot.sendMessage(new_chat_id, "This is a supergroup now!")
        else:
            print(f"Error occurred: {error}")

    def handle_member_status(self, update):
        """
        Handles member status changes, including becoming an admin, member, or leaving.
        Checks if the update is from a channel, group, or supergroup.
        """
        chat_type = update['my_chat_member']['chat']['type']
        user_id = update['my_chat_member']['from']['id']
        chat_id = update['my_chat_member']['chat']['id']
       
        set_permissions = ''
        
        self.output(update, 4)
 
        if chat_type in ['channel', 'group', 'supergroup']:
            my_member_chat = self.check_key_exists(update, 'my_chat_member', True)
             
            if my_member_chat['old_chat_member']['status'] in  ('member','administrator') and my_member_chat['new_chat_member']['status'] in ('left','kicked'):
                print('Kicked from group.....please wait')
                if self.db.remove_user(user_id,chat_id):
                    print('Chat credentials has been cleared from bot')
                else:
                    print('Error clearing chat credentials from bot')
             
            #this if block does not run for channel because bots are automatically added as admins       
            elif my_member_chat['old_chat_member']['status'] in ('left','kicked') and my_member_chat['new_chat_member']['status'] == 'member':
                print('Joined as member.....please wait')
                
                # we need to ensure that a user row(using the /new_user command by messaging the bot itself) has been created first before addition of user rows to Group,Supergroup and Channel tables 
                if self.db.prevent_unnecessary_new_user(user_id) == None:
                    print('Ensure to message bot with /new_user command')
                    self.auto_leave_chat(chat_id)
                    return False 
                
                if chat_type in ('group','supergroup'):
                    # supergroups and groups lack usernames so we use their title as a substitute....
                    chat_username = update['my_chat_member']['chat']['title']
                else:
                     chat_username = update['my_chat_member']['chat']['username']
                # next is to update the User table.
                if self.db.update_user(chat_username,chat_type,chat_id,user_id):
                    # after which we update the supergroup or group table
                    if chat_type == 'supergroup':
                        if self.db.add_supergroup(user_id,chat_username,chat_id):
                            print('Added as a member to this supergroup')
                            set_permissions = True
                    else:
                        if self.db.add_group(user_id,chat_username,chat_id):
                            print('Added a member to tnis group')
                            set_permissions = True
                        # we set permission after
                    if set_permissions:
                        new_chat_member = my_member_chat['new_chat_member']
                        status_and_permissions = {
                            key: value for key, value in new_chat_member.items()
                            if key.startswith("can") or key.startswith("is") or key == "status"
                        }
                        
                        print(status_and_permissions)                    
                        
                        if self.db.set_permissions(user_id,chat_id,chat_type,status_and_permissions) :
                            print('Permissions added!')
                        else:
                            print('Permissions not added!')                           
                    
                    
            # this runs for channels,groups and supergroups  
            elif my_member_chat['old_chat_member']['status'] in ('left','kicked') and my_member_chat['new_chat_member']['status'] == 'administrator':
                print('Promoted to admin......please wait')
               
                # we need to ensure that a user row(using the /new_user command by messaging the bot itself) has been created first before addition of user rows to Group,Supergroup and Channel tables 
                if self.db.prevent_unnecessary_new_user(user_id) == None:
                    print('Ensure to message bot with /new_user command')
                    self.auto_leave_chat(chat_id)
                    return False 
                
                if chat_type in ('group','supergroup','channel'):
                    # supergroups and groups lack usernames so we use their title as a substitute....
                    chat_username = update['my_chat_member']['chat']['title']
                    if chat_type == 'channel':
                        chat_username = update['my_chat_member']['chat']['username']
                    # next is to update the User table.
                    if self.db.update_user(chat_username,chat_type,chat_id,user_id):
                        # after which we update the supergroup or group table
                        if chat_type == 'supergroup':
                            if self.db.add_supergroup(user_id,chat_username,chat_id):
                                print('Added as an admin to this supergroup')
                                set_permissions = True
                        elif chat_type == 'supergroup':
                            if self.db.add_group(user_id,chat_username,chat_id):
                                print('Added as an admin to tnis group')
                                set_permissions = True
                        elif chat_type == 'channel':
                            if self.db.add_channel(user_id,chat_username,chat_id):
                                print('Added as an admin to this channel')
                                set_permissions = True
                                
                        # we set permission after
                        if set_permissions:
                            new_chat_member = my_member_chat['new_chat_member']
                            status_and_permissions = {
                                key: value for key, value in new_chat_member.items()
                                if key.startswith("can") or key.startswith("is") or key == "status"
                            }
                            
                            print(status_and_permissions)                    
                            
                            if self.db.set_permissions(user_id,chat_id,chat_type,status_and_permissions) :
                                print('Permissions added!')
                            else:
                                print('Permissions not added!')                           
                    
            elif my_member_chat['old_chat_member']['status'] in ('administrator','member') and my_member_chat['new_chat_member']['status'] == 'administrator':
                print('Admin permissions modified,another class method will handle this......please wait')
                new_chat_member = my_member_chat['new_chat_member']
                status_and_permissions = {
                    key: value for key, value in new_chat_member.items() 
                    if key.startswith("can") or key.startswith("is") or key == "status"
                }
                identifiers = {
                    'user_id' : user_id,
                    'chat_id' : chat_id
                }
                if self.db.update_permissions('Permissions',identifiers,status_and_permissions) :
                    print('Permissions updated!')
                else:
                    print('Permissions not updated!')
                
                
    
    # def handle_permission_changes(self,update):
    
    def create_quiz_poll(self,chat_id, question, options, correct_option_id=None, is_anonymous=True, allows_multiple_answers=False):
        """
        Create a quiz-style poll in a chat using Telegram's sendPoll API endpoint.
        
        Args:
            chat_id (int): ID of the chat (group/channel) to send the poll to.
            question (str): The question for the poll.
            options (list): A list of answer options for the poll.
            correct_option_id (int, optional): Index of the correct answer for a quiz. Set if creating a quiz.
            is_anonymous (bool): If True, the poll is anonymous.
            allows_multiple_answers (bool): If True, users can select multiple answers.
        """
        payload = {
            'chat_id': chat_id,
            'question': question,
            'options': options,
            'is_anonymous': is_anonymous,
            'type': 'quiz' if correct_option_id is not None else 'regular',
            'allows_multiple_answers': allows_multiple_answers
        }

        # If it's a quiz, add the correct option ID
        if correct_option_id is not None:
            payload['correct_option_id'] = correct_option_id

        self.bot._api_request('sendPoll', payload)


    def handle_channel_post(self, update):
        """
        Processes posts in channels by admins.
        Allows for actions on text posts, photo posts, etc.
        """
        self.output(update, 4)
        
        if 'text' in update['channel_post']:
            if 'reply_to_message' in update['channel_post']:
                print('Reply to text in channel post')
            else:
                print('Text post in channel')
    
    def handle_forwarded_messages(self, message):
        chat_id = message['chat']['id']
        is_forwarded = 'forward_from_chat' in message or 'forward_from' in message
        is_reply = 'reply_to_message' in message

        if is_forwarded:
            if 'forward_from_chat' in message:  # Forwarded from a channel
                origin_title = message['forward_from_chat'].get('title', "Unknown")
                origin_id = message['forward_from_chat'].get('id')
                forwarded_text = message.get('text', "No text provided")
                response = (f"Received a forwarded message from the channel '{origin_title}' (ID: {origin_id}):\n"
                            f"{forwarded_text}")
            elif 'forward_from' in message:  # Forwarded from a user
                sender_user = message['forward_from']
                sender_name = sender_user.get('first_name', "Unknown User")
                sender_username = sender_user.get('username', "No username")
                forwarded_text = message.get('text', "No text provided")
                response = (f"Received a forwarded message from user '{sender_name}' "
                            f"(Username: @{sender_username}):\n{forwarded_text}")
            self.bot.sendMessage(chat_id, response)

        if is_reply and 'reply_to_message' in message:
            original_message = message['reply_to_message']
            if 'is_automatic_forward' in original_message:
                if 'forward_from_chat' in original_message:  # Reply to forwarded channel message
                    origin_title = original_message['forward_from_chat'].get('title', "Unknown")
                    reply_text = message.get('text', "No text provided")
                    response = (f"Received a reply to a forwarded message from the channel '{origin_title}':\n"
                                f"Original: {original_message.get('text', 'No text')}\nReply: {reply_text}")
                elif 'forward_from' in original_message:  # Reply to forwarded user message
                    sender_user = original_message['forward_from']
                    sender_name = sender_user.get('first_name', "Unknown User")
                    reply_text = message.get('text', "No text provided")
                    response = (f"Received a reply to a forwarded message from user '{sender_name}':\n"
                                f"Original: {original_message.get('text', 'No text')}\nReply: {reply_text}")
                self.bot.sendMessage(chat_id, response)
  
    def get_user_status(self, chat_id, user_id):
        """
        Check the status of a user in a specific chat.

        :param chat_id: ID of the chat (group, supergroup, or channel)
        :param user_id: ID of the user to check
        :return: Status of the user (member, administrator, left, etc.) or error message
        """
        url = f'{self.base_url}/getChatMember'
        params = {
            'chat_id': chat_id,
            'user_id': user_id
        }

        try:
            response = requests.get(url, params=params)
            response_data = response.json()

            if response_data.get("ok"):
                print(response_data['result'])
            else:
                return f"Error: {response_data.get('description', 'Unknown error')}"
        except requests.RequestException as e:
            return f"Request failed: {e}"
        
    def handle_message_with_kb_markup(self, msg):
        """
        Handles messages with custom keyboard markup for user choices.
        """
        content_type, chat_type, chat_id = telepot.glance(msg)
        if content_type == 'text' and msg['text'] == '/start':
            keyboard = ReplyKeyboardMarkup(
                keyboard=[['Option1', 'Option2'], ['OptionA', 'OptionB']],
                resize_keyboard=True
            )
            self.bot.sendMessage(chat_id, 'Choose an option:', reply_markup=keyboard)
        else:
            self.bot.sendMessage(chat_id, "You texted...")

    def handle_message_with_inline_markup(self, msg):
        """
        Handles messages with inline markup for user actions.
        """
        content_type, chat_type, chat_id = telepot.glance(msg)
        if content_type == 'text' and msg['text'] == '/start':
            inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Button 1', callback_data='button1')],
                [InlineKeyboardButton(text='Button 2', callback_data='button2')]
            ])
            self.bot.sendMessage(chat_id, "Choose an inline button:", reply_markup=inline_keyboard)
        else:
            self.bot.sendMessage(chat_id, f"You said: {msg['text']}")

    def handle_callback_query(self, msg):
        """
        Handles inline keyboard callback queries.
        """
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
        self.bot.answerCallbackQuery(query_id, text=f"You pressed {query_data}")

    #allows bot to leave chat
    def auto_leave_chat(self,chat_id):
        try:
            self.bot.sendMessage(chat_id,'Bot Says:You need to fufill first step before adding me to any chat!')
            self.bot.leaveChat(chat_id)
            print(f"Bot has successfully left chat {chat_id}")
        except telepot.exception.TelegramError as e:
            print(f"Failed to leave chat {chat_id}: {e}")

    def output(self, data, indent=4):
        """
        Prints the JSON-formatted data for debugging purposes.
        """
        print(json.dumps(data, indent=indent))

    def check_key_exists(self, data, key, get_value=False):
        """
        Recursively checks if a key exists in a dictionary or list and returns its value if requested.
        """
        if isinstance(data, dict):
            if key in data and data[key] is not None:
                return data[key] if get_value else True
            for sub_value in data.values():
                result = self.check_key_exists(sub_value, key, get_value)
                if result:
                    return result
        elif isinstance(data, list):
            for item in data:
                result = self.check_key_exists(item, key, get_value)
                if result:
                    return result
        return None if get_value else False


# Initialize the bot handler and start listening for updates
token = "7548196461:AAFyx8Vm_Y6ijunGg9oSv3A5DuiJTYEoK-A"
bot_handler = TelegramBotHandler(token=token, bot_username="anjola_test_bot")
bot_handler.get_updates()
