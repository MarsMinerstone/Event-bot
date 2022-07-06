import sqlite3

class BotDB:

    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    def user_exists(self, user_id):
        """Проверяем, есть ли юзер в базе"""
        result = self.cursor.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (user_id,))
        return bool(len(result.fetchall()))

    def get_user_id(self, user_id):
        """Достаем id юзера в базе по его user_id"""
        result = self.cursor.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (user_id,))
        return result.fetchone()[0]

    def get_usernames(self):
        """Достаем usernaes юзеров в базе"""
        result = self.cursor.execute("SELECT `username` FROM `users`")
        return result.fetchmany(1000)

    def get_all_users_id(self):
        """Достаем всех юзеров в базе по его user_id"""
        result = self.cursor.execute("SELECT `user_id` FROM `users`")
        # print(result, result.fetchone(), sep='\n')
        return result.fetchmany(1000)

    def add_user(self, user_id, username):
        """Добавляем юзера в базу"""
        self.cursor.execute("INSERT INTO `users` (`user_id`, `username`) VALUES (?, ?)", (user_id, username))
        return self.conn.commit()

    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()