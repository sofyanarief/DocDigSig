class Document:
    def __init__(self, db):
        self.db = db

    def insert_document(self, origname_document, upname_document, t_user_id_user, t_key_id_key, t_key_t_user_id_user):
        query = """
        INSERT INTO t_document (origname_document, upname_document, t_user_id_user, t_key_id_key, t_key_t_user_id_user)
        VALUES (%s, %s, %s, %s, %s)
        """
        self.db.execute_query(query, (origname_document, upname_document, t_user_id_user, t_key_id_key, t_key_t_user_id_user))

    def get_document(self, id_document):
        query = "SELECT * FROM t_document WHERE id_document = %s"
        return self.db.fetch_query(query, (id_document,))

    def update_document(self, id_document, origname_document=None, upname_document=None):
        query = """
        UPDATE t_document SET origname_document = %s, upname_document = %s
        WHERE id_document = %s
        """
        self.db.execute_query(query, (origname_document, upname_document, id_document))

    def delete_document(self, id_document):
        query = "DELETE FROM t_document WHERE id_document = %s"
        self.db.execute_query(query, (id_document,))
