# Flask Backend Project

This project is a Flask application that serves as a backend for web applications. It includes a basic structure with routes, models, and templates.

## Project Structure

```
flask-backend
├── src
│   ├── app.py               # Main entry point of the Flask application
│   ├── config.py            # Configuration settings for the application
│   ├── models               # Directory for data models
│   │   └── __init__.py      # Initialization for models
│   ├── routes               # Directory for route definitions
│   │   └── __init__.py      # Initialization for routes
│   └── templates            # Directory for HTML templates
│       └── index.html       # Main HTML template
├── Dockerfile                # Development Dockerfile
├── Dockerfile.prod           # Production Dockerfile
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd flask-backend
   ```

2. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```
   python src/app.py
   ```

## Docker

### Development

To build and run the development Docker container, use the following commands:

```
docker build -f Dockerfile -t flask-backend-dev .
docker run -p 5000:5000 flask-backend-dev
```

### Production

To build and run the production Docker container, use the following commands:

```
docker build -f Dockerfile.prod -t flask-backend-prod .
docker run -p 5000:5000 flask-backend-prod
```

## Usage

Access the application by navigating to `http://localhost:5000` in your web browser.

## License

This project is licensed under the MIT License. See the LICENSE file for details.