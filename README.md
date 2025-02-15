# This is a guide for  game application:

---

# Game Application

A simple game built with Tkinter and Pygame featuring user login, customizable settings, and a record system using SQLite. The application allows you to:

- Log in with a username and password (or create a new user automatically).
- Customize various game settings (window size, target size/color, game level, target disappearance time, timer, and an optional skin image).
- Play a target-clicking game where your score is recorded.
- View and search past game records.
- Automatically return to the settings window after game completion or forced exit.

## Features

- **User Authentication**: Enter a username and password to log in. New users are automatically created.
- **Customizable Settings**: Adjust game window dimensions, target size and color, game level, disappearance time for targets, and game timer. Optionally, select a custom skin image.
- **Game Logic**: Play a simple game where targets appear at random positions and must be clicked before they disappear.
- **Record Management**: Game results are saved in an SQLite database. Use the "View Records" button to search and review past scores.
- **Organized GUI**: The settings window is divided into separate sections (Window Settings, Target Settings, Game Settings, Skin Settings, and Action Buttons) for easy navigation.

## Requirements

- Python 3.x
- Pygame (install via pip: `pip install pygame`)
- Tkinter (typically included with Python)
- SQLite3 (bundled with Python)

## Installation

1. **Download/Clone the Repository**: Save the `game.py` file to your computer.
2. **Install Dependencies**:  
   Open your terminal/command prompt and run:  
   ```
   pip install pygame
   ```
3. **Verify Python Installation**: Ensure Python 3.x is installed on your system.

## Usage

1. **Start the Application**:  
   Run the game by executing:
   ```
   python game.py
   ```
2. **Login**:  
   - Enter your username and password in the login window.
   - If you are a new user, an account will be created automatically.
3. **Configure Settings**:  
   Once logged in, the settings window appears. Here you can:
   - **Window Settings**: Set the game window's width and height.
   - **Target Settings**: Define target size (width x height) and select a target color.
   - **Game Settings**: Choose the game level (1-10), set the target disappearance time (or "None"), and specify the countdown timer (in minutes).
   - **Skin Settings**: Optionally choose a skin image file to be used as the target.
4. **Play the Game**:  
   Click "Play" to launch the game. A separate window will open for gameplay:
   - Click on targets to score points. Missing a target will deduct points.
   - The game automatically ends when the timer runs out or if you close the window.
5. **View Records**:  
   Click "View Records" in the settings window to search and display past game scores based on level and timer settings.
6. **Return to Settings**:  
   After the game ends (normally or by forced exit), the settings window will reappear so you can adjust settings or play again.
7. **Logout**:  
   Use the "Logout" button to return to the login window.

## Database

The application uses SQLite to manage user credentials and game records. The database file `game.db` is created automatically in the same directory if it does not exist.

## Troubleshooting

- **Pygame Issues**:  
  Ensure Pygame is installed correctly by running `pip install pygame`.
- **Display Issues**:  
  If the game window does not display correctly, check your graphics drivers or try running the game on another system.
- **Input Errors**:  
  Make sure to enter valid numerical values for window size, target size, and timer.

## License

This project is licensed under the MIT License. You are free to modify and distribute it as needed.

## Acknowledgments

This game application demonstrates integrating Tkinter and Pygame with SQLite in a Python project. Special thanks to all contributors and the open-source community.

---
