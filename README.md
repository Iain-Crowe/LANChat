# LANChat

LANChat is a simple chat application that runs over LAN. Currently, LANChat has a CLI that will be developed into a full GUI.

## Features

-   Simple and lightweight
-   Real-time messaging
-   Easy setup and usage

## Requirements

-   Python 3.9 or higher
-   Required Python libraries (specified in `requirements.txt`)

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/Iain-Crowe/LANChat.git
    cd LANChat
    ```

2. Create a virtual environment (highly recommended):

    ```bash
    python -m venv venv
    ```

3. Locate the activate script in the environment and set environment variables:

    For Linux (in `venv/bin/activate`)

    ```bash
    export SERVER_IP="0.0.0.0"  # Your IP for the server to run on
    export SERVER_PORT=8080     # A port for the server to run on
    ```

    For Windows (in `venv\Scripts\activate.bat`)

    ```batch
    set SERVER_IP="0.0.0.0"     & REM Your IP for the server to run on
    set SERVER_PORT=8080        & REM A port for the server to run on
    ```

4. Activate the virtual environment:

    For Linux (in `venv/bin/activate`)

    ```bash
    source venv/bin/activate
    ```

    For Windows (in `venv\Scripts\activate.bat`)

    ```batch
    venv\Scripts\activate.bat
    ```

5. Install the dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

### Server

1. Run the server script:

    ```bash
    python server.py # src/server.py if in root dir
    ```

2. The server will start listening for incoming connections on the port specified.

### Client

1. Run the client script:

    ```bash
    python client.py # src/client.py if in root dir
    ```

2. The client will start up and connect with the server.

## Logging

The application uses a logging system to record events and errors. Logs are displayed on the command line. I will likely alter it to save a log file later.

## Contributing

Contributions are welcome! If you'd like to help out feel free to fork the repo and submit a pull request with any changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE.md) file for details.

## Contact

For any questions or feedback, please contact me at [iainccrowe@gmail.com](iainccrowe@gmail.com).
