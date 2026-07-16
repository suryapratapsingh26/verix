import os
import numexpr
from tavily import TavilyClient


def calculator(expression: str) -> str:
    try:
        result = numexpr.evaluate(expression.strip())
        return str(result.item())
    except Exception as e:
        return f"ERROR: Invalid expression - {e}"


_tavily_client = None

def web_search(query: str) -> str:
    global _tavily_client
    if _tavily_client is None:
        _tavily_client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

    try:
        response = _tavily_client.search(query=query, max_results=3)
        results = response.get("results", [])
        if not results:
            return "No results found."

        lines = []
        for r in results:
            title = r.get("title", "")
            snippet = (r.get("content") or "")[:200]
            lines.append(f"- {title}: {snippet}")
        return "\n".join(lines)
    except Exception as e:
        return f"ERROR: search failed - {e}"