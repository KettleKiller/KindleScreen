# KindleScreen

KindleScreen is a Python application that captures screenshots at a specified frame rate and divides them into parts. The application uses Flask for the web interface and Flask-SocketIO for real-time updates.

## Features

- Captures screenshots at a specified frame rate (FPS).
- Maintains a specific aspect ratio for the screenshots.
- Divides screenshots into multiple parts and updates only the changed parts.
- Provides a web interface to view the screenshots.
- Sends real-time updates to the web interface when parts of the screenshots are updated.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/KettleKiller/KindleScreen.git
    cd KindleScreen
    ```

2. Create a virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. Run the application:
    ```bash
    python app.py
    ```

2. Open a web browser and navigate to `http://localhost:5000` to view the web interface.

## Configuration

- `SAVE_DIR`: Directory to save the screenshots.
- `ASPECT_RATIO`: Aspect ratio of the screenshots.
- `WIDTH`: Width of the screenshots.
- `OUTPUT_SIZE`: Size of the resized screenshots.
- `FPS`: Frame rate for capturing screenshots.
- `X_PARTS`: Number of parts in the X direction.
- `Y_PARTS`: Number of parts in the Y direction.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
