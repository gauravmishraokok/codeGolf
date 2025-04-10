# Code Golf Competition Platform

A minimal but extendable platform for evaluating code golf submissions. This platform supports Python, Java, and C++ and evaluates submissions based on character count (excluding whitespace).

## Features

- Support for Python, Java, and C++ code evaluation
- Character count scoring (excluding whitespace)
- Test case validation with examples
- Function signature templates
- CodeMirror-based syntax highlighting editor
- Normalized scoring based on optimal character counts
- Privacy-focused (optimal lengths are not shown to users)

### Running the Application

1. Start the API server:
```
python api.py
```

2. Open the frontend in your browser:
```
open test_frontend/index.html
```
Or just open the HTML file in your browser manually.

## Usage

1. Select a question from the dropdown
2. Choose your programming language (Python, Java, or C++)
3. Write your solution in the code editor using the provided function signature
4. Submit your solution to see your score and how close your solution is to optimal

## Scoring

The score is calculated using the formula:
```
score = round(100 * (optimal_length / user_code_length), 2)
```

Where:
- `optimal_length` is the predetermined optimal character count for that language and question
- `user_code_length` is the non-whitespace character count of your submission

The maximum possible score is 100.

## Project Structure

```
/codegolf/
│
├── script.py               # Core logic (evaluation, scoring, etc.)
├── api.py                  # Flask API for handling submissions
├── test_frontend/          # Simple HTML frontend for testing
│   └── index.html
└── README.md               # This file
```

## Extending the Platform

The platform is designed to be easily extendable:

- To add new languages, modify the evaluation functions in `script.py`
- To add new questions, update the `questions` dictionary in `script.py`
- For a persistent backend, consider replacing the hardcoded questions with a database
- Add user authentication and a leaderboard for a complete competition platform

## Sample Questions

The platform currently includes two sample questions:
1. Return the nth Fibonacci number
2. Return the factorial of n

Each question includes test cases, function signatures, and language-specific optimal character counts. 