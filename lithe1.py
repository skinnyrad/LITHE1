import streamlit as st
import ollama
import pandas as pd
import re
import subprocess
from ollama import chat
from ollama import ChatResponse
import platform
import shutil

# --- Model Selection with Session State ---
# Get available models from ollama and store in session state
if 'models' not in st.session_state:
    try:
        model_names = ollama.list()
        st.session_state.models = [model.model for model in model_names['models']]
    except Exception as e:
        st.sidebar.error(f"Error loading models: {e}")
        st.session_state.models = ["gemma3"]  # Fallback to default

# Initialize selected model in session state if not set
if 'selected_model' not in st.session_state:
    st.session_state.selected_model = st.session_state.models[0]

# Sidebar model selection, tied to session state
st.sidebar.title("Model Selection")
selected_model = st.sidebar.selectbox(
    "Select an Ollama model",
    st.session_state.models,
    index=st.session_state.models.index(st.session_state.selected_model) if st.session_state.selected_model in st.session_state.models else 0,
    key="selected_model"
)

# Always use the selected model from session state
model = st.session_state.selected_model

# Defensive: Prevent running if no model is selected
if not model:
    st.sidebar.error("No Ollama model selected. Please select a model in the sidebar.")
    st.stop()

def get_python_command():
    if platform.system() == "Windows":
        return "python"
    python3_path = shutil.which("python3")
    if python3_path:
        return "python3"
    python_path = shutil.which("python")
    if python_path:
        return "python"
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

def rewrite_question(user_question, df_columns):
    prompt = f"""
    You are an AI assistant specializing in data analysis. Your task is to rewrite the given question to make it more suitable for CSV data analysis using Python and pandas.

    CSV Column Names: {', '.join(df_columns)}

    Original Question: {user_question}

    Rewrite the question AND RESPOND WITH THE REWRITTEN QUESTION ONLY, NOTHING ELSE.
    """
    response = chat(model=model, messages=[
        {'role': 'user', 'content': prompt},
    ])
    response_text = response.message.content.strip()
    # Extract actual response after thinking if present
    return extract_response_after_thinking(response_text)

def extract_response_after_thinking(response_text):
    """Extract the actual response after <think></think> tags if present."""
    think_pattern = re.compile(r"<think>(.*?)</think>(.*)", re.DOTALL)
    match = think_pattern.match(response_text)
    if match:
        return match.group(2).strip()  # Return the content after </think>
    else:
        return response_text  # Return original response if no thinking tags found

try:
    filename = './inputdata.csv'
    df = pd.read_csv(filename, dtype=str, low_memory=False)
except Exception as e:
    st.error("Could not read CSV file. Check to make sure it exists and is properly formatted...")
    st.stop()

try:
    import pyarrow as pa
    pa.Table.from_pandas(df)
except Exception as e:
    st.error(f"DataFrame is not Arrow-compatible: {e}")
    st.stop()

# Streamlit UI setup
st.title("LITHE1 - Lightweight Intelligent Tool for Handling Exports")
st.write("Ask questions about your CSV file below.")

# Using a form for input and submission
with st.form(key='question_form'):
    st.write("### CSV File Preview")
    st.write(df)
    
    userinput = st.text_input("Enter a question:", "")
    
    # Add a submit button inside the form
    submitted = st.form_submit_button(label="Submit")

if submitted and userinput:
    with st.spinner('Processing your question...'):
        rewritten_question = rewrite_question(userinput, df.columns)

        formatted_string = f"""
        Context: You are a Python data analyst working with a CSV file named {filename}. 
        Generate Python code using pandas to answer the following question. 
        Include proper column name usage. 

        Column Names: {', '.join(df.columns)}

        Question: {rewritten_question}

        Respond with the python3 pandas code to solve the problem and nothing else.
        """
        
        response = ollama.chat(model=model, messages=[
            {'role': 'user', 'content': formatted_string},
        ])

        resp = response.message.content.strip()
        # Extract actual response after thinking if present
        resp = extract_response_after_thinking(resp)
        generated_code = extract_code(resp)

        st.code(generated_code, language='python')

        # Save and execute the generated script
        python_cmd = get_python_command()
        with open('generated_script.py', 'w') as file:
            file.write(generated_code)

        result = subprocess.run([python_cmd, 'generated_script.py'], capture_output=True, text=True)

        if result.returncode == 0:
            output = result.stdout
            st.write("### Answer:")
            st.text(output)
        else:
            st.error("Could not find an answer to the question, please try again...")
