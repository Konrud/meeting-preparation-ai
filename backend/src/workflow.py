import os
from dotenv import load_dotenv
from llama_index.core.agent.workflow import ReActAgent
from llama_index.core.workflow import StartEvent, StopEvent, Workflow, step, Context
from llama_index.core.prompts import RichPromptTemplate
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from src.enums import ProgressEventType
from src.events import ProgressEvent
from src.prompts import REACT_AGENT_SYSTEM_PROMPT_TEMPLATE
from src.tools import get_user_approve, search_web
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

            model = AzureOpenAI(
                azure_endpoint=azure_endpoint,
                engine="gpt-4o",
                api_version=azure_open_ai_api_version,
                model="gpt-4o",
                azure_ad_token_provider=token_provider,
                use_azure_ad=True,
            )

            system_prompt_template = REACT_AGENT_SYSTEM_PROMPT_TEMPLATE

            system_prompt_raw = RichPromptTemplate(system_prompt_template)

            system_prompt = system_prompt_raw.format(
                    tool=search_web.__name__,
                    meeting_info="Company: monday.com, Attendees: Maya Asher",
                )

            self.agent = ReActAgent(
                name="searchAgent",
                description="Searches the web for the given query and returns the result.",
                tools=[search_web],
                system_prompt=system_prompt,
                llm=model,
            )
            
    @step
    async def init_step(self, ctx: Context, event: StartEvent) -> RunQueryEvent:

        ctx.write_event_to_stream(ProgressEvent(type=ProgressEventType.NEW, message="init_step is happening"))
        # Get model from the event (initiated when we run the workflow [e.g. workflow.run(model=model)])
        model = event.model

        # Add the model to the state in the context [ctx.get("state")] which is always defined by the framework
        current_state = {"model": model}
        print(f"{current_state=}")

        await ctx.set("state", current_state)

        return RunQueryEvent(run_query_output="First event output")

    @step
    async def run_query_step(self, ctx: Context, event: RunQueryEvent) -> FinalEvent:

        ctx.write_event_to_stream(ProgressEvent(type=ProgressEventType.NEW, message="run_query_step is happening"))

        current_state = await ctx.get("state")

        if current_state is None:
            raise ValueError("State not found in context")

        # model = cast(OpenAI, current_state["model"])
        


        generator = await model.astream_complete(
            prompt="Give me first paragraph of David Copperfield book by Charles Dickens in the public domain. Provide only the book's text. Do not add any additional information."
        )

        response = None

        async for response in generator:
            #  Allow the workflow to stream the response delta
            ctx.write_event_to_stream(
                ProgressEvent(type=ProgressEventType.NEW, message=response.delta or "response delta is empty")
            )

        return FinalEvent(
            final_output="\nRun Query step is complete, full response is attached",
            response=str(response),
        )

    @step
    async def finish_step(self, ctx: Context, event: FinalEvent) -> StopEvent:
        ctx.write_event_to_stream(ProgressEvent(type=ProgressEventType.NEW, message="finish_step is happening"))
        return StopEvent(result="Finish Step -> Stop")

