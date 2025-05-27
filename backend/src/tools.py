import os
from llama_index.core.workflow import Context, Event, HumanResponseEvent, InputRequiredEvent
from llama_index.tools.tavily_research import TavilyToolSpec
from llama_index.core.schema import Document
from typing import List

tavily_api_key = os.environ.get("TAVILY_API_KEY", "")

tavily_tool = TavilyToolSpec(api_key=tavily_api_key)


async def search_web(query: str) -> List[Document] | str:
    """Search the web for the query and return the result.
    Args:
        query: The query to search for.
        
        Returns:
            results: A list of dictionaries containing the results:
                url: The url of the result.
                content: The content of the result.
                
                If no results are found, it returns "No results found.
    """
    results = tavily_tool.search(query=query, max_results=3)
    if results:
        return results
    else:
        return "No results found."

