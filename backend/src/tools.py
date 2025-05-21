import os
from llama_index.core.workflow import Context, Event, HumanResponseEvent, InputRequiredEvent
from llama_index.tools.tavily_research import TavilyToolSpec
from llama_index.core.schema import Document
from typing import List

tavily_api_key = os.environ.get("TAVILY_API_KEY", "")

tavily_tool = TavilyToolSpec(api_key=tavily_api_key)


async def get_user_approve(ctx: Context) -> str:
    """Get the user's approval for the task.
    Returns:
        the user's response. If the user approves, it returns "yes", otherwise "no".
    """
    # emit an event to the external stream to be captured
    ctx.write_event_to_stream(
        InputRequiredEvent(
            # **Event(user_name="Konstantin"),
            prefix="Agent is trying to call a tool. Do you approve? (yes/no)",
        )
    )

    # wait until we see a HumanResponseEvent
    response = await ctx.wait_for_event(
        # waiter_id="waiter_1",
        event_type=HumanResponseEvent,
        # waiter_event=InputRequiredEvent(
        #     prefix="question",
        #     **Event(user_name="Konstantin"),
        # ),
        requirements={"user_name": "Konstantin"},
        timeout=10, # in seconds for the case where requirements are not met, otherwise it will wait for 2000 seconds by default which is ~30 minutes
    )

    # act on the input from the event
    if response.response.strip().lower() == "yes":
        return "yes"
    else:
        return "no"


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

