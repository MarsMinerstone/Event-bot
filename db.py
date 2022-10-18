import sqlite3

class BotDB:

    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    def user_exists(self, user_id: int):
        """Проверяем, есть ли юзер в базе"""
        result = self.cursor.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (user_id,))
        return bool(len(result.fetchall()))

    def get_user_id(self, user_id: int):
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

    def add_user(self, user_id: int, username: str):
        """Добавляем юзера в базу"""
        self.cursor.execute("INSERT INTO `users` (`user_id`, `username`) VALUES (?, ?)", (user_id, username))
        return self.conn.commit()

    # resume table

    def create_resume(self, user_id: int, text: str):
        """Добавляем резюме в базу и возвращаем id"""
        self.cursor.execute("INSERT INTO `resumes` (`user_id`, `text`) VALUES (?, ?)", (user_id, text))
        self.conn.commit()
        result = self.cursor.execute("SELECT `id`, `user_id` FROM `resumes` WHERE `user_id` = ? ORDER BY `id` DESC", (user_id,))
        return result.fetchone()[0]

    def get_last_new_resume(self):
        """Достаем первое новое резюме"""
        result = self.cursor.execute("SELECT `id`, `user_id`, `text`, `approved` FROM `resumes` WHERE `approved` = FALSE")
        return result.fetchone()

    def get_last_payed_resume(self):
        """Достаем первое оплаченное резюме"""
        result = self.cursor.execute("SELECT `id`, `user_id`, `text`, `approved` FROM `resumes` "
                                     "WHERE `approved` = TRUE AND `payed` = TRUE")
        return result.fetchone()

    def get_resume_by_id(self, resume_id: int):
        """Достаем резюме по id"""
        result = self.cursor.execute("SELECT `id`, `user_id`, `text` FROM `resumes` WHERE `id` = ?", (resume_id,))
        return result.fetchone()

    def update_approved(self, resume_id: int):
        """Подтверждаем резюме"""
        self.cursor.execute("UPDATE `resumes` SET `approved` = TRUE WHERE `id` = ?", (resume_id,))
        return self.conn.commit()

    def update_published(self, resume_id: int):
        """Публикуем резюме"""
        self.cursor.execute("UPDATE `resumes` SET `published` = TRUE WHERE `id` = ?", (resume_id,))
        return self.conn.commit()

    def delete_disapproved(self, resume_id: int):
        """Удаляем неподтвержденное резюме"""
        self.cursor.execute("DELETE FROM `resumes` WHERE `id`=?", (resume_id,))
        return self.conn.commit()

    # close

    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()
