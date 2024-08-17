import streamlit as st
import pandas as pd
import requests  # Use requests to make HTTP requests
import config  # Import the config module where the API key is stored

# Use the API key from config.py
api_key = config.API_KEY_1

# Initialize data storage
queries_dump = []
queries_output_dump = []


# Initialize session state for queries and outputs
if 'queries_df' not in st.session_state:
    st.session_state.queries_df = pd.DataFrame(columns=['Serial Number', 'Content'])
if 'output_df' not in st.session_state:
    st.session_state.output_df = pd.DataFrame(columns=['Serial Number', 'Content'])

# Load existing data or create new DataFrame
try:
    queries_df = pd.read_excel('queries_data.xlsx', sheet_name='Queries Dump')
    output_df = pd.read_excel('queries_data.xlsx', sheet_name='Queries Output')
except FileNotFoundError:
    queries_df = pd.DataFrame(columns=['Serial Number', 'Content'])
    output_df = pd.DataFrame(columns=['Serial Number', 'Content'])

# Streamlit app
st.title('AI Query Assistant')

# Input box for user query
user_query = st.text_input('Enter your query:')

# Reset button
if st.button('Reset'):
    st.session_state.queries_df = pd.DataFrame(columns=['Serial Number', 'Content'])
    st.session_state.output_df = pd.DataFrame(columns=['Serial Number', 'Content'])
    st.session_state.user_query = ''  # Clear the user query
    st.session_state.output_text = ''  # Clear the output text


if user_query:
    # Add to queries dump
    serial_number = len(queries_df) + 1
    new_row = pd.DataFrame({'Serial Number': [serial_number], 'Content': [user_query]})
    queries_df = pd.concat([queries_df, new_row], ignore_index=True)

    # Call the Perplexity API
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama-3.1-sonar-huge-128k-online",  # Use a valid model name
        "messages": [
            {"role": "system", "content": "You are an artificial intelligence assistant and you need to engage in a helpful, detailed, polite conversation with a user."},
            {"role": "user", "content": user_query},
        ]
    }

    try:
        response = requests.post("https://api.perplexity.ai/chat/completions", headers=headers, json=data)
        response.raise_for_status()  # Raise an error for bad responses
        result = response.json()

        # Display the output
        st.text_area('Output:', value=result['choices'][0]['message']['content'], height=200, max_chars=None, key=None)

        # Add to output dump
        new_output_row = pd.DataFrame({'Serial Number': [serial_number], 'Content': [result['choices'][0]['message']['content']]})
        output_df = pd.concat([output_df, new_output_row], ignore_index=True)

        # Save to Excel
        with pd.ExcelWriter('queries_data.xlsx') as writer:
            queries_df.to_excel(writer, sheet_name='Queries Dump', index=False)
            output_df.to_excel(writer, sheet_name='Queries Output', index=False)

    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred: {e}")
    
