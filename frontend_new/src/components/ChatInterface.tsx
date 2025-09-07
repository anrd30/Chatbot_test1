import { Box, TextField, IconButton, Paper, Typography, Avatar, CircularProgress } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import React, { useState, useEffect, useRef } from 'react';
import { Message } from '../services/api';
import { format } from 'date-fns';
import ReactMarkdown from 'react-markdown';

interface ChatInterfaceProps {
  messages: Message[];
  onSendMessage: (message: string) => void;
  isLoading: boolean;
  messagesEndRef: React.RefObject<HTMLDivElement>;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  messages,
  onSendMessage,
  isLoading,
  messagesEndRef,
}) => {
  const [message, setMessage] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !isLoading) {
      onSendMessage(message);
      setMessage('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  useEffect(() => {
    if (!isLoading) inputRef.current?.focus();
  }, [isLoading]);

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 130px)' }}>
      <Box
        sx={{
          flex: 1,
          overflowY: 'auto',
          mb: 2,
          p: 2,
          '& > *:not(:last-child)': { mb: 2 },
        }}
      >
        {messages.length === 0 ? (
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              height: '60%',
              textAlign: 'center',
              color: 'text.secondary',
            }}
          >
            <Typography variant="h5" gutterBottom>
              Welcome to IIT RPR Chatbot
            </Typography>
            <Typography variant="body1">Ask me anything about IIT Ropar</Typography>
          </Box>
        ) : (
          messages.map((msg, index) => <MessageBubble key={index} message={msg} />)
        )}
        <div ref={messagesEndRef} />
      </Box>

      <Paper
        component="form"
        onSubmit={handleSubmit}
        elevation={3}
        sx={{ p: 1, display: 'flex', alignItems: 'center', width: '100%' }}
      >
        <TextField
          inputRef={inputRef}
          fullWidth
          variant="outlined"
          placeholder="Type your message..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
          multiline
          maxRows={4}
          InputProps={{
            sx: { borderRadius: 4 },
            endAdornment: (
              <IconButton type="submit" color="primary" disabled={!message.trim() || isLoading} sx={{ ml: 1 }}>
                {isLoading ? <CircularProgress size={24} /> : <SendIcon />}
              </IconButton>
            ),
          }}
        />
      </Paper>
    </Box>
  );
};

const MessageBubble: React.FC<{ message: Message }> = ({ message }) => {
  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start',
        mb: 2,
      }}
    >
      <Box
        sx={{
          display: 'flex',
          flexDirection: message.role === 'user' ? 'row-reverse' : 'row',
          alignItems: 'flex-start',
          maxWidth: '80%',
        }}
      >
        <Avatar
          sx={{
            bgcolor: message.role === 'user' ? 'primary.main' : 'secondary.main',
            width: 32,
            height: 32,
            ml: message.role === 'user' ? 1 : 0,
            mr: message.role === 'assistant' ? 1 : 0,
          }}
        >
          {message.role === 'user' ? 'U' : 'AI'}
        </Avatar>
        <Box>
          <Paper
            elevation={1}
            sx={{
              p: 2,
              borderRadius: 4,
              bgcolor: message.role === 'user' ? 'primary.light' : 'background.paper',
              color: message.role === 'user' ? 'primary.contrastText' : 'text.primary',
            }}
          >
            <ReactMarkdown
              components={{
                code({ node, inline, className, children, ...props }) {
                  const match = /language-(\w+)/.exec(className || '');
                  return !inline && match ? (
                    <pre
                      style={{
                        background: '#f5f5f5',
                        padding: '0.5em',
                        borderRadius: '4px',
                        overflowX: 'auto',
                      }}
                    >
                      <code className={className} {...props}>
                        {children}
                      </code>
                    </pre>
                  ) : (
                    <code className={className} {...props}>
                      {children}
                    </code>
                  );
                },
              }}
            >
              {message.content}
            </ReactMarkdown>
            <Typography
              variant="caption"
              sx={{
                display: 'block',
                textAlign: 'right',
                mt: 0.5,
                color: message.role === 'user' ? 'primary.contrastText' : 'text.secondary',
                opacity: 0.8,
              }}
            >
              {format(new Date(message.timestamp), 'h:mm a')}
            </Typography>
          </Paper>
        </Box>
      </Box>
    </Box>
  );
};
