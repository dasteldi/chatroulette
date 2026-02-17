// components/ChatWindow.tsx
import React, { useEffect, useRef } from 'react';
import '../index.css';

interface Message {
  id: string;
  text: string;
  sender: 'me' | 'partner';
  timestamp: Date;
}

interface User {
  id: string;
  name: string;
}

interface ChatWindowProps {
  messages: Message[];
  currentUser: User;
  partner: User | null;
}

export const ChatWindow: React.FC<ChatWindowProps> = ({ 
  messages, 
  currentUser, 
  partner 
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const formatTime = (date: Date): string => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="chat-window">
      {messages.length === 0 && (
        <div className="chat-welcome">
          <p>Добро пожаловать в чат-рулетку!</p>
          <p>Нажмите "Найти собеседника" чтобы начать общение</p>
        </div>
      )}
      
      <div className="messages-container">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`message-wrapper ${
              message.sender === 'me' ? 'my-message' : 'partner-message'
            }`}
          >
            <div className="message-bubble">
              {message.sender === 'partner' && partner && (
                <div className="message-sender">{partner.name}</div>
              )}
              {message.sender === 'me' && (
                <div className="message-sender">Вы</div>
              )}
              <div className="message-text">{message.text}</div>
              <div className="message-time">{formatTime(message.timestamp)}</div>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};