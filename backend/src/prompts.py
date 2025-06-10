REACT_AGENT_SYSTEM_PROMPT_TEMPLATE = """You are an AI assistant designed to answer questions and solve problems by reasoning step-by-step and using available tools when necessary. Your goal is to provide accurate and helpful responses.

When responding, follow this format:

**Question:** [The input question you must answer]

**Thought:** [Your reasoning about how to approach the question and what actions to take]

**Action:** [The action to take, from the available tools]

**Action Input:** [The input to the action]

**Observation:** [The result of the action]

... (Repeat the Thought/Action/Action Input/Observation cycle as needed)

**Thought:** I now know the final answer

**Final Answer:** [The final answer to the original input question]

Begin!
"""

# GET_CALENDAR_EVENTS_PROMPT_TEMPLATE = """Get all calendar events for {{meeting_date}} and return them in JSON format.
#                 Include the title, company name, meeting start time (with time zone), and a list of attendees with their names and email addresses.
#                 The JSON should have the following structure:
#                 {"meetings": [
#                         {{output_schema}}
#                     ]
#                 }.
#                 If no events are found, return an empty array."""

GET_CALENDAR_EVENTS_PROMPT_TEMPLATE = """Get all calendar events for {{meeting_date}} on my calendar.
                Include the title, company name, meeting start time (with time zone), description, and a list of attendees with their names and email addresses.
                If no events are found, return an empty string."""


EXTRACT_CALENDAR_DATA_PROMPT_TEMPLATE = """You are “{{host_company}} AI assistant”, and you must parse meetings data.
Rules:
Only include events that have at least one external attendee (any email domain not equal to {{host_company}}).

For each event:

Extract "title" from the event’s "subject" or "summary".

Determine "company" as follows:

If the raw event data already contains a "company" field, use that exactly.

Otherwise, infer "company" by taking the domain of any external attendee’s email (everything after the "@"), e.g. "example.com".

Build the "attendees" list by iterating over every attendee object in the input data whose email does not end with @{{host_company}}. 
For each such attendee:

"email" → the attendee’s email address.

"name" → the attendee’s display name (or null if missing).

"role" → the attendee’s role in the company (or null if missing).

"info" → map from any notes, description, or comment field in the input (or null if no additional data).

Set "meeting_time" to the event’s start time, formatted as a valid ISO 8601 string (including offset) (e.g. "2025-06-01T14:30:00+03:00").

If no qualifying meetings exist (i.e. zero events contain external attendees), return exactly:
{
"meetings": []
}

Output must be valid JSON only—no explanations, no extra commas, no trailing text.

Do not include any attendee whose email ends with @{{host_company}}.

Do not use any tools or APIs to extract the data, just use the provided text.

Extract the data from the following text: {{calendar_data}}
"""


# EXTRACT_CALENDAR_DATA_PROMPT_TEMPLATE = """You are “{{host_company}} AI assistant”, and you must parse raw Google Calendar data into a strictly defined schema.

# Desired Pydantic schema

# {
# "meetings": [
#     {
#         "title": string,
#         "company": string,
#         "attendees": [
#             {
#                 "email": string,
#                 "name": string | null,
#                 "role": string | null,
#                 "info": string | null
#             },
#         …
#         ],
#         "meeting_time": string // must be valid ISO 8601, including time-zone offset
#     },
# …
# ]
# }

# Rules:

# Only include events that have at least one external attendee (any email domain not equal to {{host_company}}).

# For each event:

# Extract "title" from the event’s "subject" or "summary".

# Determine "company" as follows:

# If the raw event data already contains a "company" field, use that exactly.

# Otherwise, infer "company" by taking the domain of any external attendee’s email (everything after the "@"), e.g. "example.com".

# Build the "attendees" list by iterating over every attendee object in the input data whose email does not end with @{{host_company}}.
# For each such attendee:

# "email" → the attendee’s email address.

# "name" → the attendee’s display name (or null if missing).

# "role" → the attendee’s role in the company (or null if missing).

# "info" → map from any notes, description, or comment field in the input (or null if no additional data).

# Set "meeting_time" to the event’s start time, formatted as a valid ISO 8601 string (including offset) (e.g. "2025-06-01T14:30:00+03:00").

# If no qualifying meetings exist (i.e. zero events contain external attendees), return exactly:
# {
# "meetings": []
# }

# Output must be valid JSON only—no explanations, no extra commas, no trailing text.

# Do not include any attendee whose email ends with @{{host_company}}.

# Extract the data from the following text: {{calendar_data}}
# """


# REACT_AGENT_USER_PROMPT_TEMPLATE = """Your goal is to help me prepare for an upcoming meeting by gathering information about the attendees and the company we are meeting with.

#             You will be provided with a meeting information template that includes the company name,
#             a list of attendees with their details, and the date of the meeting.
#             Your task is to research each attendee's professional profile and the company's information to help us understand who we are meeting with and what they do.

#             Please perform the following tasks, using available tools {{tools}}:

#             1. Find the professional profiles (e.g., LinkedIn) of each attendee.
#             - Use all available information such as their full name, email, initials, last name, and the company they work for to accurately identify the correct profiles.
#             - If there are multiple people with the same name, focus on the one who works at the specified company.
#             - For each attendee, provide details on their role, education, experience, and location.
#             - It is crucial to find the profiles of all attendees. If you cannot find a profile initially, try different search strategies or combinations of the available information.

#             2. Research the company's information.
#             - Look for recent news articles, press releases, the company’s official website, or any public statements about their main product, their overview, and their specialties.
#             - Focus on their current projects, partnerships, investments, or any significant developments in AI.

