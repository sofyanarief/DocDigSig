class User:
    def __init__(self, db):
        self.db = db

    def insert_user(self, username, userpass, user_nickname):
        query = "INSERT INTO t_user (username, userpass, user_nickname) VALUES (%s, %s, %s)"
        self.db.execute_query(query, (username, userpass, user_nickname))

    def get_user(self, id_user):
        query = "SELECT * FROM t_user WHERE id_user = %s"
        return self.db.fetch_query(query, (id_user,))

    def update_user(self, id_user, username=None, userpass=None, user_nickname=None):
        query = "UPDATE t_user SET username = %s, userpass = %s, user_nickname = %s WHERE id_user = %s"
        self.db.execute_query(query, (username, userpass, user_nickname, id_user))

    def delete_user(self, id_user):
        query = "DELETE FROM t_user WHERE id_user = %s"
        self.db.execute_query(query, (id_user,))
