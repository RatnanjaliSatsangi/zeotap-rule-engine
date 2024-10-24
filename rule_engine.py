import sqlite3
import threading

# AST Node Class
class ASTNode:
    def __init__(self, type, left=None, right=None, value=None):
        self.type = type
        self.left = left
        self.right = right
        self.value = value

# Rule Engine Class
class RuleEngine:
    def __init__(self, db_name="rules.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.lock = threading.Lock()
        self.create_table()
    
    def create_table(self):
        with self.lock:
            self.conn.execute('''CREATE TABLE IF NOT EXISTS rules 
                                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                  rule_text TEXT, 
                                  ast BLOB)''')
    
    def create_rule(self, rule_text):
        # Parse rule and build AST
        ast = self.parse_rule(rule_text)
        with self.lock:
            self.conn.execute('INSERT INTO rules (rule_text, ast) VALUES (?, ?)', 
                              (rule_text, str(ast)))
            self.conn.commit()
    
    def parse_rule(self, rule_text):
        # Simplified rule to AST conversion (Placeholder)
        # Example logic can be enhanced to parse actual rules into AST.
        return ASTNode(type="root", value=rule_text)
    
    def evaluate_rule(self, rule_id, data):
        cursor = self.conn.execute('SELECT ast FROM rules WHERE id = ?', (rule_id,))
        rule_data = cursor.fetchone()
        if rule_data:
            ast = rule_data[0]
            # Evaluate AST against the provided data (Placeholder logic)
            return self.evaluate_ast(ast, data)
        return False
    
    def evaluate_ast(self, ast, data):
        # Placeholder for evaluating AST against data
        # Example: ast might be parsed as conditions to check
        return True if data.get("age", 0) > 30 else False

    def combine_rules(self, rule_ids):
        # Combine rules based on rule_ids and return a combined AST (Placeholder)
        combined_ast = ASTNode(type="operator", left="rule1", right="rule2")
        return combined_ast
