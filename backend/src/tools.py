import os
from llama_index.core.workflow import Context, Event, HumanResponseEvent, InputRequiredEvent
from llama_index.tools.tavily_research import TavilyToolSpec

tavily_api_key = os.environ.get("TAVILY_API_KEY", "")

tavily_tool = TavilyToolSpec(api_key=tavily_api_key)


def multiply(a: float, b: float) -> float:
    """Multiply two numbers and returns the product"""
    return a * b


def add(a: float, b: float) -> float:
    """Add two numbers and returns the sum"""
    return a + b


async def get_user_name(ctx: Context) -> str:
    """Get the user's name from database and save it in Context's state."""
    state = await ctx.get("state")
    # Assuming the user name is fetched from a database or some other source
    # Here we are just simulating it by setting a static value
    user_name = "Konstantin"
    state["user_name"] = user_name
    await ctx.set("state", state)
    return f"user name is set to {user_name}"


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


async def search_web(query: str) -> str:
    """Search the web for the query and return the result."""
    results = tavily_tool.search(query=query, max_results=1)
    if results:
        return results[0].text
    else:
        return "No results found."

async def record_notes(ctx: Context, notes: str, notes_title: str) -> str:
    """Record notes in the context's state.
    Args: notes: str: The notes to be recorded.
          notes_title: str: The title of the notes.
    Returns: str: The notes recorded in the context's state.
    """
    current_state = await ctx.get("state")

    research_notes_key = "research_notes"

    if research_notes_key not in current_state:
        current_state[research_notes_key] = {}
    
    current_state[research_notes_key][notes_title] = notes

    await ctx.set("state", current_state)

    return f"Notes recorded: {notes_title} - {notes}"

async def write_report(ctx: Context, report_content: str) -> str:
    """Write a report in the context's state on a given topic.
    Args: report_content: str: The content of the report.
    Returns: str
    """
    current_state = await ctx.get("state")
    
    current_state["report_content"] = report_content

    await ctx.set("state", current_state)

    return f"Report written"


async def review_report(ctx: Context, review: str) -> str:
    """Review the report and provide feedback.
    Returns: str: The report content.
    """
    current_state = await ctx.get("state")
    
    current_state["review"] = review

    await ctx.set("state", current_state)

    return f"Report reviewed"