import json
import os
from datetime import datetime
from typing import List
from dotenv import load_dotenv
from llama_index.core import set_global_handler

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
from src.events import (
    CalendarDataParserEvent,
    CalendarDataRetrievalEvent,
    FinalEvent,
    FormatEvent,
    ProgressEvent,
    ProgressWorkflowStartEvent,
    ResearchEvent,
)
from src.models.calendar_data import CalendarData
from src.models.meeting import Meeting
from src.prompts import (
    EXTRACT_CALENDAR_DATA_PROMPT_TEMPLATE,
    FORMAT_RESPONSE_PROMPT_TEMPLATE,
    GET_CALENDAR_EVENTS_PROMPT_TEMPLATE,
    REACT_AGENT_SYSTEM_PROMPT_TEMPLATE,
    REACT_AGENT_USER_PROMPT_TEMPLATE,
)
from src.tools import search_web_tool
from llama_index.core.tools import FunctionTool, ToolMetadata
from llama_index.tools.mcp import BasicMCPClient, aget_tools_from_mcp_url
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
        open_ai_model = os.environ.get("OPEN_AI_MODEL", "")

        self.model = AzureOpenAI(
            azure_endpoint=azure_endpoint,
            engine=open_ai_model,
            api_version=azure_open_ai_api_version,
            model=open_ai_model,
            azure_ad_token_provider=token_provider,
            use_azure_ad=True,
        )

        self.agent = ReActAgent(
            name="searchAgent",
            description="Searches the web for the given query and returns the result.",
            # tools=search_web_tool,
            tools=[search_web_tool],
            llm=self.model,
            # system_prompt=REACT_AGENT_SYSTEM_PROMPT_TEMPLATE,
        )

        phoenix_api_key = os.environ.get("PHOENIX_API_KEY", "")
        os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"api_key={phoenix_api_key}"
        set_global_handler("arize_phoenix", endpoint="https://llamatrace.com/v1/traces")

    @step
    async def init_step(
        self, ctx: Context, event: ProgressWorkflowStartEvent
    ) -> CalendarDataRetrievalEvent | ResearchEvent:

        try:
            ctx.write_event_to_stream(
                ProgressEvent(
                    type=ProgressEventType.INIT, message="init_step is happening"
                )
            )

            meeting_date = event.date

            if meeting_date:
                ctx.write_event_to_stream(
                    ProgressEvent(
                        type=ProgressEventType.INIT,
                        message=f"Meeting date is set to {meeting_date}",
                    )
                )

                return CalendarDataRetrievalEvent(date=meeting_date)

            elif event.attendees and event.company:
                ctx.write_event_to_stream(
                    ProgressEvent(
                        type=ProgressEventType.INIT,
                        message=f"Attendees: {event.attendees}, Company: {event.company}",
                    )
                )
                return ResearchEvent(attendees=event.attendees, company=event.company)

            else:
                exception_text = (
                    "Meeting date, attendees, or company information is missing."
                )
                consoleLogger.error(exception_text)
                timeFileLogger.error(exception_text)
                raise WorkflowRuntimeError(exception_text)

        except Exception as e:
            exception_text = f"Error running {self.init_step.__name__}\n: {e}"
            consoleLogger.error(exception_text)
            timeFileLogger.error(exception_text)
            raise WorkflowRuntimeError(exception_text)

    @step
    async def get_calendar_data_step(
        self, ctx: Context, event: CalendarDataRetrievalEvent
    ) -> CalendarDataParserEvent:
        """Get calendar data and store it in the context"""

        try:
            ctx.write_event_to_stream(
                ProgressEvent(
                    type=ProgressEventType.CALENDAR_DATA_RETRIEVAL,
                    message="Retrieving calendar data",
                )
            )

            # For now we will be using Google Calendar API to get the meeting info
            google_calendar_mcp_config = {
                "mcpServers": {
                    "google_calendar": {
                        "command": "node",
                        "args": [os.getenv("GOOGLE_CALENDAR_MCP_CONFIG", "")],
                    }
                },
            }

            # https://docs.llamaindex.ai/en/stable/examples/tools/mcp/
            # async
            tools = await aget_tools_from_mcp_url("http://127.0.0.1:8000/mcp")
            # ! CONTINUE HERE

            # Create MCPClient from the config dictionary
            mcp_client = MCPClient.from_dict(google_calendar_mcp_config)

            mcp_agent = MCPAgent(llm=self.model, client=mcp_client, max_steps=30)

            meeting_date = event.date

            if not meeting_date:
                raise ValueError(
                    "Meeting date is required for calendar data retrieval."
                )

            # Run the query to get the meeting information
            mcp_agent_prompt_raw = RichPromptTemplate(
                template_str=GET_CALENDAR_EVENTS_PROMPT_TEMPLATE
            )

            mcp_agent_prompt = mcp_agent_prompt_raw.format(meeting_date=meeting_date)

            # calendar_data = await mcp_agent.run(f"What is on my calendar for {date}. Include the meeting title, time, and the attendees - names and emails.")
            calendar_data = await mcp_agent.run(mcp_agent_prompt)

            # meeting_info = await ctx.get("meeting_info")
            # ctx.set("meetings_state, {...})

        except Exception as e:
            exception_text = (
                f"Error running {self.get_calendar_data_step.__name__}\n: {e}"
            )
            consoleLogger.error(exception_text)
            timeFileLogger.error(exception_text)
            raise WorkflowRuntimeError(exception_text)

        return CalendarDataParserEvent(calendar_data=calendar_data)

    @step
    async def calendar_data_parser_step(
        self, ctx: Context, event: CalendarDataParserEvent
    ) -> ResearchEvent:
        """Parse the calendar data and extract meeting information"""

        try:
            ctx.write_event_to_stream(
                ProgressEvent(
                    type=ProgressEventType.CALENDAR_DATA_PARSER,
                    message="Parsing calendar data",
                )
            )

            calendar_data = event.calendar_data

            if not calendar_data:
                raise ValueError("No calendar data found.")

            extract_calendar_data_prompt_raw = RichPromptTemplate(
                template_str=EXTRACT_CALENDAR_DATA_PROMPT_TEMPLATE
            )

            extract_calendar_data_prompt = extract_calendar_data_prompt_raw.format(
                calendar_data=calendar_data,
                host_company=os.getenv("MOCK_HOST_COMPANY_NAME", "gmail"),
            )

            response_as_pydantic_obj: CalendarData = self.model.structured_predict(
                CalendarData, extract_calendar_data_prompt
            )

            calendar_data_item = response_as_pydantic_obj

            calendar_events = []

            for meeting in calendar_data_item.meetings:
                # Convert datetime ISO 8601 to "Hour:Minute AM/PM" format
                if meeting.meeting_time:
                    # Parse the ISO formatted string into a datetime object
                    dt_object = datetime.fromisoformat(meeting.meeting_time)

                    # Format the datetime object to "Hour:Minute AM/PM"
                    # %I for hour on a 12-hour clock, %M for minute, %p for locale's equivalent of either AM or PM.
                    formatted_time = dt_object.strftime("%I:%M %p")
                    meeting.meeting_time = formatted_time

                # company = meeting.company

                # event_data = {
                #     "company": company,
                #     "title": meeting.title,
                #     "attendees": {},
                #     "meeting_time": meeting.meeting_time,
                # }
                ctx.write_event_to_stream(
                    ProgressEvent(
                        type=ProgressEventType.CALENDAR_EVENT,
                        message="Processing calendar event: "
                        f"{meeting.title} at {meeting.meeting_time} with {len(meeting.attendees)} attendees",
                    )
                )

                calendar_events.append(meeting.model_dump_json())

            # Store the meeting information in the context
            # await ctx.set("meeting_info", meeting_info)

        except Exception as e:
            exception_text = (
                f"Error running {self.calendar_data_parser_step.__name__}\n: {e}"
            )
            consoleLogger.error(exception_text)
            timeFileLogger.error(exception_text)
            raise WorkflowRuntimeError(exception_text)

        return ResearchEvent(calendar_events=calendar_events)

    @step
    async def research_step(self, ctx: Context, event: ResearchEvent) -> FormatEvent:
        """Use ReAct agent to search for information about the company and meeting attendees"""

        try:
            ctx.write_event_to_stream(
                ProgressEvent(
                    type=ProgressEventType.RESEARCH,
                    message="Research step is running",
                )
            )

            search_prompt_raw = RichPromptTemplate(REACT_AGENT_USER_PROMPT_TEMPLATE)

            # meeting_info = await ctx.get("meeting_info")

            # if not meeting_info:
            #     raise ValueError("Meeting information is not available in the context.")

            # search_prompt = search_prompt_raw.format(
            #     meeting_info=meeting_info,
            #     # tools=[search_web_tool[0].metadata.name]
            #     tools=[search_web_tool.metadata.name],
            # )

            # calendar_events: List[str] = []

            if not event.calendar_events and event.attendees and event.company:
                calendar_event = {
                    "attendees": event.attendees,
                    "company": event.company,
                }
                calendar_events = [json.dumps(calendar_event)]

            elif event.calendar_events:
                calendar_events = event.calendar_events

            else:
                raise ValueError(
                    "either attendees and company name or calendar events must be provided."
                )

            search_prompt = search_prompt_raw.format(
                meetings_info=calendar_events,
                tools=[search_web_tool.metadata.name],
            )

            handler = self.agent.run(
                user_msg=search_prompt,
            )

            async for handler_event in handler.stream_events():

                if isinstance(handler_event, AgentOutput):
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
            ctx.write_event_to_stream(
                ProgressEvent(
                    type=ProgressEventType.FORMATTING,
                    message="the response is being formatted",
                )
            )

            format_prompt_raw = RichPromptTemplate(FORMAT_RESPONSE_PROMPT_TEMPLATE)

            format_prompt = format_prompt_raw.format(research_results=event.response)

            formatted_response = await self.model.acomplete(prompt=format_prompt)

        except Exception as e:
            exception_text = f"Error running {self.format_step.__name__}\n: {e}"
            consoleLogger.error(exception_text)
            timeFileLogger.error(exception_text)
            raise WorkflowRuntimeError(exception_text)

        return FinalEvent(
            # message="format step is complete", response=str(formatted_response.raw)
            message="format step is complete",
            response=str(formatted_response.text),
        )

    @step
    async def finish_step(self, ctx: Context, event: FinalEvent) -> StopEvent:
        ctx.write_event_to_stream(
            ProgressEvent(
                type=ProgressEventType.COMPLETED, message="finish_step is happening"
            )
        )
        return StopEvent(message="Finish Step -> Stop", result=event.response)
