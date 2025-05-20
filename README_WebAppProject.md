
# Python Web App with MongoDB – Dockerized

This is a Python-based web application containerized using Docker and connected to a MongoDB instance. The project demonstrates backend architecture using Python, RESTful handling, modular utility separation, and containerized orchestration with Docker Compose.

## 🚀 Features

- Lightweight Python backend
- MongoDB integration via Docker Compose
- Modular codebase with separate handler and utility layers
- Dockerized deployment for consistency across environments

## 🧰 Tech Stack

- Python (with custom web handling or minimal framework)
- MongoDB
- Docker & Docker Compose

## 📁 Project Structure

```
WebAppProject/
├── server.py           # Main entry point for the app
├── handler.py          # Handles incoming HTTP requests and routing
├── util/               # Utility modules
├── public/             # Static files (HTML, JS, CSS)
├── Dockerfile          # Docker build file for the app
├── docker-compose.yml  # Compose file to run app + MongoDB
├── requirements.txt    # Python dependencies
└── .gitignore          # Ignored files/folders
```

## 🐳 Getting Started with Docker

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/webapp-mongo-docker.git
cd webapp-mongo-docker
```

### 2. Build and Run the App

```bash
docker-compose up --build
```

This will:
- Build the Python app container
- Start MongoDB using the official Docker image
- Serve the app on `http://localhost:8080`

### 3. Shut Down

```bash
docker-compose down
```

## 🔧 Environment

- MongoDB runs on port `27017` inside the container
- Web server runs on port `8080`
- You can modify `docker-compose.yml` to adjust ports as needed

## 📌 Notes

- This app is currently a demonstration and may be extended with user sessions, REST APIs, or frontend frameworks.
- Contributions and improvements are welcome!

---

© 2025 Jaskaran Sidhu
