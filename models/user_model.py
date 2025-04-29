from flask_login import UserMixin
from db_utils import get_db_connection
from psycopg2.extras import RealDictCursor

class User(UserMixin):
    def __init__(self, user_id, name, email):
        self.id = user_id
        self.name = name
        self.email = email

    @staticmethod
    def get(user_id):
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT id, name, email FROM users WHERE id = %s", (user_id,))
        user_data = cur.fetchone()
        cur.close()
        conn.close()

        if user_data:
            return User(user_data['id'], user_data['name'], user_data['email'])
        return None
 
