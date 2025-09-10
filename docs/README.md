# IIT Ropar Info Chatbot

A modern web-based chatbot that provides accurate information about IIT Ropar using Retrieval-Augmented Generation (RAG) with vector embeddings. The application features a responsive web interface and can be deployed on Vercel.

## 🌟 Features

- **Web Interface**: Modern, responsive UI built with React and Material-UI
- **Semantic Search**: Utilizes vector embeddings for accurate question-answering
- **Testing Interface**: Built-in testing interface with red team evaluation
- **Deployment Ready**: Pre-configured for Vercel serverless deployment
- **Docker Support**: Containerized for easy local development and deployment

## 🚀 Quick Start

### Prerequisites

- Node.js 16+ (for frontend)
- Python 3.9+ (for backend)
- Docker (optional, for containerized deployment)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Chatbot_test2
   ```

2. **Set up the backend**
   ```bash
   # Install Python dependencies
   pip install -r requirements.txt
   
   # Start the local development server
   python backend.py
   ```

3. **Set up the frontend**
   ```bash
   cd frontend_new
   npm install
   npm run dev
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - API: http://localhost:3001

## 🛠 Project Structure

```
.
├── api/
│   ├── chat/               # Serverless API endpoint
│   │   ├── index.py        # Main API handler
│   │   └── vercel.json     # Vercel configuration
│   └── vercel.json         # API routing configuration
├── frontend_new/           # React frontend
│   ├── public/             # Static files
│   └── src/                # Source code
│       ├── components/      # React components
│       └── services/        # API services
├── scripts/                # Utility scripts
│   ├── evaluate_ragas.py   # RAG evaluation
│   └── generate_redteam.py # Test data generation
├── .env.production         # Production environment variables
├── vercel.json             # Main Vercel configuration
└── requirements.txt        # Python dependencies
```

## 🚀 Deployment

### Vercel Deployment

1. Push your code to a Git repository
2. Import the repository into Vercel
3. Configure environment variables in Vercel:
   - `PYTHON_VERSION`: 3.9
   - `NODE_VERSION`: 16
4. Deploy!

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build
```

## 🧪 Testing

The application includes a testing interface that can be used to evaluate the chatbot's performance:

1. Access the testing interface at `/testing`
2. Run automated tests using the provided scripts:
   ```bash
   python scripts/generate_redteam.py
   python scripts/evaluate_ragas.py
   ```

## 📚 Documentation

- [API Documentation](#) (Coming soon)
- [Deployment Guide](DEPLOYMENT.md)
- [Testing Guide](scripts/README.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
Adding New Data
To extend the chatbot, add new Q&A pairs to your CSV.

Ensure the CSV is in the same format as the existing one.

The vector database will automatically index the new data when you reload.
