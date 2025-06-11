import { useEffect, useState, type FormEvent } from "react";
import "./App.css";
import { EventType } from "./enums/EventType.enum";
import type { IStreamingResponse } from "./interfaces/IStreamingResponse.interface";
import { formatDate } from "./utilities/date";
import ReactMarkdown from "react-markdown";

function App() {
  const [loading, setLoading] = useState(false);
  const [isManualData, setIsManualData] = useState(false);
  const [error, setError] = useState<string>("");
  const [statusType, setStatusType] = useState<string>("");
  const [streamContent, setStreamContent] = useState<string[]>([]);
  const [finalResponse, setFinalResponse] = useState<string>("");

  useEffect(() => {
    if (streamContent.length > 0) {
      setLoading(false);
    }
  }, [streamContent, statusType]);

  const handleClick = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    const formData = new FormData(e.currentTarget);

    const dataToSend: {
      date?: string;
      company?: string;
      attendees?: string[];
      excludeEmails?: string[];
    } = {};

    if (!isManualData) {
      const date = formData.get("date");
      const excludeEmails = formData.get("excludeEmails");

      dataToSend.date = date ? date.toString() : "";
      dataToSend.excludeEmails = (excludeEmails as string).split(/[,\s]\s*/);
    } else {
      const company = formData.get("company") || "";
      const attendees = formData.get("attendees") || "";
      dataToSend.company = company as string;
      dataToSend.attendees = (attendees as string).split(/[,\s]\s*/);
    }

    try {
      const response = await fetch("http://localhost:5000/api/run-workflow", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Access-Control-Allow-Origin": "*",
        },
        body: JSON.stringify(dataToSend),
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
              setStreamContent((prev) => [...prev, event.data.message]);
              console.log(
                `Progress: ${event.data.type} - ${event.data.message}`
              );
            } else if (event.type === EventType.FINAL) {
              setStatusType(event.type);
              setFinalResponse(event.data.toString());
              console.log(`Final Result: ${event.data}`);
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

  const handleManualDataChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const isChecked = e.target.checked;

    setIsManualData(isChecked);
  };

  return (
    <main className="l-main">
      <form action="" onSubmit={handleClick} className="c-form">
        <fieldset
          disabled={loading || isManualData}
          className="c-form__fieldset"
        >
          <div className="c-form_field">
            <label htmlFor="date" className="c-form__label">
              Meeting date
            </label>
            <small>Meeting date in your Google Calendar</small>
            <input
              type="date"
              name="date"
              id="date"
              className="c-form_input"
              required={!isManualData}
            />
          </div>
          <div className="c-form_field">
            <label htmlFor="excludeEmails" className="c-form__label">
              Emails to exclude from research
              <small>(your email or emails of your colleagues)</small>
            </label>
            <small className="c-form__input-hint">
              List of emails to exclude from the research separated by commas or
              whitespace (e.g. mike_spring@mike.com, katebenson@kate.com).
            </small>
            <input
              type="email"
              name="excludeEmails"
              id="excludeEmails"
              className="c-form_input"
              multiple
              required={!isManualData}
            />
          </div>
        </fieldset>

        <fieldset disabled={loading} className="c-form__fieldset">
          <div className="c-form_field">
            <label htmlFor="manualData" className="c-form__label">
              Add data manually
            </label>
            <input
              type="checkbox"
              name="manualData"
              id="manualData"
              className="c-form_input"
              onChange={handleManualDataChange}
            />
          </div>
        </fieldset>

        <fieldset
          disabled={loading || !isManualData}
          className="c-form__fieldset"
        >
          <div className="c-form_field">
            <label htmlFor="company" className="c-form__label">
              Company
            </label>
            <input
              type="text"
              name="company"
              id="company"
              className="c-form_input"
              required={isManualData}
            />
          </div>
          <div className="c-form_field">
            <label htmlFor="attendees" className="c-form__label">
              Attendees
            </label>
            <small className="c-form__input-hint">
              List of attendees' emails separated by commas or whitespace (e.g.
              mike_spring@mike.com, katebenson@kate.com)
            </small>
            <input
              type="email"
              name="attendees"
              id="attendees"
              className="c-form_input"
              multiple
              required={isManualData}
            />
          </div>
        </fieldset>

        <div className="c-form_field">
          <button disabled={loading} className="c-form__button">
            Analyze
          </button>
        </div>
      </form>

      {loading && (
        <div className="loader-container">
          <section className="c-loader">
            <span className="c-loader__item"></span>
            <span className="c-loader__item"></span>
            <span className="c-loader__item"></span>
            <span className="c-loader__item"></span>
            <span className="c-loader__item"></span>
          </section>
          <p className="loader-container__loading-text">
            Processing, please wait
          </p>
        </div>
      )}

      {error && !loading && <div className="c-error">{error}</div>}

      {streamContent?.length > 0 && !loading && (
        <div className="l-stream-content">
          <ul>
            {streamContent.map((value, i) => {
              const currentDate = formatDate({
                date: new Date(),
                locale: Intl.DateTimeFormat().resolvedOptions().locale,
              });
              return (
                <li key={i}>
                  <time>{currentDate}</time>
                  <p>{value}</p>
                </li>
              );
            })}
          </ul>
        </div>
      )}

      {streamContent?.length > 0 && !loading && finalResponse && (
        <div className="l-final-response">
          <h2>Final Response</h2>
          <div className="l-final-response__content">
            <ReactMarkdown>{finalResponse}</ReactMarkdown>
          </div>
        </div>
      )}
    </main>
  );
}

export default App;
