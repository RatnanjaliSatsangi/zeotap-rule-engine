import sqlite3
import json

def setup_database(db_name="rules.db"):
    conn = sqlite3.connect(db_name)
    
    # Drop the old tables if they exist
    conn.execute('DROP TABLE IF EXISTS rules')
    conn.execute('DROP TABLE IF EXISTS config')

    # Create the new rules table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            rule_name TEXT, 
            rule_text TEXT, 
            rule_combination TEXT, 
            is_combination BOOLEAN
        )
    ''')

    # Create the config table to store predefined attributes
    conn.execute('''
        CREATE TABLE IF NOT EXISTS config (
            id TEXT PRIMARY KEY, 
            meta TEXT, 
            active BOOLEAN DEFAULT 1
        )
    ''')

    # Insert default predefined attributes as a JSON array in the config table
    default_attributes = json.dumps(['age', 'salary', 'experience', 'department'])
    conn.execute('INSERT INTO config (id, meta, active) VALUES (?, ?, ?)', 
                 ('PREDEFINED_ATTRIBUTES', default_attributes, True))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    setup_database()
