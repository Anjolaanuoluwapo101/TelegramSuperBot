import sqlite3

class BotDatabase:
    def __init__(self, db_name='database/bot_management.db'):
        self.db_name = db_name
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.conn.execute("PRAGMA foreign_keys = ON;")
            self.cursor = self.conn.cursor()
            
        except sqlite3.Error as e:
            print("Database connection error:", e)
        
    def create_tables(self):
        try:
            # Create Users table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS Users (
                    user_id INTEGER NOT NULL,
                    chat_username TEXT UNIQUE DEFAULT NULL,
                    chat_type TEXT DEFAULT NULL,
                    chat_id INTEGER UNIQUE DEFAULT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Create Groups table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS Groups (
                    user_id INTEGER NOT NULL,
                    group_name TEXT NOT NULL,
                    chat_id INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, chat_id),
                    FOREIGN KEY (chat_id) REFERENCES Users(chat_id) ON DELETE CASCADE
                )
            ''')
            
             # Create Super Groups table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS Supergroups (
                    user_id INTEGER NOT NULL,
                    supergroup_name TEXT NOT NULL,
                    chat_id INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, chat_id),
                    FOREIGN KEY (chat_id) REFERENCES Users(chat_id) ON DELETE CASCADE
                )
            ''')

            # Create Channels table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS Channels (
                    user_id INTEGER NOT NULL,
                    channel_name TEXT NOT NULL,
                    chat_id INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, chat_id),
                    FOREIGN KEY (chat_id) REFERENCES Users(chat_id) ON DELETE CASCADE
                )
            ''')

            # Create Permissions table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS Permissions (
                    user_id INTEGER NOT NULL,
                    chat_id INTEGER NOT NULL,
                    chat_type TEXT NOT NULL CHECK(chat_type IN ('group', 'channel','supergroup')),
                    status TEXT NOT NULL CHECK(status IN ('member','administrator','left','kicked')),
                    can_be_edited BOOLEAN DEFAULT 0,
                    can_manage_chat BOOLEAN DEFAULT 0,
                    can_change_info BOOLEAN DEFAULT 0,
                    can_post_messages BOOLEAN DEFAULT 0,
                    can_edit_messages BOOLEAN DEFAULT 0,
                    can_delete_messages BOOLEAN DEFAULT 0,
                    can_invite_users BOOLEAN DEFAULT 0,
                    can_restrict_members BOOLEAN DEFAULT 0,
                    can_promote_members BOOLEAN DEFAULT 0,
                    can_manage_video_chats BOOLEAN DEFAULT 0,
                    can_post_stories BOOLEAN DEFAULT 0,
                    can_edit_stories BOOLEAN DEFAULT 0,
                    can_delete_stories BOOLEAN DEFAULT 0,
                    is_anonymous BOOLEAN DEFAULT 0,
                    can_manage_voice_chats BOOLEAN DEFAULT 0,
                    can_pin_messages BOOLEAN DEFAULT 0,
                    can_manage_topics BOOLEAN DEFAULT 0,
                    FOREIGN KEY (chat_id) REFERENCES Users(chat_id) ON DELETE CASCADE
                )
            ''')

            self.conn.commit()
        except  (sqlite3.Error,AttributeError) as e:
            print("Error creating tables:", e)

    # --- Getter Methods ---
    def get_user(self, user_id):
        try:
            self.cursor.execute('SELECT * FROM Users WHERE user_id = ?', (user_id,))
            return self.cursor.fetchone()
        except  (sqlite3.Error,AttributeError) as e:
            print("Error fetching user:", e)
            return None

    def get_group(self, user_id, chat_id):
        try:
            self.cursor.execute('SELECT * FROM Groups WHERE user_id = ? AND chat_id = ?', (user_id, chat_id))
            return self.cursor.fetchone()
        except  (sqlite3.Error,AttributeError) as e:
            print("Error fetching group:", e)
            return None

    def get_channel(self, user_id, chat_id):
        try:
            self.cursor.execute('SELECT * FROM Channels WHERE user_id = ? AND chat_id = ?', (user_id, chat_id))
            return self.cursor.fetchone()
        except  (sqlite3.Error,AttributeError) as e:
            print("Error fetching channel:", e)
            return None

    def get_permissions(self, user_id, chat_id):
        try:
            self.cursor.execute('SELECT * FROM Permissions WHERE user_id = ? AND chat_id = ?', (user_id, chat_id))
            return self.cursor.fetchone()
        except  (sqlite3.Error,AttributeError) as e:
            print("Error fetching permissions:", e)
            return None

    def prevent_unnecessary_new_user(self, user_id):
        try:
            self.cursor.execute("SELECT * FROM Users WHERE user_id = ? AND chat_username = '' AND chat_type = ''", (user_id,))
            return self.cursor.fetchone()
        except  (sqlite3.Error,AttributeError) as e:
            print("Error preventing unnecessary new user:", e)
            return None

    # --- Setter Methods ---
    def add_user(self, user_id, chat_username='', chat_type=''):
        try:
            self.cursor.execute('''
                INSERT OR REPLACE INTO Users (user_id, chat_username, chat_type)
                VALUES (?, ?, ?)
            ''', (user_id, chat_username, chat_type))
            self.conn.commit()
            return True
        except  (sqlite3.Error,AttributeError) as e:
            print("Error adding chat credentials:", e)
            return False
        
    # def update_user(self,chat_username,chat_type,chat_id,user_id):
    #     print(chat_username,chat_id,chat_type,user_id)
    #     try:
    #         self.cursor.execute("UPDATE Users SET chat_username = ?,chat_type = ?, chat_id = ? WHERE user_id = ? AND ( chat_username = NULL AND chat_id = NULL ) ",(chat_username,chat_type,chat_id,user_id))
    #         self.conn.commit()
    #         return True
    #     except  (sqlite3.Error,AttributeError) as e:
    #         print("Error updating chat credentials: ",e)
    #         return False

    def update_user(self, chat_username, chat_type, chat_id, user_id):
        print(chat_username, chat_id, chat_type, user_id)
        try:
            # Using IS NULL to match rows where chat_username and chat_id are NULL
            self.cursor.execute("""
                UPDATE Users 
                SET chat_username = ?, chat_type = ?, chat_id = ? 
                WHERE user_id = ? AND chat_id IS NULL
            """, (chat_username, chat_type, chat_id, user_id))
            self.conn.commit()
            return True
        except (sqlite3.Error, AttributeError) as e:
            print("Error updating chat credentials:", e)
            return False
                
        
    def remove_user(self,user_id,chat_id):
        try:
            self.cursor.execute('DELETE FROM Users WHERE user_id = ? AND chat_id = ?',(user_id,chat_id))
            self.conn.commit()
            return True
        except (sqlite3.Error,AttributeError) as e:
            print("Error removing this chat credentials: ",e)
            return False

    def add_group(self, user_id, group_name, chat_id):
        try:
            print(self.prevent_unnecessary_new_user(user_id))
            self.cursor.execute('''
                INSERT OR REPLACE INTO Groups (user_id, group_name, chat_id)
                VALUES (?, ?, ?)
            ''', (user_id, group_name, chat_id))
            self.conn.commit()
            return True
        except (sqlite3.Error,AttributeError) as e:
            print("Error adding group:", e)
            return False
        
    def add_supergroup(self, user_id, group_name, chat_id):
        try:
            print(self.prevent_unnecessary_new_user(user_id))
            self.cursor.execute('''
                INSERT OR REPLACE INTO Supergroups (user_id, supergroup_name, chat_id)
                VALUES (?, ?, ?)
            ''', (user_id, group_name, chat_id))
            self.conn.commit()
            return True
        except  (sqlite3.Error,AttributeError) as e:
            print("Error adding supergroup:", e)
            return False

    def add_channel(self, user_id, channel_name, chat_id):
        try:
            self.cursor.execute('''
                INSERT OR REPLACE INTO Channels (user_id, channel_name, chat_id)
                VALUES (?, ?, ?)
            ''', (user_id, channel_name, chat_id))
            self.conn.commit()
            return True
        except  (sqlite3.Error,AttributeError) as e:
            print("Error adding channel:", e)
            return False

    
    def set_permissions(self, user_id, chat_id, chat_type, permissions_dict):
        """
        Sets permissions for a user in a specific group or channel.
        
        Parameters:
        - user_id: int
        - chat_id: int
        - chat_type: str
        - permissions_dict: dict - dictionary containing permission fields to be updated dynamically.
        """
        # Base fields
        base_fields = {
            "user_id": user_id,
            "chat_id": chat_id,
            "chat_type": chat_type
        }
        
        # Merge base fields with dynamic permissions from the dictionary
        data = {**base_fields, **permissions_dict}
        
        # Create placeholders for columns and values dynamically
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?" for _ in data])
        values = tuple(data.values())

        try:
            # Execute the query dynamically
            self.cursor.execute(f'''
                INSERT OR REPLACE INTO Permissions ({columns}) VALUES ({placeholders})
            ''', values)
            self.conn.commit()
            return True
        except (sqlite3.Error, AttributeError) as e:
            print("Error setting permissions:", e)
            return False
    
    def update_permissions(self, table_name, identifiers, updates):
        """
        Update specific fields in a table for rows matching multiple identifiers.
        :param table_name: Name of the table to update.
        :param identifiers: Dictionary where keys are identifier column names and values are their values.
        :param updates: Dictionary where keys are column names and values are the new values for those columns.
        :return: True if the update was successful, False otherwise.
        """
        try:
            # Prepare the SET clause for the columns to update
            set_clause = ", ".join([f"{col} = ?" for col in updates.keys()])
            
            # Prepare the WHERE clause for the identifiers
            where_clause = " AND ".join([f"{col} = ?" for col in identifiers.keys()])
            
            # Build the final SQL query
            query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
            
            # Combine the parameters for updates and identifiers
            params = list(updates.values()) + list(identifiers.values())
            
            # Execute and commit the query
            self.cursor.execute(query, tuple(params))
            self.conn.commit()
            
            return True
        except sqlite3.Error as e:
            print("Error updating chat permission:", e)
            return False

    def close_connection(self):
        try:
            self.conn.close()
        except (sqlite3.Error,AttributeError) as e:
            print("Error closing connection:", e)








