# ChatGPT PC Controller

This application lets ChatGPT directly control your PC using Python and AutoIt to hook into the Win32 API and Windows Runtime UI.

It can control the mouse and keyboard, read and click windows control elements, run any command, move, minimize and close windows, read and write to clipboard and more.

It utilizes the main OpenAI website's ChatGPT API underneath, instead of requiring costly and limited API keys.

## Screenshots
![ChatGPT PC Controller](assets/screenshot.jpg?raw=true)
- Here is is creating a command to read the text of my open notepad window, automatically replying back to ChatGPT with it's contents, and ChatGPT generating a new command back to windows based on that:
![ChatGPT PC Controller performing input and output ](assets/screenshot_in_out.jpg?raw=true)
- Newer syntax 26/06/2023:
![ChatGPT PC Controller performing input and output ](assets/screenshot_vlc.jpg?raw=true)

## Prerequisites

Before running the application, make sure you have the following prerequisites installed:

1. Python 3.x

2. Git

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

3. Enter a goal for what you want ChatGPT to do to control your PC.

4. ChatGPT will generate a set of control commands.

5. Confirm whether you want to run it.

## Settings
- Set config.ini's 'Unattended mode' to True if you like to live dangerously. It will run in an infinite loop allowing ChatGPT to make it's own decisions and explore everything it opens and reads on your computer without asking.
- You can also edit the 'Preprompt' setting to adjust the prompt that gets prepended to your command.

## Contributing

Contributions are welcome! If you find any issues or want to enhance the functionality of this application, feel free to open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).
