// Declare the global Telegram.WebApp object
declare global {
  interface Window {
    Telegram: {
      WebApp: any;
    };
  }
}

// Initialize Telegram Web App
const tg = window.Telegram.WebApp;

// Expand the WebApp to its maximum size
tg.expand();

// Export the Telegram Web App instance
export default tg;
 