import os
import re
import subprocess
import tempfile
import json
from typing import Dict, List, Any, Tuple

# Global language templates
LANGUAGE_TEMPLATES = {
    "python": """# Function to calculate {description}
def solution({parameter_name}):
    # Your code here
    pass

# DO NOT MODIFY CODE BELOW
if __name__ == "__main__":
    {parameter_name} = int(input().strip())
    print(solution({parameter_name}))""",
    
    "cpp": """#include <iostream>
using namespace std;

// Function to calculate {description}
int solution(int {parameter_name}) {{
    // Your code here
    return 0;
}}

// DO NOT MODIFY CODE BELOW
int main() {{
    int {parameter_name};
    cin >> {parameter_name};
    cout << solution({parameter_name}) << endl;
    return 0;
}}""",
    
    "java": """import java.util.Scanner;

public class Solution {{
    // Function to calculate {description}
    public static int solution(int {parameter_name}) {{
        // Your code here
        return 0;
    }}
    
    // DO NOT MODIFY CODE BELOW
    public static void main(String[] args) {{
        Scanner scanner = new Scanner(System.in);
        int {parameter_name} = scanner.nextInt();
        System.out.println(solution({parameter_name}));
        scanner.close();
    }}
}}"""
}

# Sample questions (can be moved to questions.py or loaded from JSON later)
questions = {
    "q1": {
        "description": "the nth Fibonacci number",
        "parameter_name": "n",
        "language_optimal_lengths": {
            # Optimal solution (memoization/dynamic approach):
            # Python: a,b=0,1;exec('a,b=b,a+b;'*(n-1));return b
            "python": 30,
            # C++: int a=0,b=1;for(int i=1;i<n;i++){int t=a;a=b;b+=t;}return b;
            "cpp": 45,
            # Java: int a=0,b=1;for(int i=1;i<n;i++){int t=a;a=b;b+=t;}return b;
            "java": 54
        },
        "test_cases": [
            {"input": "5", "expected_output": "5"},
            {"input": "7", "expected_output": "13"}
        ]
    },
    "q2": {
        "description": "the factorial of n",
        "parameter_name": "n",
        "language_optimal_lengths": {
            # Optimal solution (loop approach):
            # Python: r=1;exec('r*=i;'*n,{'i':1,'r':r});return r
            "python": 22,
            # C++: int r=1;for(int i=1;i<=n;i++)r*=i;return r;
            "cpp": 39,
            # Java: int r=1;for(int i=1;i<=n;i++)r*=i;return r;
            "java": 42
        },
        "test_cases": [
            {"input": "4", "expected_output": "24"},
            {"input": "6", "expected_output": "720"}
        ]
    }
}

# Create submissions directory if it doesn't exist
os.makedirs("submissions", exist_ok=True)

def get_boilerplate(question_id: str, language: str) -> str:
    """Generate boilerplate code for a question and language using templates."""
    if question_id not in questions or language not in LANGUAGE_TEMPLATES:
        return ""
    
    question = questions[question_id]
    template = LANGUAGE_TEMPLATES[language]
    
    # Format the template with question-specific details
    return template.format(
        description=question.get("description", ""),
        parameter_name=question.get("parameter_name", "n")
    )

def count_characters(code: str) -> int:
    """Count non-whitespace characters in code."""
    return len(re.sub(r'\s+', '', code))

def extract_python_function_body(code: str) -> str:
    """Extract the body of the Python solution function."""
    # Find the solution function
    pattern = r'def\s+solution\s*\([^)]*\)\s*:(.*?)(?=\n\s*(?:def|class|if\s+__name__|#\s*DO NOT MODIFY)|\Z)'
    match = re.search(pattern, code, re.DOTALL)
    if not match:
        return ""
    
    # Extract the raw body which includes leading whitespace
    raw_body = match.group(1)
    
    # Split into lines and find actual lines of code (ignoring comments and empty lines)
    lines = raw_body.split('\n')
    if not lines:
        return ""
    
    # Remove leading/trailing empty lines
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    
    if not lines:
        return ""
    
    # Join back together and return
    return '\n'.join(lines)

def extract_cpp_function_body(code: str) -> str:
    """Extract the body of the C++ solution function."""
    # Find the solution function
    pattern = r'int\s+solution\s*\([^)]*\)\s*{'
    match = re.search(pattern, code)
    if not match:
        return ""
    
    # Find the position right after the opening brace
    start_pos = match.end()
    
    # Now manually find the matching closing brace
    brace_count = 1
    end_pos = start_pos
    
    for i in range(start_pos, len(code)):
        if code[i] == '{':
            brace_count += 1
        elif code[i] == '}':
            brace_count -= 1
            if brace_count == 0:
                end_pos = i
                break
    
    if brace_count != 0:
        return ""  # Unmatched braces
    
    # Extract the function body
    body = code[start_pos:end_pos].strip()
    return body

