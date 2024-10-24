from flask import Flask, jsonify, request, render_template
from rule_engine import RuleEngine
import threading

app = Flask(__name__)
rule_engine = RuleEngine()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/create_rule', methods=['POST'])
def create_rule():
    rule_text = request.json.get('rule_text')
    if not rule_text:
        return jsonify({"error": "Rule text is required"}), 400

    threading.Thread(target=rule_engine.create_rule, args=(rule_text,)).start()
    return jsonify({"message": "Rule creation in progress"}), 201

@app.route('/api/evaluate_rule', methods=['POST'])
def evaluate_rule():
    rule_id = request.json.get('rule_id')
    data = request.json.get('data')

    if not rule_id or not data:
        return jsonify({"error": "Rule ID and data are required"}), 400

    result = rule_engine.evaluate_rule(rule_id, data)
    return jsonify({"result": result})

@app.route('/api/combine_rules', methods=['POST'])
def combine_rules():
    rule_ids = request.json.get('rule_ids')

    if not rule_ids:
        return jsonify({"error": "Rule IDs are required"}), 400

    combined_ast = rule_engine.combine_rules(rule_ids)
    return jsonify({"combined_ast": str(combined_ast)})

if __name__ == '__main__':
    app.run(debug=True)
