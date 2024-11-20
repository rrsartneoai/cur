import streamlit as st
import plotly.graph_objects as go
from dotenv import load_dotenv
import os
import google.generativeai as genai
import json

# Load environment variables
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel('gemini-pro')

st.title("Smart Grid Chatbot")

# Initialize chat history in session state if it doesn't exist
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def get_gemini_response(user_input):
    try:
        # Create a prompt that focuses on smart grid topics
        prompt = f"""You are a smart grid expert assistant. Please provide information about: {user_input}
        If the question is related to data or metrics, include some sample numerical data that could be visualized.
        Format your response as a JSON with these keys:
        - explanation: Your main response
        - data: If applicable, provide relevant numerical data as a list
        - labels: If providing data, include labels as a list
        """
        
        response = model.generate_content(prompt)
        return json.loads(response.text)
    except Exception as e:
        st.error(f"Error getting response from Gemini: {str(e)}")
        return None

def create_visualization(data, labels):
    fig = go.Figure(data=[go.Bar(x=labels, y=data)])
    fig.update_layout(
        title="Smart Grid Metrics",
        xaxis_title="Categories",
        yaxis_title="Values"
    )
    return fig

# Chat interface
user_input = st.text_input("Ask a question about the smart grid:")

if user_input:
    st.write(f"You asked: {user_input}")
    try:
        response = get_gemini_response(user_input)
        
        if response:
            # Display the explanation
            st.write("Response:", response['explanation'])
            
            # Add to chat history
            st.session_state.chat_history.append({"user": user_input, "bot": response['explanation']})
            
            # Create visualization if data is available
            if 'data' in response and 'labels' in response:
                st.write("Visualization:")
                fig = create_visualization(response['data'], response['labels'])
                st.plotly_chart(fig)
        
        # Display chat history
        if st.session_state.chat_history:
            st.write("Chat History:")
            for chat in st.session_state.chat_history:
                st.write(f"You: {chat['user']}")
                st.write(f"Bot: {chat['bot']}")
                st.write("---")

    except Exception as e:
        st.error(f"Error: {str(e)}")
