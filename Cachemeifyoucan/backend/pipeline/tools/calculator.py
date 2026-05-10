from langchain_core.tools import tool
import numexpr

@tool
def calculate(expression: str) -> str:
    """Calculates a mathematical expression using numexpr. Useful for verifying financial or statistical data."""
    try:
        result = numexpr.evaluate(expression).item()
        return str(result)
    except Exception as e:
        return f"Error calculating {expression}: {str(e)}"
