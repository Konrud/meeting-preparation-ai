import os
from dotenv import load_dotenv
from utils.logger import consoleLogger, timeFileLogger
from fastapi import Request
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from llama_index.core.workflow import Context
from src.workflow import ProgressWorkflow
from src.events import ProgressEvent

# Load environment variables
load_dotenv()

app = FastAPI()

# Configure CORS to allow requests from Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/run-workflow")
async def run_workflow_endpoint(request: Request):
    try:
        payload = await request.json()
    except HTTPException as e:
        raise HTTPException(
            status_code=400, detail={"message": f"Invalid JSON: {str(e)}"}
        )

    try:
        # Initialize the workflow timeout for 3 minutes
        progress_workflow = ProgressWorkflow(verbose=True, timeout=180)

        mock_company_name = os.environ.get("MOCK_COMPANY_NAME")
        mock_attendees = os.environ.get("MOCK_ATTENDEES")

        company = payload.get("company", mock_company_name)
        attendees = payload.get("attendees", mock_attendees)

        # Context
        ctx = Context(workflow=progress_workflow)

        await ctx.set("meeting_info", {"company": company, "attendees": attendees})

        workflow_handler = progress_workflow.run(ctx=ctx)

        # Async generator to yield events to the frontend
        async def event_generator():

            async for event in workflow_handler.stream_events():
             
             if isinstance(event, ProgressEvent):
                  print(f"\n{'=' * 20}") 
                  print(f"Progress event: {event.message=}\n")
                  yield json.dumps({
                        "type": "progress",
                        "data": {
                            "type": event.type.value,
                            "message": event.message
                        }
                    }) + "\n"
                
            # Yield the final result after all progress events
            final_result = await workflow_handler 

            yield json.dumps({
                "type": "final",
                "data": final_result
            }) + "\n"

        debug333 = 333

        return StreamingResponse(event_generator(), media_type="application/json")

    except Exception as e:
        exception_text = f"Error running llamaindex main\n: {e}"
        consoleLogger.error(exception_text)
        timeFileLogger.error(exception_text)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)