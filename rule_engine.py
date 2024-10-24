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

    def create_rule(self, rule_name, rule_text):
        conn = self.get_connection()
        conn.execute('INSERT INTO rules (rule_name, rule_text, rule_combination, is_combination) VALUES (?, ?, ?, ?)', 
                     (rule_name, rule_text, None, False))
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
        conn = self.get_connection()
        cursor = conn.execute('SELECT id, rule_name, rule_text, is_combination FROM rules')
        rules = cursor.fetchall()
        conn.close()
        return [{"id": row[0], "name": row[1], "text": row[2], "is_combination": row[3]} for row in rules]

    def parse_rule(self, rule_text):
        # This is a placeholder that returns a simple AST. 
        return ASTNode(type="operand", value=rule_text)

    def evaluate_rule(self, rule_id, data):
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
            # Replace variables with user input values
            populated_rule = self.populate_rule_with_values(rule_text, data)
            print(f"Populated rule for evaluation: {populated_rule}")
            return self.evaluate_expression(populated_rule)

    def evaluate_combined_rule(self, rule_ids, data):
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
        # Define common operators
        operators = ['>', '<', '>=', '<=', '=', '==']

        # Split the rule by logical connectors like AND, OR
        rule_parts = re.split(r'AND|OR', rule_text)

        variables = []
        # print(rule_text)
        # print(rule_parts)
        for part in rule_parts:
            # Split by each operator and extract the left-hand side (which should be the variable)
            part = part.replace("(","").replace(")","")
            for operator in operators:
                if operator in part:
                    left_side = part.split(operator)[0].strip()
                    if re.match(r'\b[a-zA-Z_]+\b', left_side):  # Ensure it's a valid variable (alphabetic)
                        variables.append(left_side)
                        # print(f"Found variable: {left_side}")  # Debugging statement
                    break

        # print(f"Final extracted variables: {variables}")  # Debugging statement
        return list(set(variables))  # Remove duplicates and return

    def populate_rule_with_values(self, rule_text, data):
        """
        Populate the rule with values from the user input.
        Numeric values should remain unquoted, and string values should be wrapped in quotes.
        Also, replace 'AND'/'OR' with Python's 'and'/'or', and ensure '=' is replaced by '=='.
        """
        # Replace AND/OR with Python's and/or
        rule_text = rule_text.replace("AND", "and").replace("OR", "or")

        # Replace single '=' with '==' for proper comparison
        rule_text = re.sub(r'(?<!\=)\=(?!\=)', '==', rule_text)

        # Now substitute the variables with user values
        for field, value in data.items():
            # Check if the value is a string or numeric
            if isinstance(value, str) and not value.isdigit():  # If the value is a non-numeric string, add quotes
                value = f"'{value}'"  # Add quotes for string values
            else:  # Numeric values should not have quotes
                value = str(value)

            # Replace the variable in the rule with the corresponding value
            rule_text = re.sub(rf'\b{field}\b', value, rule_text)
        
        return rule_text



    def evaluate_expression(self, rule_text):
        """
        Evaluate the populated rule as a Python expression.
        Caution: Using eval can be dangerous if inputs are not sanitized. This should be used with caution.
        """
        try:
            return eval(rule_text)
        except Exception as e:
            print(f"Error evaluating rule: {e}")
            return False
