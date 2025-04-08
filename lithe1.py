import streamlit as st
import ollama
import pandas as pd
import re
import subprocess
from ollama import chat
from ollama import ChatResponse
import platform
import subprocess
import shutil

model = "llama3.2"

def get_python_command():
    # Check if we're on Windows
    if platform.system() == "Windows":
        return "python"
    
    # For Linux/Mac, try to find python3 first
    python3_path = shutil.which("python3")
    if python3_path:
        return "python3"
    
    # Fall back to python if python3 is not available
    python_path = shutil.which("python")
    if python_path:
        return "python"
    
    # If neither is found, default to python3 (will likely fail but with a clearer error)
    return "python3"


# Function to extract Python code from AI response
def extract_code(response):
    code_pattern = re.compile(r"```python(.*?)```", re.DOTALL | re.IGNORECASE)  # Updated regex to match Python code blocks
    match = code_pattern.search(response)
    if match:
        code = match.group(1).strip()
    else:
        code = None  # Return None if no code block is found
    return code

# Function to rewrite user question for CSV analysis
def rewrite_question(user_question, df_columns):
    prompt = f"""
    You are an AI assistant specializing in data analysis. Your task is to rewrite the given question to make it more suitable for CSV data analysis using Python and pandas.

    CSV Column Names: {', '.join(df_columns)}

    Original Question: {user_question}

    Rewrite the question AND RESPOND WITH THE REWRITTEN QUESTION ONLY, NOTHING ELSE.  Do not provde any code:
    """

    response = chat(model=model, messages=[
        {
            'role': 'user',
            'content': prompt,
        },
    ])

    return response.message.content.strip()

try:
    filename = './inputdata.csv'
    # Specify data types and disable low_memory for consistent type inference
    df = pd.read_csv(filename, dtype=str, low_memory=False)
    df_head = df.head()
except Exception as e:
    st.error("Could not read CSV file. Check to make sure it exists and is properly formatted...")
    st.stop()

# Ensure Arrow compatibility before displaying in Streamlit
try:
    import pyarrow as pa
    pa.Table.from_pandas(df)
except Exception as e:
    st.error(f"DataFrame is not Arrow-compatible: {e}")
    st.stop()


# Streamlit UI setup
st.title("LITHE1 - Lightweight Intelligent Tool for Handling Exports")
st.write("Ask questions about your CSV file below.")

# Display the DataFrame and add search functionality
st.write("### CSV File Preview")
st.write(df)
python_cmd = get_python_command()
# Text input for user question
userinput = st.text_input("Enter a question:", "")

if userinput:
    with st.spinner('Processing your question...'):
        rewritten_question = rewrite_question(userinput, df.columns)

        formatted_string = f"""
        Context: You are a Python data analyst working with a CSV file named {filename}. 
        Generate Python code using pandas to answer the following question. 
        Include proper column name usage. 

        Column Names: {', '.join(df.columns)}

        Question: {rewritten_question}

        Respond with the python3 pandas code to solve the problem and nothing else. Note: the code will by run from a python3 script not a Jupyter notebook. 
        """

        response = ollama.chat(model=model, messages=[
            {
                'role': 'user',
                'content': formatted_string,
            },
        ])

        resp = response.message.content.strip()
        generated_code = extract_code(resp)
        st.code(generated_code, language='python')

        # Save the extracted code to a file
        with open('generated_script.py', 'w') as file:
            file.write(generated_code)

        # Run the generated script and capture the output
        result = subprocess.run([python_cmd, 'generated_script.py'], capture_output=True, text=True)

        # Display the result
        if result.returncode == 0:
            output = result.stdout
            st.write("### Answer:")
            st.text(output)
        else:
            st.error("Could not find an answer to the question, please try again...")
