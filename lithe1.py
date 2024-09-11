import streamlit as st
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain_community.tools.ddg_search import DuckDuckGoSearchRun
from langchain_ollama import ChatOllama
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain_experimental.agents import create_pandas_dataframe_agent
import pandas as pd


# Load the CSV file and display an error message if it fails
try:
    filename = './inputdata.csv'
    df = pd.read_csv(filename)
    df_head = df.head()
except Exception as e:
    st.error("Could not read CSV file. Check to make sure it exists and is properly formatted...")
    st.stop()

agent = create_pandas_dataframe_agent(ChatOllama(model="llama3.1"), df, agent_type="tool-calling", verbose=True, allow_dangerous_code=True)
#agent.invoke("Who is the youngest person on the ship, and what is their age?")

# Streamlit UI setup
st.title("LITHE1 - Lightweight Intelligent Tool for Handling Exports")
st.write("Ask questions about your CSV file below.")

# Display the DataFrame and add search functionality
st.write("### CSV File Preview")
st.write(df)

# Text input for user question
userinput = st.text_input("Enter a question:", "")

if userinput:
    with st.spinner('Processing your question...'):
        response = agent.invoke(userinput)

        # Display the result
        if response:
            st.write("### Answer:")
            st.text(response['output'])
        else:
            st.error("Could not find an answer to the question, please try again...")
    response = ""
