# create_admin_user.py
from werkzeug.security import generate_password_hash
from db_utils import get_db_connection

def create_admin_user():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
    count = cur.fetchone()[0]
    if count == 0:
        hashed_pw = generate_password_hash('admin123')
        cur.execute("""
            INSERT INTO users (email, phone, password_hash, first_name, last_name, role, preferred_language)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            'admin@recipekeeper.com',
            '+910000000000',
            hashed_pw,
            'Admin',
            'User',
            'admin',
            'en'
        ))
        conn.commit()
        print("✅ Admin user created: admin@recipekeeper.com / admin123")

    cur.close()
    conn.close()