# import sqlite3

# class BotDatabase:
#     def __init__(self, db_name='database/bot_management.db'):
#         self.db_name = db_name
#         self.conn = sqlite3.connect(self.db_name)
#         self.cursor = self.conn.cursor()
        
#     def create_tables(self):
#         # Create Users table
#         self.cursor.execute('''
#             CREATE TABLE IF NOT EXISTS Users (
#                 user_id INTEGER NOT NULL,
#                 chat_username INTEGER UNIQUE,
#                 chat_type TEXT,
#                 created_at DATETIME DEFAULT CURRENT_TIMESTAMP
#             )
#         ''')

#         # Create Groups table
#         self.cursor.execute('''
#             CREATE TABLE IF NOT EXISTS Groups (
#                 user_id INTEGER NOT NULL,
#                 group_name TEXT NOT NULL,
#                 chat_id INTEGER NOT NULL,
#                 created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
#                 PRIMARY KEY (user_id, chat_id),
#                 FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
#             )
#         ''')

#         # Create Channels table
#         self.cursor.execute('''
#             CREATE TABLE IF NOT EXISTS Channels (
#                 user_id INTEGER NOT NULL,
#                 channel_name TEXT NOT NULL,
#                 chat_id INTEGER NOT NULL,
#                 created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
#                 PRIMARY KEY (user_id, chat_id),
#                 FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
#             )
#         ''')