def extract_java_function_body(code: str) -> str:
    """Extract the body of the Java solution function."""
    # Find the solution function
    pattern = r'public\s+static\s+int\s+solution\s*\([^)]*\)\s*{'
    match = re.search(pattern, code)
    if not match:
        return ""
    
    # Find the position right after the opening brace
    start_pos = match.end()
    
    # Now manually find the matching closing brace
    brace_count = 1
    end_pos = start_pos
    
    for i in range(start_pos, len(code)):
        if code[i] == '{':
            brace_count += 1
        elif code[i] == '}':
            brace_count -= 1
            if brace_count == 0:
                end_pos = i
                break
    
    if brace_count != 0:
        return ""  # Unmatched braces
    
    # Extract the function body
    body = code[start_pos:end_pos].strip()
    return body

def extract_function_body(code: str, language: str) -> str:
    """Extract just the function body based on language."""
    if language == "python":
        return extract_python_function_body(code)
    elif language == "cpp":
        return extract_cpp_function_body(code)
    elif language == "java":
        return extract_java_function_body(code)
    return ""

def run_python_code(code: str, input_data: str) -> Tuple[bool, str]:
    """Run Python code with given input and return output."""
    # Create a wrapper to handle input and capture output
    wrapped_code = f"""
import sys
from io import StringIO

# Capture stdout
original_stdout = sys.stdout
sys.stdout = StringIO()

# Set up input
sys.stdin = StringIO('''{input_data}''')

try:
{code}
    output = sys.stdout.getvalue().strip()
    print(output)  # This will be captured
except Exception as e:
    print(f"Error: {{e}}")

# Restore stdout
sys.stdout = original_stdout
"""
    
    try:
        result = subprocess.run(
            ["python", "-c", wrapped_code],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode != 0:
            return False, f"Execution error: {result.stderr}"
        return True, result.stdout.strip()
    except subprocess.TimeoutExpired:
        return False, "Timeout: Code took too long to execute"
    except Exception as e:
        return False, f"Error: {str(e)}"

def run_cpp_code(code: str, input_data: str) -> Tuple[bool, str]:
    """Compile and run C++ code with given input."""
    # Create temp files for code and compilation
    with tempfile.NamedTemporaryFile(suffix='.cpp', delete=False, mode='w') as code_file:
        code_file.write(code)
        cpp_file = code_file.name
    
    executable = os.path.join("submissions", f"{os.path.basename(cpp_file)}.exe")
    
    try:
        # Compile the code
        compile_result = subprocess.run(
            ["g++", cpp_file, "-o", executable],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if compile_result.returncode != 0:
            os.unlink(cpp_file)
            return False, f"Compilation error: {compile_result.stderr}"
        
        # Run the compiled code
        run_result = subprocess.run(
            [executable],
            input=input_data,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        output = run_result.stdout.strip()
        
        # Clean up
        os.unlink(cpp_file)
        if os.path.exists(executable):
            os.unlink(executable)
            
        if run_result.returncode != 0:
            return False, f"Runtime error: {run_result.stderr}"
            
        return True, output
        
    except subprocess.TimeoutExpired:
        if os.path.exists(cpp_file):
            os.unlink(cpp_file)
        if os.path.exists(executable):
            os.unlink(executable)
        return False, "Timeout: Code took too long to execute"
    except Exception as e:
        if os.path.exists(cpp_file):
            os.unlink(cpp_file)
        if os.path.exists(executable):
            os.unlink(executable)
        return False, f"Error: {str(e)}"

def run_java_code(code: str, input_data: str) -> Tuple[bool, str]:
    """Compile and run Java code with given input."""
    # Extract class name from code
    class_match = re.search(r'public\s+class\s+(\w+)', code)
    if not class_match:
        return False, "Error: Could not find public class name in Java code"
    
    class_name = class_match.group(1)
    java_file = os.path.join("submissions", f"{class_name}.java")
    
    try:
        # Write the code to a file
        with open(java_file, 'w') as f:
            f.write(code)
        
        # Compile the code
        compile_result = subprocess.run(
            ["javac", java_file],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if compile_result.returncode != 0:
            os.unlink(java_file)
            return False, f"Compilation error: {compile_result.stderr}"
        
        # Run the compiled code
        run_result = subprocess.run(
            ["java", "-cp", "submissions", class_name],
            input=input_data,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        output = run_result.stdout.strip()
        
        # Clean up
        os.unlink(java_file)
        class_file = os.path.join("submissions", f"{class_name}.class")
        if os.path.exists(class_file):
            os.unlink(class_file)
            
        if run_result.returncode != 0:
            return False, f"Runtime error: {run_result.stderr}"
            
        return True, output
        
    except subprocess.TimeoutExpired:
        if os.path.exists(java_file):
            os.unlink(java_file)
        class_file = os.path.join("submissions", f"{class_name}.class")
        if os.path.exists(class_file):
            os.unlink(class_file)
        return False, "Timeout: Code took too long to execute"
    except Exception as e:
        if os.path.exists(java_file):
            os.unlink(java_file)
        class_file = os.path.join("submissions", f"{class_name}.class")
        if os.path.exists(class_file):
            os.unlink(class_file)
        return False, f"Error: {str(e)}"

def calculate_code_diff(submitted_code: str, question_id: str, language: str) -> str:
    """
    Calculate the difference between original boilerplate and submitted code.
    Returns only the code added/modified by the user.
    """
    # Get original boilerplate
    original_boilerplate = get_boilerplate(question_id, language)
    
    # Remove comments for comparison
    def clean_comments(code: str, language: str) -> str:
        if language == "python":
            code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
        else:  # cpp or java
            code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
            code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
        return code
    
    # Clean comments but preserve structure
    clean_boilerplate = clean_comments(original_boilerplate, language)
    clean_submission = clean_comments(submitted_code, language)
    
    # Remove whitespace for tokenization
    tokenized_boilerplate = re.sub(r'\s+', ' ', clean_boilerplate).strip()
    tokenized_submission = re.sub(r'\s+', ' ', clean_submission).strip()
    
    # For accurate character counting, remove all whitespace
    char_count_boilerplate = re.sub(r'\s+', '', clean_boilerplate)
    char_count_submission = re.sub(r'\s+', '', clean_submission)
    
    # If the submission is identical to boilerplate (no changes), return empty string
    if char_count_submission == char_count_boilerplate:
        return ""
    
    # If submission contains exact boilerplate, extract added parts
    user_code = ""
    
    # First try a simple detection for complete added functions or blocks
    # This works better for structural additions like helper functions
    if language == "cpp" or language == "java":
        # Find all function declarations not in boilerplate
        boilerplate_functions = set(re.findall(r'\b\w+\s+\w+\s*\([^)]*\)\s*{', tokenized_boilerplate))
        all_functions = re.findall(r'\b\w+\s+\w+\s*\([^)]*\)\s*{', tokenized_submission)
        
        for func in all_functions:
            if func not in boilerplate_functions and "solution" not in func:
                # Calculate character count for this added function
                # Find the full function body
                func_pattern = re.escape(func.replace('{', '').strip()) + r'\s*{'
                func_match = re.search(func_pattern, clean_submission)
                
                if func_match:
                    start_pos = func_match.start()
                    # Find matching closing brace
                    brace_count = 0
                    in_function = False
                    
                    for i, c in enumerate(clean_submission[start_pos:]):
                        if c == '{':
                            brace_count += 1
                            in_function = True
                        elif c == '}' and in_function:
                            brace_count -= 1
                            if brace_count == 0:
                                # Extract and count the full function
                                full_func = clean_submission[start_pos:start_pos+i+1]
                                user_code += re.sub(r'\s+', '', full_func)
                                break
    
    # If still empty or for Python, fall back to a different approach
    if not user_code:
        # Get the solution function from both
        if language == "python":
            solution_pattern = r'def\s+solution\s*\([^)]*\)\s*:(.*?)(?=\n\s*(?:def|class|if\s+__name__|#)|\Z)'
        elif language == "cpp":
            solution_pattern = r'int\s+solution\s*\([^)]*\)\s*{(.*?)}'
        elif language == "java":
            solution_pattern = r'public\s+static\s+int\s+solution\s*\([^)]*\)\s*{(.*?)}'
            
        boilerplate_solution = re.search(solution_pattern, clean_boilerplate, re.DOTALL)
        submission_solution = re.search(solution_pattern, clean_submission, re.DOTALL)
        
        if boilerplate_solution and submission_solution:
            # Get just the solution body
            boilerplate_body = boilerplate_solution.group(1)
            submission_body = submission_solution.group(1)
            
            # Count chars in modified solution body
            if boilerplate_body != submission_body:
                solution_user_code = re.sub(r'\s+', '', submission_body)
                user_code += solution_user_code
        
        # Calculate the total difference between submission and boilerplate
        # Count total characters added
        if len(char_count_submission) > len(char_count_boilerplate):
            remaining_chars = len(char_count_submission) - len(char_count_boilerplate)
            
            # If still no user code found through pattern matching
            if not user_code:
                # Count everything that's added
                user_code = char_count_submission[-remaining_chars:]
    
    # Fallback: if still empty but clearly different, count all non-matching characters
    if not user_code and char_count_submission != char_count_boilerplate:
        # Just count the difference in length
        user_code = "x" * (len(char_count_submission) - len(char_count_boilerplate))
    
    return user_code

def evaluate_submission(code: str, language: str, question_id: str) -> Dict[str, Any]:
    """Evaluate a code submission and return results."""
    # Verify question exists
    if question_id not in questions:
        return {
            "passed": False,
            "score": 0,
            "char_count": 0,
            "max_score": 100,
            "details": f"Question ID {question_id} not found"
        }
    
    # Verify language is supported
    if language not in ["python", "cpp", "java"]:
        return {
            "passed": False,
            "score": 0,
            "char_count": 0,
            "max_score": 100,
            "details": f"Language {language} not supported"
        }
    
    question = questions[question_id]
    test_cases = question["test_cases"]
    
    # Run all test cases first with the full code
    for test_case in test_cases:
        input_data = test_case["input"]
        expected_output = test_case["expected_output"]
        
        if language == "python":
            success, output = run_python_code(code, input_data)
        elif language == "cpp":
            success, output = run_cpp_code(code, input_data)
        elif language == "java":
            success, output = run_java_code(code, input_data)
        
        if not success:
            return {
                "passed": False,
                "score": 0,
                "char_count": 0,
                "max_score": 100,
                "details": output
            }
        
        # Compare outputs
        if output.strip() != expected_output.strip():
            return {
                "passed": False,
                "score": 0,
                "char_count": 0,
                "max_score": 100,
                "details": f"Test failed: Expected '{expected_output}', got '{output}'"
            }
    
    # Calculate the user-added code by diffing with original boilerplate
    user_code = calculate_code_diff(code, question_id, language)
    
    # Store the extracted user code for debugging
    user_code_file = os.path.join("submissions", f"last_user_code_{language}.txt")
    with open(user_code_file, 'w') as f:
        f.write(f"Original Code:\n{code}\n\nUser Added Code:\n{user_code}")
    
    # Count characters in user-added code (whitespace already removed)
    char_count = len(user_code)
    
    # Make sure char_count is at least 1 to avoid division by zero
    char_count = max(1, char_count)
    
    # Calculate score
    optimal_length = question["language_optimal_lengths"][language]
    score = 100 * (optimal_length / char_count)
    # Cap score at 100
    score = min(score, 100)
    
    return {
        "passed": True,
        "score": score,
        "char_count": char_count,
        "max_score": 100,
        "details": "All test cases passed"
    }

# Function that can be called from API or CLI
def process_submission(code: str, language: str, question_id: str) -> Dict[str, Any]:
    """Process a submission and return evaluation results."""
    return evaluate_submission(code, language, question_id)

# Get formatted questions for API
def get_formatted_questions():
    """Return questions with generated boilerplate code."""
    formatted_questions = {}
    
    for qid, question in questions.items():
        formatted_question = {
            "id": qid,
            "description": question["description"],
            "test_cases": question["test_cases"],
            "boilerplate": {}
        }
        
        # Generate boilerplate code for each language
        for language in ["python", "cpp", "java"]:
            formatted_question["boilerplate"][language] = get_boilerplate(qid, language)
        
        formatted_questions[qid] = formatted_question
    
    return formatted_questions

# For testing directly from command line
if __name__ == "__main__":
    # Example usage
    python_code = """
def solution(n):
    if n <= 1:
        return n
    return solution(n-1) + solution(n-2)

if __name__ == "__main__":
    n = int(input())
    print(solution(n))
    """
    
    result = process_submission(python_code, "python", "q1")
    print(json.dumps(result, indent=2))
    
    # Print an example of what the frontend API needs to provide
    print("\nExample input format from frontend/database:")
    print(json.dumps({
        "q1": {
            "description": "the nth Fibonacci number",
            "parameter_name": "n",
            "language_optimal_lengths": {
                "python": 30,
                "cpp": 45,
                "java": 54
            },
            "test_cases": [
                {"input": "5", "expected_output": "5"},
                {"input": "7", "expected_output": "13"}
            ]
        }
    }, indent=2)) 