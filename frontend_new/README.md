# IIT RPR Chatbot - Frontend

A modern, responsive chat interface for the IIT Ropar Chatbot, built with React, TypeScript, and Material-UI.

## Features

- Modern, clean UI with responsive design
- Markdown support in messages
- Code syntax highlighting
- Smooth scrolling and loading states
- Mobile-friendly interface
- Persistent chat history (in local storage)

## Prerequisites

- Node.js (v16 or higher)
- npm or yarn

## Getting Started

1. **Install Dependencies**
   ```bash
   cd frontend_new
   npm install
   ```

2. **Start Development Server**
   ```bash
   npm run dev
   ```
   This will start the development server at `http://localhost:5173`

3. **Building for Production**
   ```bash
   npm run build
   ```
   The build artifacts will be stored in the `dist/` directory.

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```
VITE_API_URL=http://localhost:5000
```

## Project Structure

```
frontend_new/
├── public/              # Static files
├── src/
│   ├── components/      # Reusable components
│   ├── services/        # API services and utilities
│   ├── theme.ts         # MUI theme configuration
│   ├── App.tsx          # Main application component
│   └── main.tsx         # Application entry point
├── index.html           # HTML template
├── package.json         # Project dependencies and scripts
└── vite.config.ts       # Vite configuration
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Deployment

This project is ready to be deployed to any static hosting service like Vercel, Netlify, or GitHub Pages.

## License

MIT
