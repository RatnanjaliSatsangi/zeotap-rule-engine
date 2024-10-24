from flask import Flask, jsonify, request, render_template
from rule_engine import RuleEngine

app = Flask(__name__)
rule_engine = RuleEngine()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/create_rule', methods=['POST'])
def create_rule():
    rule_name = request.json.get('rule_name')
    rule_text = request.json.get('rule_text')
    
    if not rule_name or not rule_text:
        return jsonify({"error": "Rule name and text are required"}), 400

    # Create the rule in the database
    rule_engine.create_rule(rule_name, rule_text)
    return jsonify({"message": "Rule created successfully"}), 201

@app.route('/api/evaluate_rule', methods=['POST'])
def evaluate_rule():
    rule_id = request.json.get('rule_id')
    data = request.json.get('data')

    if not rule_id or not data:
        return jsonify({"error": "Rule ID and data are required"}), 400

    # Evaluate the rule with the provided data
    result = rule_engine.evaluate_rule(rule_id, data)
    return jsonify({"result": result})

@app.route('/api/combine_rules', methods=['POST'])
def combine_rules():
    rule_ids = request.json.get('rule_ids')

    if not rule_ids:
        return jsonify({"error": "Rule IDs are required"}), 400

    # Combine the rules and return the result
    combined_rule = rule_engine.combine_rules(rule_ids)
    return jsonify({"combined_ast": str(combined_rule)})

@app.route('/api/get_rules', methods=['GET'])
def get_rules():
    # Get all rules from the database
    rules = rule_engine.get_all_rules()
    return jsonify({"rules": rules})

@app.route('/api/get_rule_metadata/<int:rule_id>', methods=['GET'])
def get_rule_metadata(rule_id):
    """
    Fetch metadata for the selected rule to dynamically create input fields for evaluation.
    """
    conn = rule_engine.get_connection()
    cursor = conn.execute('SELECT rule_text FROM rules WHERE id = ?', (rule_id,))
    rule_data = cursor.fetchone()
    conn.close()

    if rule_data:
        rule_text = rule_data[0]
        # Extract the fields (variable names) from the rule text
        fields = rule_engine.extract_fields_from_rule(rule_text)
        return jsonify({"fields": fields})
    else:
        return jsonify({"error": "Rule not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
