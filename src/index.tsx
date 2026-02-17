import React from 'react';
import ReactDOM from 'react-dom/client';
import TextChat from './components/TextChat.tsx';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(<TextChat />);