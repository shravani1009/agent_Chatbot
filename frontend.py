# Step1: Setup UI with Streamlit (model provider, model, system prompt, web search, query)
import streamlit as st

st.set_page_config(page_title="LangGraph Agent UI", layout="centered")
st.title("AI Chatbot Agents")
st.write("Create and Interact with the AI Agents!")

system_prompt = st.text_area("Define your AI Agent: ", height=70, placeholder="Type your system prompt here...")

MODEL_NAMES_GROQ = ["llama-3.3-70b-versatile", "mixtral-8x7b-32768"]
MODEL_NAMES_OPENAI = ["gpt-4o-mini"]

provider = st.radio("Select Provider:", ("Groq", "OpenAI"))

if provider == "Groq":
    selected_model = st.selectbox("Select Groq Model:", MODEL_NAMES_GROQ)
elif provider == "OpenAI":
    selected_model = st.selectbox("Select OpenAI Model:", MODEL_NAMES_OPENAI)

allow_web_search = st.checkbox("Allow Web Search")

user_query = st.text_area("Enter your query: ", height=150, placeholder="Ask Anything!")

API_URL = "http://127.0.0.1:9999/chat"

# Initialize chat history in session state if it doesn't exist
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if st.button("Ask Agent!"):
    if user_query.strip():
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        
        # Display user message
        with st.chat_message("user"):
            st.write(user_query)
        
        # Step2: Connect with backend via URL
        import requests
        import json

        # The key fix - sending the message directly as a dictionary
        payload = {
            "model_name": selected_model,
            "model_provider": provider,
            "system_prompt": system_prompt if system_prompt else "You are a helpful assistant.",
            "messages": [
                {"role": "user", "content": user_query}
            ],
            "allow_search": allow_web_search
        }

        try:
            # Show loading message
            with st.spinner("Thinking..."):
                response = requests.post(API_URL, json=payload)
            
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    
                    # Extract the actual response content
                    if isinstance(response_data, str):
                        assistant_response = response_data
                    elif isinstance(response_data, dict):
                        if "error" in response_data:
                            assistant_response = f"Error: {response_data['error']}"
                        elif "response" in response_data:
                            assistant_response = response_data['response']
                        else:
                            assistant_response = "I received a response but couldn't understand it."
                    else:
                        assistant_response = "I received a response in an unexpected format."
                    
                    # Add assistant response to chat history
                    st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})
                    
                    # Display assistant response
                    with st.chat_message("assistant"):
                        st.write(assistant_response)
                        
                except ValueError:
                    # Handle JSON parsing error without showing raw response
                    with st.chat_message("assistant"):
                        error_msg = "I had trouble processing the response."
                        st.write(error_msg)
                    st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
            else:
                # Handle HTTP error without showing raw response
                with st.chat_message("assistant"):
                    error_msg = f"I couldn't get a response (Status code: {response.status_code})"
                    st.write(error_msg)
                st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
        except requests.exceptions.RequestException:
            # Handle request error without showing raw response
            with st.chat_message("assistant"):
                error_msg = "I couldn't connect to the AI service."
                st.write(error_msg)
            st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
    else:
        st.error("Please enter a valid query.")