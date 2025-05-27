import { useEffect, useState } from "react";
import "./App.css";
import { EventType } from "./enums/EventType.enum";
import type { IStreamingResponse } from "./interfaces/IStreamingResponse.interface";

// const source = new EventSource("http://localhost:5000/api/run-workflow");

// source.onmessage = (event) => {
//   const data = JSON.parse(event.data);
//   if (data.type === EventType.PROGRESS) {
//     console.log(`Progress: ${data.data.type} - ${data.data.message}`);
//   } else if (data.type === EventType.FINAL) {
//     console.log(`Final Result: ${data.data}`);
//     source.close();
//   }
// };

// source.onerror = (event) => {
//   // if (event.target?.readyState === EventSource.CLOSED) {
//   //   console.log("Connection closed.");
//   //   return;
//   // }

//   console.error("EventSource failed:", event);
//   source.close();
// };

// source.onopen = (event) => {
//   console.log(`Connection opened.\n event: ${event}`);
// };

function App() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>("");
  const [statusType, setStatusType] = useState<string>("");
  const [streamContent, setStreamContent] = useState<string>("");

  useEffect(() => {
    if (streamContent.length > 0) {
      // if (statusType !== EventType.COMPANY_EVENT) {
      //   setStatusType('');
      // }
      setLoading(false);
    }
  }, [streamContent, statusType]);

  const handleClick = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await fetch("http://localhost:5000/api/run-workflow", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Access-Control-Allow-Origin": "*",
        },
        body: JSON.stringify({ company: "monday.com", attendees: ["Maya Asher"] }),
      });

      const reader = response.body?.getReader();
      if (!reader) throw new Error("No reader available");

      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const decodedChunk = decoder.decode(value, { stream: true });
        buffer += decodedChunk;

        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (!line.trim()) continue;

          try {
            const event: IStreamingResponse = JSON.parse(line);

            if (event.type === EventType.PROGRESS) {
              setStatusType(event.data.type);
              setStreamContent(event.data.message);
              console.log(`Progress: ${event.data.type} - ${event.data.message}`);
            } else if (event.type === EventType.FINAL) {
              setStatusType(event.type);
              setStreamContent(JSON.stringify(event.data));
              console.log(`Final Result: ${event.data}`);
              // source.close();
            }
          } catch (e) {
            console.error("Error parsing event:", e);
          }
        }
      }
    } catch (error) {
      console.error("Error fetching meeting data:", error);
      setError("Error analyzing meetings. Please try again.");
      setLoading(false);
    }
  };

  return (
    <main className="l-main">
      {loading && (
        <div className="loader-container">
          <section className="c-loader">
            <span className="c-loader__item"></span>
            <span className="c-loader__item"></span>
            <span className="c-loader__item"></span>
            <span className="c-loader__item"></span>
            <span className="c-loader__item"></span>
          </section>
          <p className="loader-container__loading-text">Processing, please wait</p>
        </div>
      )}

      {error && !loading && <div className="c-error">{error}</div>}

      {streamContent && !loading && (
        <div className="l-stream-content">
          <p>{streamContent}</p>
        </div>
      )}

      <form action="" onSubmit={handleClick}>
        <div className="c-form_field">
          <label htmlFor="company" className="c-form__label">
            Company
          </label>
          <input type="text" name="company" id="company" className="c-form_input" />
        </div>
        <div className="c-form_field">
          <label htmlFor="attendees" className="c-form__label">
            Attendees
          </label>
          <small>
            List attendees separated by commas or semicolons (e.g. Mike Spring; Kate Benson)
          </small>
          <input type="text" name="attendees" id="attendees" className="c-form_input" />
        </div>
        <div className="c-form_field">
          <button disabled={loading} className="c-form__button">
            Analyze
          </button>
        </div>
      </form>
    </main>
  );
}

export default App;
