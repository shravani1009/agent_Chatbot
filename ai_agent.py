# if you dont use pipenv uncomment the following:
# from dotenv import load_dotenv
# load_dotenv()

#Step1: Setup API Keys for Groq, OpenAI and Tavily
import os

GROQ_API_KEY=os.environ.get("GROQ_API_KEY")
TAVILY_API_KEY=os.environ.get("TAVILY_API_KEY")
OPENAI_API_KEY=os.environ.get("OPENAI_API_KEY")

#Step2: Setup LLM & Tools
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults

openai_llm=ChatOpenAI(model="gpt-4o-mini")
groq_llm=ChatGroq(model="llama-3.3-70b-versatile")

search_tool=TavilySearchResults(max_results=2)

#Step3: Setup AI Agent with Search tool functionality
from langgraph.prebuilt import create_react_agent
from langchain_core.messages.ai import AIMessage

system_prompt="Act as an AI chatbot who is smart and friendly"

def get_response_from_ai_agent(llm_id, messages, allow_search, system_prompt, provider):
    try:
        if provider == "Groq":
            llm = ChatGroq(model=llm_id, api_key=GROQ_API_KEY)
        elif provider == "OpenAI":
            llm = ChatOpenAI(model=llm_id, api_key=OPENAI_API_KEY)
        else:
            return {"error": "Invalid provider"}

        from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

        # Convert dict messages to LangChain message types
        formatted_messages = [SystemMessage(content=system_prompt)]
        for msg in messages:
            if msg["role"] == "user":
                formatted_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                formatted_messages.append(AIMessage(content=msg["content"]))

        try:
            response = llm.invoke(formatted_messages)
            return {"response": response.content if hasattr(response, 'content') else str(response)}
        except Exception as e:
            return {"error": f"LLM Error: {str(e)}"}
            
    except Exception as e:
        return {"error": f"General Error: {str(e)}"}