#         # Create Permissions table (handles both Groups and Channels)
#         self.cursor.execute('''
#             CREATE TABLE IF NOT EXISTS Permissions (
#                 permission_id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 chat_id INTEGER NOT NULL,
#                 chat_type TEXT NOT NULL CHECK(chat_type IN ('group', 'channel')),
#                 status TEXT NOT NULL CHECK(status IN ('member','administrator','left','kicked')),
#                 can_post_messages BOOLEAN DEFAULT 0,
#                 can_edit_messages BOOLEAN DEFAULT 0,
#                 can_delete_messages BOOLEAN DEFAULT 0,
#                 can_invite_users BOOLEAN DEFAULT 0,
#                 can_restrict_members BOOLEAN DEFAULT 0,
#                 can_pin_messages BOOLEAN DEFAULT 0,
#                 can_manage_video_chats BOOLEAN DEFAULT 0,
#                 can_post_stories BOOLEAN DEFAULT 0,
#                 can_edit_stories BOOLEAN DEFAULT 0,
#                 can_delete_stories BOOLEAN DEFAULT 0,
#                 is_anonymous BOOLEAN DEFAULT 0,
#                 can_manage_voice_chats BOOLEAN DEFAULT 0,
#                 FOREIGN KEY (chat_id) REFERENCES Users(chat_username) ON DELETE CASCADE
#             )
#         ''')

