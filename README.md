# LITHE1 - Lightweight Intelligent Tool for Handling Exports (Version 1)

LITHE1 is a versatile and lightweight intelligent tool designed to perform AI-driven data analysis on CSV files. Utilizing the power of the `ollama` module with open source Large Language Models, LITHE1 provides an interactive experience for users to query and analyze their CSV data efficiently.

![data-analysis](./img/data-analysis.jpg)

## Features

- **AI-Powered Analysis**: Leverages advanced AI models to understand and process user queries related to CSV data.
- **Interactive Querying**: Allows users to input questions and receive Python code that performs the requested analysis on the CSV file.
- **Automatic Code Generation and Execution**: Generates and executes Python scripts based on user queries to provide immediate answers.
- **Error Handling**: Includes mechanisms to handle connection issues with the LLM and CSV file reading errors.
- **Model Agnostic**: Compatible with all models available in [Ollama](https://www.ollama.com/library), allowing for effortless switching and customization.
- **Offline Analysis**: The tool uses offline models provided by `Ollama` so your data doesn't get sent to a third party.

## Installation

[Install Ollama](https://ollama.com/) and download the necessary models.  The default model recommended for use with LITHE1 is [qwen2.5-coder](https://ollama.com/library/qwen2.5-coder).  This model can be downloaded from the command line:
```sh
ollama pull qwen2.5-coder
```

Ensure you have the following Python dependencies installed:

- `ollama`
- `pandas`
- `re`
- `subprocess`
- `streamlit`

Install the required Python packages:

```sh
pip install ollama pandas streamlit
```

## Usage

Place your CSV file in the same directory as `lithe1.py` and name it `inputdata.csv`.  Once you have done this you can run the tool:

```sh
streamlit run lithe1.py
```

![lithe1-main](./img/lithe1-main.png)

Enter your questions about the CSV file when prompted. LITHE1 will generate and execute Python code to provide the answers. **Note: This tool is not intended for production use.  The project is running LLM generated code, which is highly dangerous.  We would advise running the tool in a docker container to prevent code execution.**


## Example

After starting the tool, you might enter a question like:

```
What are the column headers of the csv file?
```

LITHE1 will generate and execute the relevant Python code to answer your question.  The application will show you what code was generated and executed.

![lithe1-answer](./img/lithe1-answer.png)

## Max File Size

The max default file size for streamlit is 200 MB.  If you try to upload a file larger than that, you will get this error:

```
MessageSizeError: Data of size 225.7 MB exceeds the message size limit of 200.0 MB.

This is often caused by a large chart or dataframe. Please decrease the amount of data sent to the browser, or increase the limit by setting the config option server.maxMessageSize. Click here to learn more about config options.

Note that increasing the limit may lead to long loading times and large memory consumption of the client's browser and the Streamlit server.
```

### Adjusting Streamlit's Configuration for Larger Files:
To allow larger files in Streamlit, you can define a global configuration by locating and editing the `.streamlit` directory created during installation. Follow these steps based on your operating system:

1. **Find or create the Configuration File:**
   - **macOS/Linux**: The configuration file is located at `~/.streamlit/config.toml`. The `~` represents your home directory (e.g., `/Users/<YourUsername>/`).
   - **Windows**: You’ll find the file at `$env:userprofile\.streamlit\config.toml`. `$env:userprofile` typically corresponds to `C:\Users\<YourUsername>\`.

2. **Edit or Create the Configuration File:**
   - If the file does not exist, you can create it manually. Use a text editor of your choice:
     - On Windows: Open Notepad or any preferred editor.
     - On macOS/Linux: Use `nano`, `vim`, or a graphical text editor like VS Code or TextEdit.
   - Add or modify the following content:
     ```plaintext
     [server]
     maxMessageSize = 250
     ```
     Replace `250` with the desired size in megabytes.

3. **Save and Apply the Changes:**
   - After saving the file, restart your Streamlit application to apply the updated configuration.


## Contributing

We welcome contributions to improve LITHE1. Feel free to submit issues or pull requests.


## License

This project is licensed under the MIT License.


## Acknowledgments

LITHE1 was developed by Josiah Bryan ([Halcy0nic](https://github.com/Halcy0nic)) at Skinny Research and Development to simplify the process of querying and analyzing CSV files using the latest AI technologies.
