from flask import Flask, request, jsonify
from flask_cors import CORS
from script import process_submission, questions, get_formatted_questions

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/questions', methods=['GET'])
def get_questions():
    """Return all available questions with test cases and generated boilerplate code."""
    # Get questions with boilerplate code generated from templates
    formatted_questions = get_formatted_questions()
    return jsonify(formatted_questions)

@app.route('/submit', methods=['POST'])
def submit_code():
    """Process a code submission."""
    data = request.json
    
    # Validate required fields
    required_fields = ['code', 'language', 'questionId']
    for field in required_fields:
        if field not in data:
            return jsonify({
                "error": f"Missing required field: {field}"
            }), 400
    
    code = data['code']
    language = data['language']
    question_id = data['questionId']
    
    # Validate language
    if language not in ['python', 'cpp', 'java']:
        return jsonify({
            "error": f"Unsupported language: {language}"
        }), 400
        
    # Process the submission
    result = process_submission(code, language, question_id)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5000) 