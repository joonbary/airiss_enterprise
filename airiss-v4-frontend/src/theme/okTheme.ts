import { createTheme } from '@mui/material/styles';

// OK금융그룹 색상 팔레트
const okColors = {
  primary: '#FF5722',      // OK 오렌지
  secondary: '#4A4A4A',    // OK 다크 브라운
  warning: '#F89C26',      // OK 옐로우
  grey: '#B3B3B3',         // OK 브라이트 그레이
  white: '#FFFFFF',
  black: '#000000',
  darkGrey: '#6A6A6A',
  lightGrey: '#F5F5F5',
  success: '#4CAF50',
  error: '#F44336',
};

const theme = createTheme({
  palette: {
    primary: {
      main: okColors.primary,
      light: '#FF8A50',
      dark: '#C41C00',
      contrastText: okColors.white,
    },
    secondary: {
      main: okColors.secondary,
      light: '#757575',
      dark: '#212121',
      contrastText: okColors.white,
    },
    warning: {
      main: okColors.warning,
      light: '#FFB74D',
      dark: '#F57C00',
      contrastText: okColors.white,
    },
    error: {
      main: okColors.error,
    },
    success: {
      main: okColors.success,
    },
    grey: {
      50: okColors.lightGrey,
      100: '#F5F5F5',
      200: '#EEEEEE',
      300: '#E0E0E0',
      400: '#BDBDBD',
      500: okColors.grey,
      600: '#757575',
      700: okColors.darkGrey,
      800: okColors.secondary,
      900: '#212121',
    },
    background: {
      default: '#FAFAFA',
      paper: okColors.white,
    },
  },
  typography: {
    fontFamily: "'OK', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif",
    h1: {
      fontWeight: 700,
      fontSize: '2.5rem',
      letterSpacing: '-0.02em',
    },
    h2: {
      fontWeight: 700,
      fontSize: '2rem',
      letterSpacing: '-0.01em',
    },
    h3: {
      fontWeight: 700,
      fontSize: '1.75rem',
      letterSpacing: '-0.01em',
    },
    h4: {
      fontWeight: 700,
      fontSize: '1.5rem',
      letterSpacing: '-0.01em',
    },
    h5: {
      fontWeight: 500,
      fontSize: '1.25rem',
    },
    h6: {
      fontWeight: 500,
      fontSize: '1rem',
    },
    subtitle1: {
      fontWeight: 500,
      fontSize: '1rem',
      lineHeight: 1.75,
    },
    subtitle2: {
      fontWeight: 500,
      fontSize: '0.875rem',
      lineHeight: 1.57,
    },
    body1: {
      fontWeight: 300,
      fontSize: '1rem',
      lineHeight: 1.5,
    },
    body2: {
      fontWeight: 300,
      fontSize: '0.875rem',
      lineHeight: 1.43,
    },
    button: {
      fontWeight: 500,
      fontSize: '0.875rem',
      letterSpacing: '0.02em',
      textTransform: 'none',
    },
    caption: {
      fontWeight: 300,
      fontSize: '0.75rem',
      lineHeight: 1.66,
    },
    overline: {
      fontWeight: 500,
      fontSize: '0.75rem',
      letterSpacing: '0.08em',
      textTransform: 'uppercase',
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          padding: '8px 24px',
          fontWeight: 500,
          transition: 'all 0.3s ease',
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: '0 4px 12px rgba(255, 87, 34, 0.3)',
          },
        },
        contained: {
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.05)',
          transition: 'all 0.3s ease',
          '&:hover': {
            boxShadow: '0 8px 24px rgba(0, 0, 0, 0.1)',
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 12,
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          fontWeight: 500,
        },
      },
    },
    MuiTypography: {
      styleOverrides: {
        root: {
          fontFamily: "'OK', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif",
        },
      },
    },
  },
});

export default theme;