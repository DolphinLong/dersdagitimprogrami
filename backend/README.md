# Backend Setup

This is a Django project for the course distribution system.

## Setup

1.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    ```

2.  **Activate the virtual environment:**
    -   **Windows:**
        ```bash
        venv\Scripts\activate
        ```
    -   **macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Create a `.env` file:**
    Create a `.env` file in the `backend` directory and add the following:
    ```
    SECRET_KEY='your-secret-key'
    DEBUG=True
    ALLOWED_HOSTS=127.0.0.1,localhost
    ```

5.  **Run the database migrations:**
    ```bash
    python manage.py migrate
    ```

6.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```

The backend server will be running at `http://127.0.0.1:8000/`.
