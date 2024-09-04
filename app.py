#----------------------------------------------------------------
################ Importing Libraries 
#----------------------------------------------------------------
import streamlit as st
import pandas as pd
import config
import requests  # Use requests to make HTTP requests
import os
from pathlib import Path
import pdfplumber
from transformers import pipeline  # Import Hugging Face pipeline
from langchain_community.chat_models import ChatPerplexity
# import transformers
# pipeline = transformers.pipeline
#from langchain import OpenAI, LLMChain, PromptTemplate  # Import LangChain modules
#from langchain.llms import OpenAI  # Correct import path for OpenAI
from langchain_openai import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

#----------------------------------------------------------------
################ API Keys 
#----------------------------------------------------------------
# Use the API key from config.py 
api_key = config.API_KEY_1  

#----------------------------------------------------------------
################ Basic Webapp UI
#----------------------------------------------------------------
# Streamlit app
st.title('ASK ANYTHING - Source from the Internet or your PDF document')

# Add a box on the top right corner
st.markdown(
    """
    <style>
    .top-right {
        position: fixed;
        top: 40px;
        right: 550px;
        background-color: #000 ;
        padding: 20px;
        border-radius: 50px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        z-index: 100;
    }
    </style>
    <div class="top-right">
        Created by Ayush Jha
    </div>
    """,
    unsafe_allow_html=True
)


# Input box for user query
user_query = st.text_input('Enter your query:')
st.write("User query input stage reached.")

# Query type selection
query_type = st.selectbox('Select the type of query:', 
                          ['Basic Information Retrieval', 'Analytical Query', 
                           'Summarization Request', 'Detailed Explanation', 
                           'Critical Review'])
st.write("Query type selection stage reached.")


#----------------------------------------------------------------
################ Input Query Stage 
# Stores query in excel, with input and output prompt with serial no.
#----------------------------------------------------------------
# Initialize data storage
queries_dump = []
queries_output_dump = []

# Initialize session state for queries and outputs
if 'queries_df' not in st.session_state:
    st.session_state.queries_df = pd.DataFrame(columns=['Serial Number', 'Content'])
if 'output_df' not in st.session_state:
    st.session_state.output_df = pd.DataFrame(columns=['Serial Number', 'Content'])

# Load existing data or create a new DataFrame
try:
    queries_df = pd.read_excel('queries_data.xlsx', sheet_name='Queries Dump')
    output_df = pd.read_excel('queries_data.xlsx', sheet_name='Queries Output')
except FileNotFoundError:
    queries_df = pd.DataFrame(columns=['Serial Number', 'Content'])
    output_df = pd.DataFrame(columns=['Serial Number', 'Content'])
    st.write("Excel data loaded successfully.")


#-----------------------------------------------------------------
########## Functions created 
# summarize_text
# extract_text_from_pdf
#-----------------------------------------------------------------
# Function to summarize the extracted PDF text if it's too long
def summarize_text(text, max_length=300):
    try:
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        summary = summarizer(text, 
                             max_length=max_length, 
                             min_length=100, 
                             do_sample=False,
                             clean_up_tokenization_spaces=True)[0]['summary_text']
        st.write("Text summarized successfully.")
        return summary
    except Exception as e:
        st.error(f'Summarization error: {e}')
        st.write("Error during text summarization.")
        return "Summarization failed."

 # Extract text from the uploaded PDF
def extract_text_from_pdf(pdf_path):
    text = ''
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + '\n'
    except Exception as e:
        st.error(f'Error extracting text: {e}')
        return None
    return text

#----------------------------------------------------------------
################ PDF Upload and Layout
#----------------------------------------------------------------
# Sidebar for PDF upload
st.sidebar.header('Upload PDF')
uploaded_file = st.sidebar.file_uploader('Choose a PDF file', type='pdf')
st.write("PDF upload stage reached.")

# Directory to save uploaded files
uploaded_dir = Path('uploaded_files')
if not uploaded_dir.exists():
    os.makedirs(uploaded_dir)

# Initialize session state for uploaded files
if 'uploaded_files' not in st.session_state:
    st.session_state['uploaded_files'] = []

extracted_text = None  # Initialize extracted_text

