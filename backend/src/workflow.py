import os
from dotenv import load_dotenv
from llama_index.core.agent.workflow import ReActAgent
from llama_index.core.workflow import StartEvent, StopEvent, Workflow, step, Context
from llama_index.core.agent.workflow import (
    AgentOutput,
    ToolCall,
    ToolCallResult,
)
from llama_index.core.workflow.errors import WorkflowRuntimeError
from llama_index.core.prompts import RichPromptTemplate
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from src.enums import ProgressEventType
from src.events import FinalEvent, ProgressEvent, ResearchEvent
from src.prompts import REACT_AGENT_USER_PROMPT_TEMPLATE
from src.tools import search_web
from utils.logger import consoleLogger, timeFileLogger
from llama_index.llms.azure_openai import AzureOpenAI

# Load environment variables
load_dotenv()

class ProgressWorkflow(Workflow):
    
    def __init__(self):
            super().__init__()
            
            credential = DefaultAzureCredential()
            
            token_provider = get_bearer_token_provider(
                credential, "https://cognitiveservices.azure.com/.default"
            )

            azure_endpoint = os.environ.get("AZURE_ENDPOINT", "")
            azure_open_ai_api_version = os.environ.get("AZURE_OPEN_AI_API_VERSION", "")

            self.model = AzureOpenAI(
                azure_endpoint=azure_endpoint,
                engine="gpt-4o",
                api_version=azure_open_ai_api_version,
                model="gpt-4o",
                azure_ad_token_provider=token_provider,
                use_azure_ad=True,
            )

            # system_prompt_template = REACT_AGENT_SYSTEM_PROMPT_TEMPLATE

            # system_prompt_raw = RichPromptTemplate(system_prompt_template)

            # system_prompt = system_prompt_raw.format(tools=search_web.__name__)

            self.agent = ReActAgent(
                name="searchAgent",
                description="Searches the web for the given query and returns the result.",
                tools=[search_web],
                # system_prompt=system_prompt,
                llm=self.model,
            )
            
    @step
    async def init_step(self, ctx: Context, event: StartEvent) -> ResearchEvent:

        try:
            ctx.write_event_to_stream(ProgressEvent(type=ProgressEventType.INIT, message="init_step is happening"))
            # Get model from the event (initiated when we run the workflow [e.g. workflow.run(model=model)])
            # model = event.model

            # # Add the model to the state in the context [ctx.get("state")] which is always defined by the framework
            # current_state = {"model": model}
            # print(f"{current_state=}")

            # await ctx.set("state", current_state)
            
        except Exception as e:
            exception_text = f"Error running {self.init_step.__name__}\n: {e}"
            consoleLogger.error(exception_text)
            timeFileLogger.error(exception_text)
            raise WorkflowRuntimeError(exception_text)

        return ResearchEvent()

    @step
    async def research_step(self, ctx: Context, event: ResearchEvent) -> FinalEvent:
        """Use ReAct agent to search for information about the company and meeting attendees"""
        
        try:

            ctx.write_event_to_stream(ProgressEvent(type=ProgressEventType.PROCESSING, message="ReAct agent is running"))

            # current_state = await ctx.get("state")

            # if current_state is None:
            #     raise ValueError("State not found in context")

            # model = cast(OpenAI, current_state["model"])
                
            search_prompt_raw = RichPromptTemplate(REACT_AGENT_USER_PROMPT_TEMPLATE)
            
            search_prompt = search_prompt_raw.format(meeting_info="Company: monday.com, Attendees: Maya Asher")
            
            handler = self.agent.run(user_msg=search_prompt, ctx=ctx)
            
            current_agent = None

            async for handler_event in handler.stream_events():

                if (
                    hasattr(handler_event, "current_agent_name")
                    and handler_event.current_agent_name != current_agent
                ):
                    current_agent = handler_event.current_agent_name
                    print(f"\n{'='*20}")
                    print(f"🤖 Agent: {current_agent}")
                    print(f"{'='*20}\n")

                elif isinstance(handler_event, AgentOutput):
                    if handler_event.response.content:
                        print(f"{'='*20}\n")
                        print("📤 Agent Output:", handler_event.response.content)
                        print(f"{'='*20}\n")
                    if handler_event.tool_calls:
                        print(f"{'='*20}\n")
                        print(
                            "🛠️  Planning to use tools:",
                            [call.tool_name for call in handler_event.tool_calls],
                        )
                        print(f"{'='*20}\n")

                elif isinstance(handler_event, ToolCall):
                    print(f"{'='*20}\n")
                    print(f"🔨 Calling Tool: {handler_event.tool_name}\n")
                    print(f"  With arguments: {handler_event.tool_kwargs}\n")
                    print(f"{'='*20}\n")

                elif isinstance(handler_event, ToolCallResult):
                    print(f"🔧 Tool Call Result: ({handler_event.tool_name})\n")
                    print(f"  Arguments: {handler_event.tool_kwargs}\n")
                    print(f"  Output: {handler_event.tool_output}\n")
                    print(f"{'='*20}\n")

            # generator = await model.astream_complete(
            #     prompt="Give me first paragraph of David Copperfield book by Charles Dickens in the public domain. Provide only the book's text. Do not add any additional information."
            # )
            
            response = await handler
            print(f"\n===\nresponse: {str(response)}\n===\n")
            
            
                # #  Allow the workflow to stream the response delta
                # ctx.write_event_to_stream(
                #     ProgressEvent(type=ProgressEventType.NEW, message=response.delta or "response delta is empty")
                # )
        except Exception as e:
            exception_text = f"Error running {self.research_step.__name__}\n: {e}"
            consoleLogger.error(exception_text)
            timeFileLogger.error(exception_text)
            raise WorkflowRuntimeError(exception_text)

        return FinalEvent(
            message="\nRun Query step is complete, full response is attached",
            response=str(response),
        )

    @step
    async def finish_step(self, ctx: Context, event: FinalEvent) -> StopEvent:
        ctx.write_event_to_stream(ProgressEvent(type=ProgressEventType.COMPLETED, message="finish_step is happening"))
        return StopEvent(message="Finish Step -> Stop", result=event.response)

