// components/UserInfo.tsx
import React from 'react';
import '../index.css';

interface User {
  id: string;
  name: string;
  isOnline: boolean;
}

interface UserInfoProps {
  user: User;
  partner: User | null;
  isConnected: boolean;
  isSearching: boolean;
}

export const UserInfo: React.FC<UserInfoProps> = ({
  user,
  partner,
  isConnected,
  isSearching
}) => {
  return (
    <div className="user-info">
      <div className="current-user">
        <span className="user-name">{user.name}</span>
        <span className="user-status online">●</span>
      </div>
      
      {isSearching && (
        <div className="search-status">
          <span className="searching">🔍 Поиск собеседника...</span>
        </div>
      )}
      
      {isConnected && partner && (
        <div className="partner-info">
          <span className="separator">↔</span>
          <div className="partner-details">
            <span className="partner-name">{partner.name}</span>
            <span className="partner-status online">●</span>
          </div>
        </div>
      )}
    </div>
  );
};