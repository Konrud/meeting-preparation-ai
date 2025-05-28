import os
from llama_index.core.tools import FunctionTool
from llama_index.tools.tavily_research import TavilyToolSpec
from llama_index.core.schema import Document
from typing import List
from llama_index.core.tools.tool_spec.load_and_search import LoadAndSearchToolSpec

tavily_api_key = os.environ.get("TAVILY_API_KEY", "")

tavily_tool = TavilyToolSpec(api_key=tavily_api_key)


async def search_web(query: str) -> List[Document] | str:
    """Search the Internet for the query and return the result.
    Args:
        query (str): The query to search for.

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


# search_web_function_tool = FunctionTool.from_defaults(
#     fn=search_web,
#     name="search_web",
#     description="Searches the web for the given query and returns the result.",
# )

# search_web_tool = LoadAndSearchToolSpec.from_defaults(
#     tool=search_web_function_tool
# ).to_tool_list()

search_web_tool = FunctionTool.from_defaults(
    fn=search_web,
    name="search_web",
    description="Searches the web for the given query and returns the result.",
)