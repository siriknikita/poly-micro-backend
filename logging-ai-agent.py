import os
import json
from typing import TypedDict, Optional

from dotenv import load_dotenv


from langchain_core.tools import tool

from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
import requests
import google.generativeai as genai
from enum import Enum
from pydantic import BaseModel, field_validator, Field

# Pydantic Models for Logs
class Severity(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class LogBase(BaseModel):
    project_id: str
    service_id: str
    test_id: Optional[str] = None
    func_id: Optional[str] = None
    message: str
    severity: Severity
    timestamp: Optional[str] = None
    source: Optional[str] = None

    @field_validator('severity', mode='before')
    @classmethod
    def uppercase_severity(cls, value: any) -> str:
        # Ensure value is a string and uppercase
        s_value = str(value).upper()
        
        # Map "WARN" to "WARNING"
        if s_value == "WARN":
            return "WARNING"
        
        # Return the (potentially mapped) uppercase string
        return s_value
    
    class Config:
        arbitrary_types_allowed = True

class Log(LogBase):
    id: str
    
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


load_dotenv()


class ChatState(TypedDict):
    messages: list


gemini_api_key_for_langchain = os.getenv("GEMINI_API_KEY")
if not gemini_api_key_for_langchain:
    # This is a critical failure, so we raise an error to stop the script early.
    raise ValueError("GEMINI_API_KEY not found in environment variables. This is required for the main LLM.")
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", google_api_key=gemini_api_key_for_langchain, convert_system_message_to_human=True)

# Configure genai globally for direct use (e.g., in tools not using LangChain's ChatModel)
try:
    genai.configure(api_key=gemini_api_key_for_langchain)
    gemini_model_for_analysis = genai.GenerativeModel('gemini-1.5-flash-latest')
except Exception as e:
    # This is also a critical failure for the analysis tool.
    raise ValueError(f"Error configuring global Gemini model for analysis: {e}. Ensure GEMINI_API_KEY is valid.")

# Helper functions for log analysis
def fetch_project_logs(project_id: str) -> list[Log]:
    url = f"http://backend:8000/api/logs/project/{project_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        logs_data = response.json()
        return [Log(**log_data) for log_data in logs_data]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching logs from {url}: {e}")
        return []
    except json.JSONDecodeError: # json import is already available
        print(f"Error decoding JSON response from {url}")
        return []
    except Exception as e: # Catch pydantic validation errors too
        print(f"Error processing log data: {e}")
        return []

def analyze_logs_with_gemini(logs: list[Log]) -> str:
    # Now uses the globally configured gemini_model_for_analysis

    if not logs: # Initial list was empty
        return "No logs provided for analysis."

    log_entries_str = ""
    for log_item in logs:
        log_entries_str += (
            f"- Timestamp: {log_item.timestamp or 'N/A'}, "
            f"Severity: {log_item.severity.value if log_item.severity else 'N/A'}, "
            f"Service: {log_item.service_id or 'N/A'}, "
            f"Message: {log_item.message or 'N/A'}, "
            f"Source: {log_item.source or 'N/A'}\n"
        )

    # This check is for when logs list was not empty, but all items were essentially blank after formatting.
    if not log_entries_str and logs: 
        return "Fetched logs, but they appear to be empty or malformed after formatting."


    prompt = (
        "You are an expert log analyst. Please analyze the following logs and provide concise insights. "
        "Focus on identifying critical errors, recurring warnings, unusual patterns, or any anomalies that might require immediate attention. "
        "Summarize the overall health of the system based on these logs.\n\n"
        "Logs:\n"
        f"{log_entries_str}\n\n"
        "Insights:"
    )

    try:
        response = gemini_model_for_analysis.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return f"Error analyzing logs with Gemini: {e}"

class GetLogInsightsArgs(BaseModel):
    project_id: Optional[str] = Field(default="683036c1d66b42efae6b4cb6", description="The ID of the project to analyze. Defaults to '683036c1d66b42efae6b4cb6' if not provided.")

@tool(args_schema=GetLogInsightsArgs)
def get_log_insights(args: Optional[GetLogInsightsArgs] = None):
    """Fetches logs for a project, analyzes them using Gemini, and returns insights."""
    
    # If ToolNode/LLM doesn't pass an args object, create one to use defaults.
    invoked_args = args if args is not None else GetLogInsightsArgs()

    print(f"Tool 'get_log_insights' called for project_id: {invoked_args.project_id}")
    logs_list = fetch_project_logs(invoked_args.project_id)
    
    if not logs_list:
        # fetch_project_logs prints specific errors. This message is for the LLM.
        return "No logs were found for the project, or an error occurred while fetching them. Check console for details."
    
    insights = analyze_logs_with_gemini(logs_list)
    return insights


llm = llm.bind_tools([get_log_insights])



def llm_node(state):
    response = llm.invoke(state['messages'])
    return {'messages': state['messages'] + [response]}


def router(state):
    last_message = state['messages'][-1]
    return 'tools' if getattr(last_message, 'tool_calls', None) else 'end'


tool_node = ToolNode([get_log_insights])


def tools_node(state):
    result = tool_node.invoke(state)

    return {
        'messages': state['messages'] + result['messages']
    }


builder = StateGraph(ChatState)
builder.add_node('llm', llm_node)
builder.add_node('tools', tools_node)
builder.add_edge(START, 'llm')
builder.add_edge('tools', 'llm')
builder.add_conditional_edges('llm', router, {'tools': 'tools', 'end': END})

graph = builder.compile()


if __name__ == '__main__':
    state = {'messages': []}

    print('Type an instruction or "quit".\n')

    while True:
        user_message = input('> ')

        if user_message.lower() == 'quit':
            break

        state['messages'].append({'role': 'user', 'content': user_message})

        state = graph.invoke(state)

        print(state['messages'][-1].content, '\n')
