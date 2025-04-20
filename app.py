import streamlit as st
import os
from rwanda_trade_bot import RwandaTradeBot

# Set page configuration
st.set_page_config(
    page_title="Rwanda Trade Chatbot",
    page_icon="🇷🇼",
    layout="wide"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "bot" not in st.session_state:
    # Get API key from environment variable or Streamlit secrets
    openai_api_key = os.environ.get("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", None)
    
    if not openai_api_key:
        st.error("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
        st.stop()
    
    # Initialize the trade bot
    st.session_state.bot = RwandaTradeBot(openai_api_key=openai_api_key)

# Display header
st.title("Rwanda Trade Portal Chatbot")
st.markdown("""
Ask questions about import and export requirements for products in Rwanda.  
*Example: "What documents do I need to export coffee from Rwanda?" or "What are the fees for importing electronics?"*
""")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Get user input
if prompt := st.chat_input("Ask about Rwanda trade requirements..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Display assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")
        
        try:
            response = st.session_state.bot.query(prompt)
            message_placeholder.markdown(response)
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            message_placeholder.markdown(f"Error: {str(e)}")

# Display sidebar
with st.sidebar:
    st.title("About")
    st.markdown("""
    **Rwanda Trade Chatbot** helps you navigate import and export requirements for Rwanda.
    
    This tool provides information on:
    - Required documents
    - Import/export procedures
    - Fees and charges
    - Product-specific regulations
    
    Data is sourced from the [Rwanda Trade Portal](https://rwandatrade.rw).
    
    *This is a project for the course 17630.*
    """)
    
    # Add disclaimer
    st.caption("Disclaimer: This chatbot provides information for guidance purposes only. Always verify requirements with official sources.")

    # Add refresh button
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.experimental_rerun()