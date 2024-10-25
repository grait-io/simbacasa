// Declare the global Telegram.WebApp object
declare global {
  interface Window {
    Telegram: {
      WebApp: any;
    };
  }
}

// Initialize Telegram Web App with a getter to ensure it's available
let _tg: any = null;

const getTg = () => {
  if (!_tg) {
    _tg = window.Telegram?.WebApp;
    if (_tg) {
      _tg.expand();
    }
  }
  return _tg;
};

// Export the Telegram Web App instance getter
export default getTg();