#         self.conn.commit()
        
#         # --- Getter Methods ---
#     def get_user(self, user_id):
#         """Fetch a user by user_id."""
#         self.cursor.execute('SELECT * FROM Users WHERE user_id = ?', (user_id,))
#         return self.cursor.fetchone()

#     def get_group(self, user_id, chat_id):
#         """Fetch a group by group_id and chat_id."""
#         self.cursor.execute('SELECT * FROM Groups WHERE user_id = ? AND chat_id = ?', (user_id, chat_id))
#         return self.cursor.fetchone()

#     def get_channel(self, user_id, chat_id):
#         """Fetch a channel by channel_id and chat_id."""
#         self.cursor.execute('SELECT * FROM Channels WHERE user_id = ? AND chat_id = ?', (user_id, chat_id))
#         return self.cursor.fetchone()

#     def get_permissions(self, user_id, chat_id):
#         """Fetch permissions for a user in a specific group or channel."""
#         self.cursor.execute('SELECT * FROM Permissions WHERE user_id = ? AND chat_id = ?', (user_id, chat_id))
#         return self.cursor.fetchone()

#     def prevent_unncessary_new_user(self,user_id):
#         """ Prevent unncessary /new_user command by the same user"""
#         self.cursor.execute("SELECT * FORM Users WHERE user_id = ? AND chat_username = '' AND chat_type = '' ", (user_id))
#         return self.cursor.fetchone()
    
#     # --- Setter Methods ---
#     def add_user(self, user_id, chat_username = '', chat_type = ''):
#         """Add a new user to the Users table."""
#         self.cursor.execute('''
#             INSERT OR REPLACE INTO Users (user_id,chat_username ,chat_type)
#             VALUES (?, ?, ?)
#         ''', (user_id, chat_username, chat_type))
#         self.conn.commit()

#     def add_group(self, user_id, group_name, chat_id):
#         """Add a new group associated with a user."""
#         self.cursor.execute('''
#             INSERT OR REPLACE INTO Groups (user_id, group_name, chat_id)
#             VALUES (?, ?, ?)
#         ''', (user_id, group_name, chat_id))
#         self.conn.commit()

#     def add_channel(self,user_id, channel_name, chat_id):
#         """Add a new channel associated with a user."""
#         self.cursor.execute('''
#             INSERT OR REPLACE INTO Channels (user_id, channel_name, chat_id)
#             VALUES (?, ?, ?)
#         ''', ( user_id, channel_name, chat_id))
#         self.conn.commit()

#     def set_permissions(self, user_id, chat_id, chat_type, can_post_messages=0, can_edit_messages=0,
#                         can_delete_messages=0, can_invite_users=0, can_restrict_members=0,
#                         can_pin_messages=0, can_manage_video_chats=0):
#         """Set permissions for a user in a specific group or channel."""
#         self.cursor.execute('''
#             INSERT OR REPLACE INTO Permissions (
#                 user_id, chat_id, chat_type, can_post_messages, can_edit_messages, 
#                 can_delete_messages, can_invite_users, can_restrict_members, 
#                 can_pin_messages, can_manage_video_chats,can_post_stories,
#                 can_edit_stories,can_delete_stories, is_anonymous,can_manage_voice_chats,
#             ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?,?,?,?)
#         ''', (user_id, chat_id, chat_type, can_post_messages, can_edit_messages,
#               can_delete_messages, can_invite_users, can_restrict_members,
#               can_pin_messages, can_manage_video_chats))
#         self.conn.commit()


#     def close_connection(self):
#         """Closes the database connection."""
#         self.conn.close()




