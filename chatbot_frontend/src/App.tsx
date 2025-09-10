import { useState, useEffect, useRef } from 'react';
import { Box, CssBaseline, Container, Stack, Button, useTheme } from '@mui/material';
import { ThemeProvider } from '@mui/material/styles';
import { theme } from './theme';
import { ChatInterface } from './components/ChatInterface';
import { Header } from './components/Header';
import Testing from './components/Testing';
import { Message } from './services/api';
import ChatIcon from '@mui/icons-material/Chat';
import BuildIcon from '@mui/icons-material/Build';

export default function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [chatId, setChatId] = useState<string>('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const controllerRef = useRef<AbortController | null>(null);
  const timersRef = useRef<number[]>([]);
  const [view, setView] = useState<'chat' | 'testing'>('chat');

  // Load messages from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem('chatHistory');
    if (saved) {
      try {
        const parsedMessages = JSON.parse(saved);
        setMessages(parsedMessages);
      } catch (error) {
        console.error('Error parsing chat history:', error);
      }
    }
  }, []);

  // Save messages to localStorage whenever they change
  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem('chatHistory', JSON.stringify(messages));
    }
  }, [messages]);

  const handleSendMessage = async (message: string) => {
    if (!message.trim()) return;

    const startTime = Date.now();

    const userMessage: Message = {
      role: 'user',
      content: message,
      timestamp: new Date(),
    };

    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setIsLoading(true);

    try {
      // Cleanup any previous timers/controllers
      if (controllerRef.current) {
        controllerRef.current.abort();
      }
      timersRef.current.forEach((id) => clearTimeout(id));
      timersRef.current = [];

      const controller = new AbortController();
      controllerRef.current = controller;

      // Staged timeouts: 20s, 40s, 60s (abort)
      const t1 = window.setTimeout(() => {
        setMessages((prev) => [
          ...prev,
          { role: 'assistant', content: 'Time 1: still working…', timestamp: new Date() },
        ]);
      }, 20_000);
      const t2 = window.setTimeout(() => {
        setMessages((prev) => [
          ...prev,
          { role: 'assistant', content: 'Time 2: almost there…', timestamp: new Date() },
        ]);
      }, 40_000);
      const t3 = window.setTimeout(() => {
        controller.abort();
        setMessages((prev) => [
          ...prev,
          { role: 'assistant', content: 'Time 3: request timed out after 60s. Please try again or refine your question.', timestamp: new Date() },
        ]);
        setIsLoading(false);
      }, 60_000);
      timersRef.current.push(t1, t2, t3);

      // Use the environment variable for the API URL
      const apiUrl = import.meta.env.VITE_API_URL || '/api/chat';
      
      console.log('Sending request to:', apiUrl);
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({ question: message }),
        signal: controller.signal,
      });

      console.log('Response status:', response.status);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('Server error:', errorText);
        throw new Error(`Error ${response.status}: ${errorText}`);
      }

      const data = await response.json();
      console.log('Response data:', data);

      const endTime = Date.now();
      const time = ((endTime - startTime) / 1000).toFixed(1);

      const assistantMessage: Message = {
        role: 'assistant',
        content: `${data.answer || data.error || 'No response from server'}\n\nResponded in ${time}s`,
        timestamp: new Date(),
      };

      // Clear staged timers on success
      timersRef.current.forEach((id) => clearTimeout(id));
      timersRef.current = [];

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error: any) {
      console.error('Error sending message:', error);
      // If aborted by our timeout, we already appended a timeout message in t3
      if (error?.name !== 'AbortError') {
        const errorEndTime = Date.now();
        const errorTime = ((errorEndTime - startTime) / 1000).toFixed(1);
        const errorMessage: Message = {
          role: 'assistant',
          content: `Sorry, there was an error processing your request. Responded in ${errorTime}s`,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errorMessage]);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewChat = () => {
    setChatId(`chat-${Date.now()}`);
    setMessages([]);
    localStorage.removeItem('chatHistory');
    // Cleanup timers and any pending request
    if (controllerRef.current) {
      controllerRef.current.abort();
      controllerRef.current = null;
    }
    timersRef.current.forEach((id) => clearTimeout(id));
    timersRef.current = [];
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <Header onNewChat={handleNewChat} />
        <Container
          maxWidth="lg"
          sx={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            py: 2,
            px: { xs: 1, sm: 2 },
          }}
        >
          <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
            <Button variant={view === 'chat' ? 'contained' : 'outlined'} startIcon={<ChatIcon />} onClick={() => setView('chat')}>Chat</Button>
            <Button variant={view === 'testing' ? 'contained' : 'outlined'} startIcon={<BuildIcon />} onClick={() => setView('testing')}>Testing</Button>
          </Stack>

          {view === 'chat' ? (
            <ChatInterface
              messages={messages}
              onSendMessage={handleSendMessage}
              isLoading={isLoading}
              messagesEndRef={messagesEndRef}
            />
          ) : (
            <Testing />
          )}
        </Container>
      </Box>
    </ThemeProvider>
  );
}
