# Production Deployment Guide

This guide provides a checklist and instructions for deploying the FastAPI backend to a production environment.

---

## 1. Environment Setup Checklist

Before deploying, ensure your production environment is ready.

-   [ ] **Server**: A virtual private server (VPS), container platform (Docker), or PaaS (like Heroku, Fly.io).
-   [ ] **PostgreSQL Database**: A managed production-grade PostgreSQL database (e.g., AWS RDS, Google Cloud SQL, or DigitalOcean Managed Databases).
-   [ ] **Domain Name**: A registered domain name pointing to your server's IP address.
-   [ ] **SSL Certificate**: An SSL certificate for enabling HTTPS (Let's Encrypt is a free option).

## 2. Production Environment Variables

Set these environment variables in your production environment. **Do not hardcode them.**

-   `DATABASE_URL`: The connection string for your **production** PostgreSQL database.
    
    DATABASE_URL=postgresql+asyncpg://<user>:<password>@<host>:<port>/<dbname>
    
-   `SECRET_KEY`: A long, random, and secret string for signing JWTs. Generate a secure key with:
    bash
    openssl rand -hex 32
    
-   `CORS_ORIGINS`: A comma-separated list of your **production frontend URLs**.
    
    CORS_ORIGINS=https://www.your-frontend.com,https://your-frontend.com
    

## 3. Uvicorn for Production

Do not use the `--reload` flag in production. Use a process manager like `Gunicorn` to manage `Uvicorn` workers for better performance and reliability.

1.  **Install Gunicorn**:
    bash
    pip install gunicorn
    
2.  **Run with Gunicorn**:
    bash
    gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.main:app --bind 0.0.0.0:8000 -c gunicorn_conf.py
    
    -   `-w 4`: Starts 4 worker processes (a good starting point is `2 * num_cores + 1`).
    -   `-k uvicorn.workers.UvicornWorker`: Uses Uvicorn to handle the async processing.
    -   `--bind 0.0.0.0:8000`: Binds to all network interfaces on port 8000.
    -   `-c gunicorn_conf.py`: Optional configuration file for advanced settings (logging, timeouts).

## 4. HTTPS/SSL Configuration

**Never run a production application over HTTP.** Use a reverse proxy like **Nginx** or **Caddy** to handle HTTPS termination.

### Example Nginx Configuration

This configuration listens on port 443 (HTTPS), handles SSL, and forwards requests to the Gunicorn server running on port 8000.

nginx
server {
    listen 80;
    server_name api.yourdomain.com;
    # Redirect HTTP to HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name api.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}


## 5. Docker Deployment (Recommended)

Containerizing the application with Docker is the recommended approach for portability and consistency.

1.  **Create a `Dockerfile`** in the root directory:

    dockerfile
    # Use an official Python runtime as a parent image
    FROM python:3.11-slim

    # Set the working directory
    WORKDIR /app

    # Copy the requirements file and install dependencies
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt

    # Copy the application code
    COPY . .

    # Command to run the application using Gunicorn
    CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "app.backend.main:app", "--bind", "0.0.0.0:8000"]
    

2.  **Build the Docker image**:
    bash
    docker build -t appointment-backend .
    

3.  **Run the Docker container**:
    bash
    docker run -d -p 8000:8000 --env-file .env --name api appointment-backend
    
    -   `-d`: Run in detached mode.
    -   `-p 8000:8000`: Map port 8000 of the host to port 8000 of the container.
    -   `--env-file .env`: Load environment variables from the `.env` file.

## 6. Health Checks, Monitoring, and Logging

-   **Health Checks**: Use the `/health` endpoint with a monitoring service (like UptimeRobot or your cloud provider's monitoring) to ensure the API is live.
-   **Logging**: Configure Gunicorn/Uvicorn to output structured logs (e.g., JSON). Ship these logs to a centralized logging service (e.g., ELK Stack, Datadog, or Sentry).
-   **Monitoring**: Use tools like Prometheus and Grafana or a PaaS provider's built-in monitoring to track CPU, memory, response times, and error rates.

## 7. Security Best Practices

-   [ ] **Limit Database Permissions**: The database user should only have the permissions it needs (`SELECT`, `INSERT`, `UPDATE`, `DELETE`), not `SUPERUSER` privileges.
-   [ ] **Regularly Rotate Secrets**: Change your `SECRET_KEY` and database credentials periodically.
-   [ ] **Keep Dependencies Updated**: Regularly scan for and update vulnerable packages.
-   [ ] **Set Up a Firewall**: Use a firewall (like `ufw` on Linux) to only allow traffic on necessary ports (e.g., 80, 443).
