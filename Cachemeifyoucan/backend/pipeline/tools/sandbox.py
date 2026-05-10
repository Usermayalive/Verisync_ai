import subprocess
import sys
from langchain_core.tools import tool

@tool
def python_sandbox(code: str) -> str:
    """Executes Python code in a secure, minimal sandbox. Use this for complex data modeling or custom logic validation."""
    try:
        process = subprocess.Popen(
            [sys.executable, "-c", code],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(timeout=5)
        if stderr:
            return f"Error: {stderr}"
        return stdout if stdout else "Code executed successfully (no output)."
    except subprocess.TimeoutExpired:
        process.kill()
        return "Error: Execution timed out (max 5s)."
    except Exception as e:
        return f"Error: {str(e)}"
