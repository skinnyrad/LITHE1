import streamlit as st
import ollama
import pandas as pd
import re
import subprocess


# Load the CSV file and display an error message if it fails
try:
    filename = './inputdata.csv'
    df = pd.read_csv(filename)
    df_head = df.head()
except Exception as e:
    st.error("Could not read CSV file. Check to make sure it exists and is properly formatted...")
    st.stop()

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
        formatted_string = f"""
        Context: You are a chatbot assistant answering questions about a CSV file named {filename} for a user. Respond only with the python3 code that will answer the question and nothing else. Here are the first few rows of the CSV file:

        {df_head}

        User Question: {userinput}
        """
        response = ollama.chat(model='llama3:instruct', messages=[
            {
                'role': 'user',
                'content': formatted_string,
            },
        ])
        resp = response['message']['content']

        # Function to extract code from the response
        def extract_code(response):
            # Regular expression to match code within triple backticks
            code_pattern = re.compile(r'```(.*?)```', re.DOTALL)
            match = code_pattern.search(response)
            
            if match:
                # Extract code within backticks
                code = match.group(1).strip()
            else:
                # Use the entire response as code
                code = response.strip()
            
            return code

        generated_code = extract_code(resp)
        st.code(generated_code, language='python')

        # Save the extracted code to a file
        with open('generated_script.py', 'w') as file:
            file.write(generated_code)
        
        # Run the generated script and capture the output
        result = subprocess.run(['python3', 'generated_script.py'], capture_output=True, text=True)

        # Display the result
        if result.returncode == 0:
            output = result.stdout
            st.write("### Answer:")
            st.text(output)
        else:
            st.error("Could not find an answer to the question, please try again...")
