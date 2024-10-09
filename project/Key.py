class Key:
    def __init__(self, db):
        self.db = db

    def insert_key(self, key_priv_value, key_pub_value, key_name, key_position, key_other_info, t_user_id_user):
        query = """
        INSERT INTO t_key (key_priv_value, key_pub_value, key_name, key_position, key_other_info, t_user_id_user) 
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        self.db.execute_query(query, (key_priv_value, key_pub_value, key_name, key_position, key_other_info, t_user_id_user))

    def get_key(self, id_key):
        query = "SELECT * FROM t_key WHERE id_key = %s"
        return self.db.fetch_query(query, (id_key,))

    def update_key(self, id_key, key_priv_value=None, key_pub_value=None, key_name=None, key_position=None, key_other_info=None):
        query = """
        UPDATE t_key SET key_priv_value = %s, key_pub_value = %s, key_name = %s, key_position = %s, key_other_info = %s
        WHERE id_key = %s
        """
        self.db.execute_query(query, (key_priv_value, key_pub_value, key_name, key_position, key_other_info, id_key))

    def delete_key(self, id_key):
        query = "DELETE FROM t_key WHERE id_key = %s"
        self.db.execute_query(query, (id_key,))
