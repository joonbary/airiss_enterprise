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
    fontFamily: '"Noto Sans KR", "Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 700,  // Bold
      fontFamily: '"Inter", "Noto Sans KR", sans-serif',
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 700,  // Bold
      fontFamily: '"Inter", "Noto Sans KR", sans-serif',
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 700,  // Bold
      fontFamily: '"Inter", "Noto Sans KR", sans-serif',
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 600,  // Semibold
      fontFamily: '"Inter", "Noto Sans KR", sans-serif',
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 600,  // Semibold
      fontFamily: '"Inter", "Noto Sans KR", sans-serif',
    },
    h6: {
      fontSize: '1rem',
      fontWeight: 500,  // Medium
      fontFamily: '"Inter", "Noto Sans KR", sans-serif',
    },
    body1: {
      fontWeight: 400,  // Normal
      fontFamily: '"Noto Sans KR", "Inter", sans-serif',
    },
    body2: {
      fontWeight: 400,  // Normal
      fontFamily: '"Noto Sans KR", "Inter", sans-serif',
    },
    button: {
      fontWeight: 500,  // Medium
      textTransform: 'none',
      fontFamily: '"Inter", "Noto Sans KR", sans-serif',
    },
    caption: {
      fontWeight: 400,  // Normal
      fontFamily: '"Noto Sans KR", "Inter", sans-serif',
    },
    overline: {
      fontWeight: 500,  // Medium
      textTransform: 'none',
      fontFamily: '"Inter", "Noto Sans KR", sans-serif',
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
          fontFamily: '"Inter", "Noto Sans KR", sans-serif',
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
    MuiTypography: {
      styleOverrides: {
        root: {
          fontFamily: '"Noto Sans KR", "Inter", sans-serif',
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiInputBase-root': {
            fontFamily: '"Noto Sans KR", "Inter", sans-serif',
          },
        },
      },
    },
  },
});

export default theme;