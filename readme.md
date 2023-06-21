['# ChatGPT Code Uploader

This is a Python application that utilizes the OpenAI GPT-3.5 model to generate responses based on files and a pretext.

## Prerequisites

Before running the application, make sure you have the following prerequisites installed:

- Python 3.x
- The required Python libraries mentioned in the `requirements.txt` file.

To install the required Python libraries, you can use the following command:

```shell
pip install -r requirements.txt
```

Additionally, you need to install a Driver for Selenium.
Please follow the instructions specific to your browser to install the driver.

For Chrome:
https://googlechromelabs.github.io/chrome-for-testing/
You will need to change webdriver_path, chrome_path and user_data_dir in config.ini if it's incorrect. Soon I will add an options menu to do this better and try to detect it automatically.

Firefox (Untested):
https://github.com/mozilla/geckodriver/releases
You will need to change webdriver_path, chrome_path and user_data_dir in config.ini, but even then, I don't think it will work at this stage. May support it soon.

## Installation

1. Clone the repository:

   ```shell
   git clone https://github.com/Tophness/ChatGPTCodeUploader.git
   ```

2. Change to the project directory:

   ```shell
   cd ChatGPTUploader
   ```

3. Install the prerequisite Python libraries:

   ```shell
   pip install -r requirements.txt
   ```

4. Install the Chrome Driver. Refer to the instructions specific to your operating system to install the Chrome Driver.

## Usage

To use the program, follow these steps:

1. Open a terminal or command prompt and navigate to the project directory.

2. Run the `main.py` file:

   ```shell
   python main.py
   ```

3. The application window will appear.

4. Enter the necessary details and select the desired options:

   - Prepend Text: Enter any text you want to prepend to the prompt input.
   - Input Directory: Select the directory containing the files you want to process.
   - File Types (comma-separated): Specify the file extensions of the files to process (e.g., js, json, py).
   - Output Type: Select the desired output type.
     - Prompt: Display the output in the application window.
     - Copy to Clipboard: Copy the output to the clipboard.
     - Save to File: Save the output to a text file.
   - Output Text File: If the output type is set to "Save to File," enter the desired output file name. By default, it is set to "prompt.txt."

5. Click the **Generate Output** button.

6. The program will process the files in the specified directory and create a prompt according to the selected options. If you selected 'prompt' output type, it will also prompt ChatGPT and return the chat response.


## Contributing

Contributions are welcome! If you find any issues or want to enhance the functionality of this application, feel free to open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).']
