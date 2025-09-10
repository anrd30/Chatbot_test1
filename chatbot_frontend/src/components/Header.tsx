import { AppBar, Toolbar, Typography, Button, Box, useTheme } from '@mui/material';
import ChatIcon from '@mui/icons-material/Chat';
import AddIcon from '@mui/icons-material/Add';

interface HeaderProps {
  onNewChat: () => void;
}

export function Header({ onNewChat }: HeaderProps) {
  const theme = useTheme();
  
  return (
    <AppBar 
      position="static" 
      color="default" 
      elevation={0}
      sx={{
        borderBottom: `1px solid ${theme.palette.divider}`,
        backgroundColor: theme.palette.background.paper,
      }}
    >
      <Toolbar sx={{ justifyContent: 'space-between' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <ChatIcon color="primary" />
          <Typography 
            variant="h6" 
            component="h1" 
            color="primary"
            sx={{
              fontWeight: 600,
              background: `linear-gradient(45deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              display: 'inline',
            }}
          >
            IIT RPR Chatbot
          </Typography>
        </Box>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={onNewChat}
          sx={{
            borderRadius: '20px',
            textTransform: 'none',
            fontWeight: 500,
            boxShadow: '0 2px 10px rgba(25, 118, 210, 0.2)',
            '&:hover': {
              boxShadow: '0 4px 12px rgba(25, 118, 210, 0.3)',
            },
          }}
        >
          New Chat
        </Button>
      </Toolbar>
    </AppBar>
  );
}
