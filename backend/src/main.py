import os
import asyncio
from dotenv import load_dotenv
from llama_index.core.agent.workflow import (
    AgentInput,
    AgentOutput,
    AgentStream,
    AgentWorkflow,
    FunctionAgent,
    ReActAgent,
    ToolCallResult,
)
from llama_index.core.workflow.events import Event
from llama_index.core.workflow import Context, InputRequiredEvent, HumanResponseEvent
from llama_index.llms.openai import OpenAI
from src.tools import get_user_approve, get_user_name, multiply, add, search_web
from utils.logger import consoleLogger, timeFileLogger

# Load environment variables
load_dotenv()


async def run_llamaindex_main():
    """
    https://docs.llamaindex.ai/en/stable/understanding/agent/
    """

    try:

        openai_api_key = os.environ.get("OPENAI_API_KEY", "")

        # --- Init Modal ---#
        model = OpenAI(model="gpt-4o-mini")

        # --------------------------
        #   Initialize the agent and AgentWorkflow
        # --------------------------
        math_agent = FunctionAgent(
            name="MathAgent",
            description="Performs basic mathematical operations.",
            tools=[multiply, add],
            llm=model,
            system_prompt="You are an agent that can perform basic mathematical operations using tools.",
        )

        user_agent = FunctionAgent(
            name="UserAgent",
            description="Gets the user's info (e.g. name, age, etc...).",
            tools=[get_user_name],
            llm=model,
            system_prompt="You are an agent that can receive data about the current user using appropriate tools.",
        )

        web_search_agent = FunctionAgent(
            name="WebSearchAgent",
            description="Search the web for information.",
            tools=[search_web, get_user_approve],
            llm=model,
            system_prompt="You are an agent that can receive a query and search the Internet for the answer using appropriate tool. Do not change the `query` that comes from user in any way, use it as is without adding or changing anything. You always ask for user approval, using specified tool, before using a tool for a search in the Internet. If you receive 'no' from the user, or requirements are not met, you should not proceed using a tool for the web search.",
        )

        manager_agent_sys_prompt = """
        You are a manager agent. You have the following agents at your disposal: MathAgent agent and UserAgent agent and WebSearchAgent. Use them to perform tasks. When the agents are not needed, you can ignore them. When an agent generates a response, use this response to create a final answer. Start the final answer with: 'FINAL ANSWER:'.
        """

        manager_agent = ReActAgent(
            name="managerAgent",
            description="Manages other agents and tasks",
            system_prompt=manager_agent_sys_prompt,
            llm=model,
            tools=[],
        )

        agent_workflow = AgentWorkflow(
            agents=[manager_agent, user_agent, math_agent, web_search_agent],
            root_agent="managerAgent",
        )

        # --------------------------
        #  Maintaining state by creating Context
        # --------------------------
        ctx = Context(agent_workflow)

        # --------------------------
        #
        # --------------------------

        # --------------------------
        # Handle single message input
        # --------------------------

        # response = await agent_workflow.run(
        #     user_msg="Hello, my name is Konstantin.",
        #     ctx=ctx,
        # )

        # print(f"\nAgent response:{response.response.content=}\n")

        # response = await agent_workflow.run(
        #     user_msg="What is the result of multiplying 5 and 5?",
        #     ctx=ctx,
        # )

        # print(f"\nAgent response:{response.response.content=}\n")

        # response = await agent_workflow.run(
        #     user_msg="What is my name?",
        #     ctx=ctx,
        # )

        # print(f"\nAgent response:{response.response.content=}\n")
        # consoleLogger.debug(response["messages"])

        # --------------------------
        # Using Stream
        # --------------------------

        # handler = agent_workflow.run(
        #     user_msg="Is the actor Val Kilmer still alive?",
        #     ctx=ctx,
        # )

        # async for event in handler.stream_events():

        #     if isinstance(event, AgentStream):
        #         print(f"{event.delta=}", end="", flush=True)

        #     elif isinstance(event, AgentInput):
        #         print(f"\n{'---' * 5}\n")
        #         print("Agent input: ", event.input)  # the current input messages
        #         print(
        #             "\nAgent name:", event.current_agent_name
        #         )  # the current agent name

        #     elif isinstance(event, AgentOutput):
        #         print(f"\n{'---' * 5}\n")
        #         print("Agent output: ", event.response)  # the current full response
        #         print(
        #             "\nTool calls made: ", event.tool_calls
        #         )  # the selected tool calls, if any
        #         print("\nRaw LLM response: ", event.raw)  # the raw llm api response

        #     elif isinstance(event, ToolCallResult):
        #         print(f"\n{'---' * 5}\n")
        #         print("Tool called: ", event.tool_name)  # the tool name
        #         print("\nArguments to the tool: ", event.tool_kwargs)  # the tool kwargs
        #         print("\nTool output: ", event.tool_output)  # the tool output

        #     # print final output
        #     print(f"\n{'---' * 5}\n")
        #     print(f"Final output:\n{str(await handler)}")

        # --------------------------
        # Human in the loop
        # --------------------------

        handler = agent_workflow.run(
            user_msg="Is the actor Val Kilmer still alive?",
            ctx=ctx,
        )

        async for event in handler.stream_events():

            if isinstance(event, InputRequiredEvent):
                # capture keyboard input
                response = input(event.prefix)

                if isinstance(handler.ctx, Context):

                    user_name = event.get("user_name", "John")

                    human_response_event = HumanResponseEvent(
                        **Event(user_name=user_name),
                        response=response,
                    )

                    # send our response back
                    handler.ctx.send_event(
                        human_response_event
                    )

            elif isinstance(event, AgentOutput):
                print(f"\n{'---' * 5}\n")
                print("Agent output: ", event.response)  # the current full response
                print(
                    "\nTool calls made: ", event.tool_calls
                )  # the selected tool calls, if any
                print("\nRaw LLM response: ", event.raw)  # the raw llm api response

            elif isinstance(event, ToolCallResult):
                print(f"\n{'---' * 5}\n")
                print("Tool called: ", event.tool_name)  # the tool name
                print("\nArguments to the tool: ", event.tool_kwargs)  # the tool kwargs
                print("\nTool output: ", event.tool_output)  # the tool output
        

        response = await handler
        print(str(response))

        debug333 = 333

    except Exception as e:
        exception_text = f"Error running llamaindex main\n: {e}"
        consoleLogger.error(exception_text)
        timeFileLogger.error(exception_text)
        raise ValueError(exception_text)


# Additional configurations
if __name__ == "__main__":

    asyncio.run(run_llamaindex_main())
