# ChatGPT PC Controller

This application lets ChatGPT Control your PC using Python and AutoIt. It utilizes the main OpenAI website's ChatGPT API underneath, instead of requiring API keys.

## Screenshots
![ChatGPT PC Controller](assets/screenshot.jpg?raw=true)
- Here is is creating a command to read the text of my open notepad window, automatically replying back to ChatGPT with it's contents, and ChatGPT generating a new command back to windows based on that:
![ChatGPT PC Controller performing input and output ](assets/screenshot_in_out.jpg?raw=true)

## Prerequisites

Before running the application, make sure you have the following prerequisites installed:

1. Install Python 3.x

2. Install the Web Driver. Please follow the instructions specific to your browser to install the driver.

For Chrome:
- Download: https://googlechromelabs.github.io/chrome-for-testing/
- You will need to change webdriver_path, chrome_path and user_data_dir in config.ini if the defaults are incorrect. Soon I will add an options menu to do this better and try to detect it automatically.

Firefox (Untested):
- Download: https://github.com/mozilla/geckodriver/releases
- You will need to change webdriver_path, chrome_path and user_data_dir in config.ini, but even then, I don't think it will work at this stage. May support it soon.

## Installation

1. Clone the repository:

   ```shell
   git clone https://github.com/Tophness/ChatGPT-PC-Controller.git
   ```

2. Change to the project directory:

   ```shell
   cd ChatGPT-PC-Controller
   ```

3. Install the prerequisite Python libraries:

   ```shell
   pip install -r requirements.txt
   ```

## Usage

To use the program, follow these steps:

1. Open a terminal or command prompt and navigate to the project directory.

2. Run the `main.py` file:

   ```shell
   python main.py
   ```

3. Enter a command to control your PC.

4. ChatGPT will generate a control command.

5. Confirm whether you want to run it.


## Contributing

Contributions are welcome! If you find any issues or want to enhance the functionality of this application, feel free to open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).
