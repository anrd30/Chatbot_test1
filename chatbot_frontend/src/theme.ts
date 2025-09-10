import { createTheme } from '@mui/material/styles';

declare module '@mui/material/styles' {
  interface Theme {
    custom: {
      maxWidth: string;
      drawerWidth: number;
    };
  }
  interface ThemeOptions {
    custom?: {
      maxWidth?: string;
      drawerWidth?: number;
    };
  }
}

export const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#0066cc',
      light: '#338fff',
      dark: '#004499',
      contrastText: '#fff',
    },
    secondary: {
      main: '#ffffff',
      light: '#ffffff',
      dark: '#cccccc',
      contrastText: '#000',
    },
    background: {
      default: '#000000',
      paper: '#0a0a0a',
    },
    text: {
      primary: '#ffffff',
      secondary: '#cccccc',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 600,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 600,
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 600,
    },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 600,
          borderRadius: 8,
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
          backgroundColor: '#1e293b',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundColor: '#1e293b',
          color: '#f1f5f9',
        },
      },
    },
  },
  custom: {
    maxWidth: '1200px',
    drawerWidth: 280,
  },
});
