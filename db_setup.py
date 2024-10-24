import sqlite3

def setup_database(db_name="rules.db"):
    conn = sqlite3.connect(db_name)
    
    # Drop the old table if it exists
    conn.execute('DROP TABLE IF EXISTS rules')
    
    # Create the new table with rule_name, rule_text, rule_combination, and is_combination columns
    conn.execute('''
        CREATE TABLE IF NOT EXISTS rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            rule_name TEXT, 
            rule_text TEXT, 
            rule_combination TEXT, 
            is_combination BOOLEAN
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    setup_database()
