import React, { useState, useEffect, useRef } from 'react';
import '../index.css';

// Глобальные переменные для защиты
let isWebSocketCreated = false;
let connectionAttempts = 0;

const TextChat: React.FC = () => {
  const [messages, setMessages] = useState<any[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [inChat, setInChat] = useState(false);
  const [partner, setPartner] = useState<any>(null);
  const [inputText, setInputText] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  
  const ws = useRef<WebSocket | null>(null);
  const userId = useRef<string>('');
  const mounted = useRef(true);

  const connectWebSocket = () => {
    // МАКСИМАЛЬНАЯ ЗАЩИТА
    if (isWebSocketCreated) {
      console.log('⛔ WebSocket already created, skipping...');
      return;
    }
    
    if (!mounted.current) return;
    
    connectionAttempts++;
    if (connectionAttempts > 1) {
      console.log(`⛔ Connection attempt #${connectionAttempts} blocked`);
      return;
    }
    
    let uid = localStorage.getItem('userId');
    if (!uid) {
      uid = 'user_' + Math.random().toString(36).substring(2, 8);
      localStorage.setItem('userId', uid);
    }
    userId.current = uid;

    console.log('🚀 Creating WebSocket for user:', uid);
    console.log('📡 URL:', `ws://localhost:8000/ws/${uid}`);
    
    const socket = new WebSocket(`ws://localhost:8000/ws/${uid}`);
    isWebSocketCreated = true;
    
    socket.onopen = () => {
      if (!mounted.current) return;
      console.log('✅ WebSocket OPEN');
      setIsConnected(true);
      
      socket.send(JSON.stringify({
        type: 'user:join',
        data: {
          name: 'User_' + uid.substring(0, 4)
        }
      }));
    };
    
    socket.onmessage = (event) => {
      if (!mounted.current) return;
      
      try {
        const msg = JSON.parse(event.data);
        console.log('📩 Received:', msg);
        
        switch(msg.type) {
          case 'user:joined':
            console.log('✅ Joined server');
            break;
            
          case 'searching':
            setIsSearching(true);
            setMessages(prev => [...prev, {
              id: Date.now(),
              text: '🔍 Ищем собеседника...',
              type: 'system'
            }]);
            break;
            
          case 'partner:found':
            console.log('🎉 PARTNER FOUND!', msg.data);
            
            // Проверяем, что это не мы сами
            if (msg.data.partner.id === userId.current) {
              console.log('❌ Нашел сам себя, продолжаем поиск...');
              setTimeout(() => {
                if (ws.current?.readyState === WebSocket.OPEN && mounted.current) {
                  ws.current.send(JSON.stringify({
                    type: 'partner:search',
                    data: {}
                  }));
                }
              }, 1000);
              return;
            }
            
            setIsSearching(false);
            setInChat(true);
            setPartner(msg.data.partner);
            setMessages(prev => [...prev, {
              id: Date.now(),
              text: `✅ Найден собеседник: ${msg.data.partner.name}`,
              type: 'system'
            }]);
            break;
            
          case 'message:receive':
            setMessages(prev => [...prev, {
              id: Date.now(),
              text: msg.data.text,
              type: 'partner',
              name: msg.data.sender_name
            }]);
            break;
            
          case 'partner:disconnected':
            setInChat(false);
            setPartner(null);
            setMessages(prev => [...prev, {
              id: Date.now(),
              text: '❌ Собеседник отключился',
              type: 'system'
            }]);
            break;
        }
      } catch (e) {
        console.error('Error parsing message:', e);
      }
    };
    
    socket.onclose = () => {
      if (!mounted.current) return;
      console.log('❌ WebSocket CLOSED');
      setIsConnected(false);
      setIsSearching(false);
      setInChat(false);
      setPartner(null);
      isWebSocketCreated = false;
      connectionAttempts = 0;
    };
    
    socket.onerror = (error) => {
      console.error('WebSocket ERROR:', error);
    };
    
    ws.current = socket;
  };

  useEffect(() => {
    mounted.current = true;
    connectWebSocket();
    
    return () => {
      mounted.current = false;
      if (ws.current) {
        ws.current.close();
        isWebSocketCreated = false;
        connectionAttempts = 0;
      }
    };
  }, []);

  const handleSearch = () => {
    if (!ws.current || ws.current.readyState !== WebSocket.OPEN) {
      console.error('WebSocket not connected');
      return;
    }
    
    console.log('🔍 Sending search request...');
    ws.current.send(JSON.stringify({
      type: 'partner:search',
      data: {}
    }));
  };

  const handleSend = () => {
    if (!inputText.trim() || !inChat) return;
    if (!ws.current || ws.current.readyState !== WebSocket.OPEN) return;
    
    ws.current.send(JSON.stringify({
      type: 'message:send',
      data: { text: inputText }
    }));
    
    setMessages(prev => [...prev, {
      id: Date.now(),
      text: inputText,
      type: 'me'
    }]);
    
    setInputText('');
  };

  const handleDisconnect = () => {
    if (!ws.current || ws.current.readyState !== WebSocket.OPEN) return;
    
    ws.current.send(JSON.stringify({
      type: 'partner:disconnect',
      data: {}
    }));
    window.location.reload();
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <div className="user-info">
          <span className="user-name">
            👤 User_{userId.current?.substring(0,4)}
          </span>
          
          <span className={`status ${isConnected ? 'online' : 'offline'}`}>
            {isConnected ? '● Online' : '○ Offline'}
          </span>
          
          {partner && (
            <span className="partner-name">
              ↔ {partner.name}
            </span>
          )}
          {isSearching && (
            <span className="searching">
              🔍 Поиск...
            </span>
          )}
        </div>
        
        <div className="chat-controls">
          {!inChat && !isSearching && isConnected && (
            <button
              className="btn btn-primary"
              onClick={handleSearch}
            >
              Найти собеседника
            </button>
          )}
          {inChat && (
            <button
              className="btn btn-danger"
              onClick={handleDisconnect}
            >
              Отключиться
            </button>
          )}
        </div>
      </div>

      <div className="messages-area">
        {messages.length === 0 && (
          <div className="welcome-message">
            {isConnected 
              ? 'Нажмите "Найти собеседника" чтобы начать общение'
              : 'Подключение к серверу...'}
          </div>
        )}
        
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`message-wrapper ${msg.type === 'me' ? 'my-message' : 'other-message'}`}
          >
            <div className={`message-bubble ${msg.type}`}>
              {msg.type === 'partner' && (
                <div className="message-sender">
                  {msg.name}
                </div>
              )}
              <div className="message-text">
                {msg.text}
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="input-area">
        <input
          type="text"
          className="message-input"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder={inChat ? "Введите сообщение..." : "Нет собеседника"}
          disabled={!inChat}
        />
        <button
          className="send-button"
          onClick={handleSend}
          disabled={!inChat || !inputText.trim()}
        >
          Отправить
        </button>
      </div>
    </div>
  );
};

export default TextChat;