import mysql.connector

class DatabaseConnector:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.charset = 'utf8mb4'
        self.collation = 'utf8mb4_general_ci'
        self.connection = None

    def connect(self):
        self.connection = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
            charset=self.charset,
            collation=self.collation
        )
        self.cursor = self.connection.cursor(dictionary=True)

    def close(self):
        if self.connection:
            self.cursor.close()
            self.connection.close()

    def execute_query(self, query, params=None):
        self.cursor.execute(query, params or ())
        self.connection.commit()

    def fetch_query(self, query, params=None):
        self.cursor.execute(query, params or ())
        return self.cursor.fetchall()
