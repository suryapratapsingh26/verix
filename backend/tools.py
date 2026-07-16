import numexpr


def calculator(expression: str) -> str:
    try:
        result = numexpr.evaluate(expression.strip())
        return str(result.item())
    except Exception as e:
        return f"ERROR: Invalid expression - {e}"