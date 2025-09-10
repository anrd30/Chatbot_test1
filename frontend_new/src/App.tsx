import { useState, useEffect, useRef } from 'react';
import { Box, CssBaseline, Container, Stack, Button } from '@mui/material';
import { ThemeProvider } from '@mui/material/styles';
import { theme } from './theme';
import { ChatInterface } from './components/ChatInterface';
import { Header } from './components/Header';
import Testing from './components/Testing';
import { Message } from './services/api';

export default function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [chatId, setChatId] = useState<string>('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const controllerRef = useRef<AbortController | null>(null);
  const timersRef = useRef<number[]>([]);
  const [view, setView] = useState<'chat' | 'testing'>('chat');

  // Initialize chatId on first load
  useEffect(() => {
    setChatId(`chat-${Date.now()}`);
  }, []);

  // Scroll to bottom whenever messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (message: string) => {
    if (!message.trim()) return;

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

      const assistantMessage: Message = {
        role: 'assistant',
        content: data.answer || data.error || 'No response from server',
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
        const errorMessage: Message = {
          role: 'assistant',
          content: 'Sorry, there was an error processing your request. Please try again.',
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
            <Button variant={view === 'chat' ? 'contained' : 'outlined'} onClick={() => setView('chat')}>Chat</Button>
            <Button variant={view === 'testing' ? 'contained' : 'outlined'} onClick={() => setView('testing')}>Testing</Button>
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
