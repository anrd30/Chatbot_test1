# IIT Ropar Chatbot - Deployment Guide

This guide covers both Vercel (frontend) and Docker (backend) deployment options.

## Option 1: Vercel Deployment (Frontend) + Docker Backend

### Prerequisites

1. [Docker](https://www.docker.com/get-started) installed
2. [Node.js](https://nodejs.org/) (v16 or later) and npm
3. [Vercel CLI](https://vercel.com/cli) (for deployment)

### Deploy Frontend to Vercel

1. **Install Vercel CLI** (if not installed):
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy the frontend**:
   ```bash
   cd frontend_new
   vercel --prod
   ```
   - Follow the prompts to complete the deployment
   - Note the deployment URL (e.g., `https://your-frontend.vercel.app`)

### Deploy Backend with Docker

1. **Build the Docker image**:
   ```bash
   docker build -t iit-chatbot-backend .
   ```

2. **Run the container**:
   ```bash
   docker run -d -p 3001:3001 --name iit-chatbot iit-chatbot-backend
   ```

## Option 2: Full Docker Deployment (Development)

1. **Start all services** (frontend + backend):
   ```bash
   docker-compose up --build
   ```

2. Access the application at `http://localhost:3000`

## Environment Variables

### Frontend (Vercel)
- `VITE_API_URL`: URL of your backend API (e.g., `https://your-backend.com`)

### Backend (Docker)
- `PYTHONUNBUFFERED`: Set to `1` for better logging
- Add other required environment variables in `docker-compose.yml`

## Production Considerations

1. **Database**: For production, use a managed database service
2. **HTTPS**: Ensure your backend API is served over HTTPS
3. **Scaling**: Consider using a container orchestration service (e.g., Kubernetes) for production
4. **Monitoring**: Set up logging and monitoring for both frontend and backend

## Troubleshooting

- **Frontend not connecting to backend**: Check CORS settings and API URL
- **Docker build fails**: Ensure all required files are in the Docker context
- **Port conflicts**: Update ports in `docker-compose.yml` if needed

## Maintenance

- Keep dependencies updated
- Monitor resource usage
- Set up automated backups for any persistent data