# Save uploaded file and display history
if uploaded_file is not None:
    # Save uploaded file
    file_path = uploaded_dir / uploaded_file.name
    with open(file_path, 'wb') as f:
        f.write(uploaded_file.getbuffer())
    st.sidebar.success('File uploaded successfully!')
    st.write("PDF file uploaded successfully.")
    # Extract text from the uploaded PDF
    extracted_text = extract_text_from_pdf(file_path)

    if extracted_text and len(extracted_text) > 1000:
        extracted_text = summarize_text(extracted_text)
        st.text_area('Extracted PDF Text:', value=extracted_text, height=200)
    else:
        st.write("No text extracted from PDF.")



# Show uploaded file names in sidebar history
# st.sidebar.write('Uploaded Files:')
# for file in uploaded_dir.iterdir():
#     st.sidebar.write(file.name)
#     st.sidebar.download_button(label='Download', data=file.read_bytes(), file_name=file.name)
st.sidebar.write('Uploaded Files:')
for file_name in st.session_state['uploaded_files']:
    st.sidebar.write(file_name)

#----------------------------------------------------------------
################ Text Preprocessing using Hugging Face 
#----------------------------------------------------------------
# Define a summarization pipeline using Hugging Face models (e.g., BART for summarization)
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")


# Summarize the extracted text if it exists and is long
if extracted_text and len(extracted_text) > 1000:
    extracted_text = summarize_text(extracted_text)
    st.text_area('Summarized PDF Text:', value=extracted_text, height=200)

#----------------------------------------------------------------
################ LangChain for Query Interaction 
#----------------------------------------------------------------
# Define a flexible template to handle different query types
template = """
You are an AI assistant capable of handling various tasks including basic information retrieval, detailed analysis, summarization, explanation, and critical review. Based on the following context, answer the user's query in the most appropriate manner.

Context:
{context}

Query:
{query}

Type of Query: {query_type}

Instructions:
For Basic Information Retrieval: Answer the user's query in a clear and concise manner.
For Analytical Query: Perform a detailed analysis and answer the user's query with supporting arguments.
For Summarization Request: Summarize the key points from the context and answer the user's query.
For Detailed Explanation: Explain the answer to the user's query in a detailed and easy-to-understand manner.
For Critical Review: Evaluate the content in the context provided and critically analyze it to answer the user's query.

Response:
"""



# Initialize LangChain with Perplexity
llm = ChatPerplexity(
    model="llama-3-sonar-small-32k-online",  # Choose a suitable model
    temperature=0.7
)
prompt = PromptTemplate(template=template, input_variables=["context", "query", "query_type"])
chain = LLMChain(llm=llm, prompt=prompt)

# Prepare the context for LangChain
context = extracted_text if extracted_text else "No PDF uploaded."

# Combine the query with the context and process using LangChain
if user_query:
    response = chain.run(context=context, query=user_query, query_type=query_type)
    st.text_area('LangChain Output:', value=response, height=200)
    st.write("LangChain processing complete.")

    # No need for separate Perplexity API call since it's integrated with LangChain
    # Display the final output
    st.text_area('Final Output:', value=response, height=200)

    # Add to output dump
    serial_number = len(queries_df) + 1
    new_row = pd.DataFrame({'Serial Number': [serial_number], 'Content': [user_query]})
    queries_df = pd.concat([queries_df, new_row], ignore_index=True)

    new_output_row = pd.DataFrame({'Serial Number': [serial_number], 'Content': [response]})
    output_df = pd.concat([output_df, new_output_row], ignore_index=True)

    # Save to Excel
    with pd.ExcelWriter('queries_data.xlsx') as writer:
        queries_df.to_excel(writer, sheet_name='Queries Dump', index=False)
        output_df.to_excel(writer, sheet_name='Queries Output', index=False)
    st.write("Data saved to Excel successfully.")
#----------------------------------------------------------------
################ Reset Functionality
#----------------------------------------------------------------
# Reset button to clear session states and data
if st.button('Reset'):
    st.session_state.queries_df = pd.DataFrame(columns=['Serial Number', 'Content'])
    st.session_state.output_df = pd.DataFrame(columns=['Serial Number', 'Content'])
    st.session_state.user_query = ''  # Clear the user query
    st.session_state.output_text = ''  # Clear the output text
    st.write("Session state reset.")