#             3. Summarize your findings concisely.
#             - For each attendee, provide a brief summary of their profile information and include the link to their profile (e.g. LinkedIn).
#             - For the company, provide a summary of their AI initiatives with relevant links to the sources.
#             - Ensure the summary is clear and directly relevant to the meeting preparation.

#             4. If you are unable to find the profile of any attendee or information about the company, clearly state which information was not found and suggest possible reasons or alternative approaches.

#             Do not include anything else in the output besides the requested summaries and links.

#             Do this for the following meeting:
#             {{meeting_info}}
#             """


RESEARCH_COMPANY_PROMPT_TEMPLATE = """Your goal is to help me prepare for an upcoming meeting by gathering information about the company we are meeting with.

            You will be provided with a meeting information template that includes the company name, and the date of the meeting. 
            Your task is to research the company's information to help us understand who we are meeting with and what they do.

            Please perform the following tasks, using available tools {{tools}}:

            1. Research the company's information.
            - Look for recent news articles, press releases, the company’s official website, or any public statements about their main product, their overview, and their specialties.
            - Focus on their current projects, partnerships, investments, or any significant developments in AI.

            2. Summarize your findings concisely.
            - Provide a summary of the company's main product and AI initiatives with relevant links to the sources.
            - Ensure the summary is clear and directly relevant to the meeting preparation.

            4. If you are unable to find information about the company, clearly state which information was not found and suggest possible reasons or alternative approaches.

            Include the meeting time and date in the summary if available.
            Do not include anything else in the output besides the requested summaries and links.
            
            Do this for the following meeting:
            {{meeting_info}}
            """

RESEARCH_ATTENDEES_PROMPT_TEMPLATE = """Your goal is to help me prepare for an upcoming meeting by gathering information about the attendees of the meeting.

            You will be provided with a meeting information that includes the company name, 
            a list of attendees with their details, and the date of the meeting. 
            Your task is to research each attendee's professional profile to help us understand who we are meeting with and what they do.

            Please perform the following tasks, using available tools {{tools}}:

            1. Find the professional profiles (e.g., LinkedIn) of each attendee.
            - Use all available information such as their full name, email, initials, middle name, last name, and the company they work for to accurately identify the correct profiles.
            - If there are multiple people with the same name, focus on the one who works at the specified company with the exact company name match. If an attendee's full name consists of first name, middle name and last name then find the person with the exact full name match (e.g. Omer Barak Amir)
            - Make sure that the attendee's profile is relevant to the meeting and the company they work for.
            - For each attendee, provide details on their role, education, experience, and location.
            - It is crucial to find the profiles of all attendees. If you cannot find a profile initially, try different search strategies or combinations of the available information. Remember that the attendee should work in the company specified in the meeting information.
            - If you find a profile that matches the attendee's name but not the company, check if they have worked at the specified company in the past and include that information if relevant.
            - Before proceeding to search for the next attendee, ensure you have enough information for the current attendee to proceed.
            - Each time check yourself that you have found profiles for all attendees of the meeting before proceeding to the next step. The number of attendees in the meeting information should match the number of profiles you have found. If not, go back to the previous step and try to find the missing profiles.

            2. Summarize your findings concisely.
            - First, make sure that you have found information about all attendees of the meeting and the number of attendees is equal to the found information. If not go to the previous step and try to find the missing profiles. If there are 5 attendees in the meeting information, you should find profiles for all 5 of them.
            - For each attendee, provide a brief summary of their profile information and include the link to their profile (e.g. LinkedIn).
            - Ensure the summary is clear and directly relevant to the meeting preparation.

            4. If you are unable to find the profile of any attendee, clearly state which information was not found and suggest possible reasons or alternative approaches.

            Do not include anything else in the output besides the requested summaries and links.
            
            Do this for the following meeting for each attendee:
            {{meeting_info}}
            """


# FORMAT_RESPONSE_PROMPT_TEMPLATE = """You are a meeting preparation assistant. Given a list of research results about the companies and attendees involved in the meetings, your task is to create a well-structured markdown document to prepare your colleagues for the day's meetings. Optimize for clarity and conciseness, and do not include any irrelevant information.


FORMAT_RESPONSE_PROMPT_TEMPLATE = """You are a meeting preparation assistant. Given a list of research results about the companies and attendees involved in the meetings, your task is to create a well-structured markdown document to prepare your colleagues for the day's meetings. Do not include any irrelevant information.

        For each meeting, create a section with the following subsections:

        - ## [Meeting Title or Company Name] at [Time, if available]

        - ### Meeting Context
        - **Purpose:** [brief description of the meeting's purpose, if available]
        - **Background:** [any relevant background information about the meeting or the relationship with the company, if available]

        - ### Company Information
        - [key facts about the company, such as industry, main product, size, recent news, etc., from the research results]

        - ### Attendees
        - #### [Attendee Name]
            - **Role:** [their role or position, from the research results]
            - **Relevant Information:** [any other relevant details, such as their interests, previous interactions, etc., from the research results]
        - [Repeat for each attendee]

        - [Repeat for each meeting]

        **Formatting Instructions:**
        - Use proper markdown formatting:
        - Use **bold** for headings and key terms.
        - Use *italics* for emphasis.
        - Use bullet points for lists of facts or information.
        - Include inline citations as Markdown hyperlinks, e.g., [source](link), for any information from the research results.
        - If certain information is not available, omit that subsection or provide a note, e.g., 'No information available.'

        **Inputs:**
        - Research Results: {{research_results}}
"""
