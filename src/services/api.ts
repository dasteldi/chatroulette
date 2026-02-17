// REST API сервис
const API_URL = 'http://localhost:8000';

export interface UserResponse {
  success: boolean;
  data?: {
    user_id: string;
    name: string;
  };
  error?: string;
}

export interface StatsResponse {
  success: boolean;
  data?: {
    online_users: number;
    waiting_users: number;
    active_chats: number;
    timestamp: string;
  };
}

class ApiService {
  async createUser(): Promise<UserResponse> {
    try {
      const response = await fetch(`${API_URL}/api/user/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error creating user:', error);
      return {
        success: false,
        error: 'Failed to create user'
      };
    }
  }

  async getStats(): Promise<StatsResponse> {
    try {
      const response = await fetch(`${API_URL}/api/stats`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error getting stats:', error);
      return {
        success: false,
        error: 'Failed to get stats'
      };
    }
  }

  async getUserInfo(userId: string) {
    try {
      const response = await fetch(`${API_URL}/api/user/${userId}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error getting user info:', error);
      return {
        success: false,
        error: 'Failed to get user info'
      };
    }
  }
}

export const api = new ApiService();