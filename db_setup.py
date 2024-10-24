import sqlite3

def setup_database(db_name="rules.db"):
    conn = sqlite3.connect(db_name)
    conn.execute('''CREATE TABLE IF NOT EXISTS rules 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                     rule_text TEXT, 
                     ast BLOB)''')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    setup_database()
