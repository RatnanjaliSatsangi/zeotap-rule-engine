import sqlite3
import json
import re

# AST Node Class
class ASTNode:
    def __init__(self, type, left=None, right=None, value=None):
        self.type = type  # 'operator' or 'operand'
        self.left = left  # Left child (ASTNode)
        self.right = right  # Right child (ASTNode)
        self.value = value  # For 'operand' nodes, store value (e.g., 'age > 30')

    def __str__(self):
        if self.type == "operand":
            return str(self.value)  # Operand nodes are leaf nodes with conditions
        elif self.type == "operator":
            return f"({self.left} {self.value} {self.right})"  # Recursively print the left and right nodes

# Rule Engine Class
class RuleEngine:
    def __init__(self, db_name="rules.db"):
        self.db_name = db_name  # Save the DB name but open connections per request
    
    def get_connection(self):
        """Create a new database connection for each request."""
        return sqlite3.connect(self.db_name)

    def get_predefined_attributes(self):
        """Fetch predefined attributes from the config table."""
        conn = self.get_connection()
        cursor = conn.execute('SELECT meta FROM config WHERE id = "PREDEFINED_ATTRIBUTES" AND active = 1')
        result = cursor.fetchone()
        conn.close()

        if result:
            return json.loads(result[0])  # Return the list of attributes from the JSON string
        return []

    def update_predefined_attributes(self, new_attributes):
        """Update the predefined attributes in the config table."""
        attributes_json = json.dumps(new_attributes)
        conn = self.get_connection()
        conn.execute('UPDATE config SET meta = ? WHERE id = "PREDEFINED_ATTRIBUTES"', (attributes_json,))
        conn.commit()
        conn.close()

    def create_rule(self, rule_name, rule_text):
        """Create a new rule after validation."""
        if not self.validate_rule(rule_text):
            raise ValueError(f"Invalid rule: {rule_text}")

        conn = self.get_connection()
        conn.execute('INSERT INTO rules (rule_name, rule_text, rule_combination, is_combination) VALUES (?, ?, ?, ?)', 
                     (rule_name, rule_text, None, False))
        conn.commit()
        conn.close()

    def modify_rule(self, rule_id, new_rule_text):
        """Modify an existing rule by updating its rule text."""
        if not self.validate_rule(new_rule_text):
            raise ValueError(f"Invalid rule: {new_rule_text}")

        conn = self.get_connection()
        conn.execute('UPDATE rules SET rule_text = ? WHERE id = ?', (new_rule_text, rule_id))
        conn.commit()
        conn.close()

    def delete_rule(self, rule_id):
        """Delete a rule by its ID."""
        conn = self.get_connection()
        conn.execute('DELETE FROM rules WHERE id = ?', (rule_id,))
        conn.commit()
        conn.close()

    def combine_rules(self, rule_ids):
        """Combine the rules by storing their IDs in rule_combination."""
        rule_combination = json.dumps(rule_ids)  # Store the list of rule IDs as a JSON string
        combined_rule_name = "Combined Rule"
        combined_rule_text = f"Combination of rules: {rule_ids}"

        conn = self.get_connection()
        conn.execute('INSERT INTO rules (rule_name, rule_text, rule_combination, is_combination) VALUES (?, ?, ?, ?)', 
                     (combined_rule_name, combined_rule_text, rule_combination, True))
        conn.commit()
        conn.close()

        return {"combined_rule_name": combined_rule_name, "combined_rule_text": combined_rule_text}

    def get_all_rules(self):
        """Fetch all rules from the database."""
        conn = self.get_connection()
        cursor = conn.execute('SELECT id, rule_name, rule_text, is_combination FROM rules')
        rules = cursor.fetchall()
        conn.close()
        return [{"id": row[0], "name": row[1], "text": row[2], "is_combination": row[3]} for row in rules]

    def evaluate_rule(self, rule_id, data):
        """Evaluate the rule by fetching it from the database and comparing with data."""
        conn = self.get_connection()
        cursor = conn.execute('SELECT rule_text, rule_combination, is_combination FROM rules WHERE id = ?', (rule_id,))
        rule_data = cursor.fetchone()
        conn.close()

        if rule_data is None:
            return False

        rule_text, rule_combination, is_combination = rule_data

        if is_combination:
            rule_ids = json.loads(rule_combination)
            return self.evaluate_combined_rule(rule_ids, data)
        else:
            populated_rule = self.populate_rule_with_values(rule_text, data)
            print(f"Populated rule for evaluation: {populated_rule}")
            return self.evaluate_expression(populated_rule)

    def evaluate_combined_rule(self, rule_ids, data):
        """Evaluate combined rules."""
        results = []
        for rule_id in rule_ids:
            results.append(self.evaluate_rule(rule_id, data))
        return all(results)  # You can modify this to use 'any()' for OR logic

    def extract_fields_from_rule(self, rule_text):
        """
        Extract variable names (fields) from the rule text.
        This function will extract variables from the left-hand side of operators and ignore values from the right-hand side.
        Example: From "age > 30 AND salary > 50000", we extract ["age", "salary", "department", "experience"].
        """
        operators = ['>', '<', '>=', '<=', '=', '==']
        rule_parts = re.split(r'AND|OR', rule_text)

        variables = []
        for part in rule_parts:
            part = part.replace("(", "").replace(")", "")
            for operator in operators:
                if operator in part:
                    left_side = part.split(operator)[0].strip()
                    if re.match(r'\b[a-zA-Z_]+\b', left_side):  # Ensure it's a valid variable (alphabetic)
                        variables.append(left_side)
                    break
        return list(set(variables))  # Remove duplicates and return

    def populate_rule_with_values(self, rule_text, data):
        """
        Populate the rule with values from the user input.
        Numeric values should remain unquoted, and string values should be wrapped in quotes.
        Also, replace 'AND'/'OR' with Python's 'and'/'or', and ensure '=' is replaced by '=='.
        """
        rule_text = rule_text.replace("AND", "and").replace("OR", "or")
        rule_text = re.sub(r'(?<!\=)\=(?!\=)', '==', rule_text)

        for field, value in data.items():
            if isinstance(value, str) and not value.isdigit():
                value = f"'{value}'"
            else:
                value = str(value)
            rule_text = re.sub(rf'\b{field}\b', value, rule_text)
        
        return rule_text

    def evaluate_expression(self, rule_text):
        """Evaluate the populated rule as a Python expression."""
        try:
            return eval(rule_text)
        except Exception as e:
            print(f"Error evaluating rule: {e}")
            return False

    def validate_rule(self, rule_text):
        """
        Validate that the rule text is well-formed and uses valid attributes.
        - Ensure it contains valid operators.
        - Ensure only catalog attributes are used.
        """
        operators = ['>', '<', '>=', '<=', '=', '==', 'AND', 'OR']
        attributes = self.extract_fields_from_rule(rule_text)
        valid_attributes = self.get_predefined_attributes()

        # Validate attributes
        for attribute in attributes:
            if attribute not in valid_attributes:
                print(f"Error: Invalid attribute '{attribute}'. It must be one of {valid_attributes}.")
                return False
        
        return True
