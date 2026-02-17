type MessageHandler = (data: any) => void;

export class WebSocketService {
  private ws: WebSocket | null = null;
  private handlers: Map<string, MessageHandler[]> = new Map();
  private userId: string;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 3; // Уменьшил количество попыток
  private reconnectTimeout: NodeJS.Timeout | null = null;
  private intentionalClose = false; // Флаг для намеренного закрытия

  constructor(userId: string) {
    this.userId = userId;
    this.connect();
  }

  private connect() {
    // Если уже есть соединение, не создаем новое
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected');
      return;
    }

    const wsUrl = `ws://localhost:8000/ws/${this.userId}`;
    console.log('🔄 Connecting to WebSocket:', wsUrl);
    
    try {
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('✅ WebSocket connected successfully');
        this.reconnectAttempts = 0;
        this.emit('connect', null);
        
        // Отправляем информацию о пользователе
        const userName = localStorage.getItem('userName') || `User_${this.userId.slice(0,4)}`;
        this.emit('user:join', { name: userName });
      };

      this.ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          console.log('📩 Received:', message.type, message.data);
          
          const handlers = this.handlers.get(message.type) || [];
          handlers.forEach(handler => handler(message.data));
        } catch (error) {
          console.error('Error parsing message:', error);
        }
      };

      this.ws.onclose = (event) => {
        console.log('❌ WebSocket disconnected:', event.reason);
        
        // Очищаем все обработчики
        this.handlers.clear();
        
        // Если это не намеренное закрытие и есть попытки переподключения
        if (!this.intentionalClose && this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnectAttempts++;
          console.log(`🔄 Reconnecting... Attempt ${this.reconnectAttempts}`);
          
          if (this.reconnectTimeout) {
            clearTimeout(this.reconnectTimeout);
          }
          
          this.reconnectTimeout = setTimeout(() => this.connect(), 2000);
        }
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
    } catch (error) {
      console.error('Error creating WebSocket:', error);
    }
  }

  public on(event: string, handler: MessageHandler) {
    if (!this.handlers.has(event)) {
      this.handlers.set(event, []);
    }
    this.handlers.get(event)?.push(handler);
  }

  public off(event: string, handler: MessageHandler) {
    const handlers = this.handlers.get(event);
    if (handlers) {
      const index = handlers.indexOf(handler);
      if (index !== -1) {
        handlers.splice(index, 1);
      }
    }
  }

  public emit(event: string, data: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      const message = JSON.stringify({ type: event, data });
      console.log('📤 Sending:', event, data);
      this.ws.send(message);
    } else {
      console.warn('WebSocket not connected, state:', this.ws?.readyState);
    }
  }

  public disconnect() {
    this.intentionalClose = true; // Помечаем как намеренное закрытие
    
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
    }
    
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    
    this.handlers.clear();
  }

  public isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }
}