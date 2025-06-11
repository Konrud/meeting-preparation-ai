# 🗓️ Meeting Preparation AI

<div align="center">
  <img src="images/meeting-preparation-ai.gif" alt="Meeting Preparation AI Demo" width="600"/>
</div>

## 👋 Welcome to the Meeting Preparation AI!

This repository demonstrates how to build an intelligent meeting preparation agent with real-time web access, leveraging advanced search capabilities and seamless calendar integration. The agent connects to a Google Calendar via a Meeting Coordination Platform (MCP), retrieves relevant meeting information, and enriches it with up-to-date, cited insights from the web.

The project is designed for easy customization and extension, allowing you to:

- Integrate proprietary or internal data sources
- Modify the agent architecture or swap out LLMs
- Add additional Meeting Coordination Platform (MCP) integrations

---

## 🚀 Features

- 🌐 **Real-time Web Search:** Instantly fetches up-to-date information using a search API.
- 🧠 **Agentic Reasoning:** Combines MCP and ReAct agent flows for smarter, context-aware responses.
- 🔄 **Streaming Substeps:** See agentic reasoning and substeps streamed live for transparency.
- 🔗 **Citations:** All web search results are cited for easy verification.
- 🗓️ **Google Calendar Integration:** (via MCP) Access and analyze your meeting data.
- ⚡ **Async FastAPI Backend:** High-performance, async-ready backend for fast responses.
- 💻 **Modern React Frontend:** Interactive UI for dynamic user interactions.

---

## 📂 Repository Structure

- **Backend** ([`backend/`](./backend))
  - [`workflow.py`](./backend/src/workflow.py): Agentic flow (MCP + LlamaIndex)
  - **Server endpoint** ([`main.py`](./backend/src/main.py)): FastAPI server for API endpoints and streaming
- **Frontend** ([`frontend/`](./frontend/src)): React-based UI for meeting insights

---

## 🛠️ Local Setup

**Python version:** 3.13.3 (local development)

### Google Calendar MCP Setup

See [google-calendar-mcp](https://github.com/nspady/google-calendar-mcp) for full details.

**Google Cloud Setup:**

1. Go to the Google Cloud Console and create/select a project.
2. Enable the Google Calendar API.
3. Create OAuth 2.0 credentials:
   - Go to Credentials
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "User data" for the type of data that the app will be accessing
   - Add your app name and contact information
   - Select "Desktop app" as the application type
4. Add your email as a test user under the OAuth Consent screen.
5. Create a file `gcp-oauth.keys.json` in the root of `google-calendar-mcp` directory.
6. Download your credentials and paste them in `gcp-oauth.keys.json`.

This file should look like the following:

```json
{
  "installed": {
    "client_id": "<your-client-id>",
    "project_id": "<your-project-id>",
    "auth_uri": "<your-auth-uri>",
    "token_uri": "<your-token-uri>",
    "auth_provider_x509_cert_url": "<your-auth-provider>",
    "client_secret": "<your-secret>",
    "redirect_uris": ["http://localhost"]
  }
}
```

**Install the MCP:**

```bash
cd google-calendar-mcp
npm install
```

### Backend Setup

1. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   .\venv\Scripts\activate #on Windows
   ```
2. Install dependencies:
   ```bash
   python3 -m pip install -r requirements.txt
   ```
3. Set environment variables in `.env` file:
   ```bash
   TAVILY_API_KEY=<tavily-api-key>
   AZURE_ENDPOINT=<azure-api-key>
   AZURE_OPEN_AI_API_VERSION=<azure-openai-api-version>
   OPEN_AI_MODEL=<open-ai-model-name>
   PHOENIX_API_KEY=<phoenix-api-key> # for debugging agents flow
   ```
4. Run the backend server:
   ```bash
   python main.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```

---

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

---

## License

MIT
