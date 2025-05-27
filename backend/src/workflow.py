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
from src.events import FinalEvent, FormatEvent, ProgressEvent, ResearchEvent
from src.prompts import FORMAT_RESPONSE_PROMPT_TEMPLATE, REACT_AGENT_USER_PROMPT_TEMPLATE
from src.tools import search_web
from utils.logger import consoleLogger, timeFileLogger
from llama_index.llms.azure_openai import AzureOpenAI

# Load environment variables
load_dotenv()

class ProgressWorkflow(Workflow):
    
    def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            
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
            
        except Exception as e:
            exception_text = f"Error running {self.init_step.__name__}\n: {e}"
            consoleLogger.error(exception_text)
            timeFileLogger.error(exception_text)
            raise WorkflowRuntimeError(exception_text)

        return ResearchEvent()

    @step
    async def research_step(self, ctx: Context, event: ResearchEvent) -> FormatEvent:
        """Use ReAct agent to search for information about the company and meeting attendees"""
        
        try:
            ctx.write_event_to_stream(ProgressEvent(type=ProgressEventType.PROCESSING, message="ReAct agent is running"))
                
            search_prompt_raw = RichPromptTemplate(REACT_AGENT_USER_PROMPT_TEMPLATE)

            meeting_info = await ctx.get("meeting_info")

            if not meeting_info:
                raise ValueError("Meeting information is not available in the context.")
            
            search_prompt = search_prompt_raw.format(meeting_info=meeting_info)
            
            handler = self.agent.run(user_msg=search_prompt, ctx=ctx)

            # response = await self.agent.run(user_msg=search_prompt, ctx=ctx)
            
            # current_agent = None

            # async for handler_event in handler.stream_events():

            #     if (
            #         hasattr(handler_event, "current_agent_name")
            #         and handler_event.current_agent_name != current_agent
            #     ):
            #         current_agent = handler_event.current_agent_name
            #         print(f"\n{'='*20}")
            #         print(f"🤖 Agent: {current_agent}")
            #         print(f"{'='*20}\n")

            #     elif isinstance(handler_event, AgentOutput):
            #         if handler_event.response.content:
            #             print(f"{'='*20}\n")
            #             print("📤 Agent Output:", handler_event.response.content)
            #             print(f"{'='*20}\n")
            #         if handler_event.tool_calls:
            #             print(f"{'='*20}\n")
            #             print(
            #                 "🛠️  Planning to use tools:",
            #                 [call.tool_name for call in handler_event.tool_calls],
            #             )
            #             print(f"{'='*20}\n")

            #     elif isinstance(handler_event, ToolCall):
            #         print(f"{'='*20}\n")
            #         print(f"🔨 Calling Tool: {handler_event.tool_name}\n")
            #         print(f"  With arguments: {handler_event.tool_kwargs}\n")
            #         print(f"{'='*20}\n")

            #     elif isinstance(handler_event, ToolCallResult):
            #         print(f"🔧 Tool Call Result: ({handler_event.tool_name})\n")
            #         print(f"  Arguments: {handler_event.tool_kwargs}\n")
            #         print(f"  Output: {handler_event.tool_output}\n")
            #         print(f"{'='*20}\n")
            
            
            # Get the final response
            response = await handler
            print(f"\n===\nresponse: {str(response)}\n===\n")
            
            
        except Exception as e:
            exception_text = f"Error running {self.research_step.__name__}\n: {e}"
            consoleLogger.error(exception_text)
            timeFileLogger.error(exception_text)
            raise WorkflowRuntimeError(exception_text)


        return FormatEvent(
            message="\nResearch step is complete, full response is attached",
            response=str(response),
        )
        
    @step
    async def format_step(self, ctx: Context, event: FormatEvent) -> FinalEvent:
        """Format the response"""
        
        try: 
            ctx.write_event_to_stream(ProgressEvent(type=ProgressEventType.FORMATTING, message="the response is being formatted"))
        
            format_prompt_raw = RichPromptTemplate(FORMAT_RESPONSE_PROMPT_TEMPLATE)
                
            format_prompt = format_prompt_raw.format(research_results=event.response)
            
            formatted_response = await self.model.acomplete(prompt=format_prompt)
        
        except Exception as e:
            exception_text = f"Error running {self.format_step.__name__}\n: {e}"
            consoleLogger.error(exception_text)
            timeFileLogger.error(exception_text)
            raise WorkflowRuntimeError(exception_text)

        return FinalEvent(message="format step is complete", response=str(formatted_response.raw))
    
    @step
    async def finish_step(self, ctx: Context, event: FinalEvent) -> StopEvent:
        ctx.write_event_to_stream(ProgressEvent(type=ProgressEventType.COMPLETED, message="finish_step is happening"))
        return StopEvent(message="Finish Step -> Stop", result=event.response)

