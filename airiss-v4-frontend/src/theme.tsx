import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    primary: {
      main: '#FF5722', // OK 오렌지
      light: '#FF8A50',
      dark: '#E64A19',
    },
    secondary: {
      main: '#4A4A4A', // OK 다크브라운
      light: '#6A6A6A',
      dark: '#2C2C2C',
    },
    warning: {
      main: '#F89C26', // OK 옐로우
    },
    grey: {
      300: '#B3B3B3', // OK 브라이트그레이
    },
    background: {
      default: '#FAFAFA',
      paper: '#FFFFFF',
    },
  },
  typography: {
    fontFamily: '"OKFont", "Noto Sans KR", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 700,  // Bold
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 700,  // Bold
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 700,  // Bold
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 500,  // Medium
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 500,  // Medium
    },
    h6: {
      fontSize: '1rem',
      fontWeight: 500,  // Medium
    },
    body1: {
      fontWeight: 300,  // Light
    },
    body2: {
      fontWeight: 300,  // Light
    },
    button: {
      fontWeight: 500,  // Medium
      textTransform: 'none',
    },
    caption: {
      fontWeight: 300,  // Light
    },
    overline: {
      fontWeight: 500,  // Medium
      textTransform: 'none',
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 500,  // Medium
          fontFamily: 'OKFont, sans-serif',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        },
      },
    },
  },
});

export default theme;