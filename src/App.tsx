// App.tsx
import React from 'react';
import { TextChat } from '../components/TextChat.tsx';
import './index.css';

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>Текстовая Чат-Рулетка</h1>
      </header>
      <main className="app-main">
        <TextChat />
      </main>
    </div>
  );
}

export default App;