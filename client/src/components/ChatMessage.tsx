import React from 'react';
import ReactMarkdown from 'react-markdown';
import { User, Bot, FileCode } from 'lucide-react';
import type { Source } from '../services/api';

export interface Message {
  role: 'user' | 'ai';
  content: string;
  sources?: Source[];
}

export const ChatMessage: React.FC<{ message: Message }> = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <div className={`message ${message.role}`}>
      <div className="avatar">
        {isUser ? <User size={20} /> : <Bot size={20} />}
      </div>
      
      <div style={{ flex: 1 }}>
        <div className="message-content">
          <ReactMarkdown>{message.content}</ReactMarkdown>
        </div>
        
        {message.sources && message.sources.length > 0 && (
          <div className="sources-container">
            <div className="sources-title">
              Sources Referenced ({message.sources.length})
            </div>
            <div className="sources-list">
              {message.sources.map((source, index) => (
                <div key={index} className="source-item">
                  <FileCode size={16} className="source-icon" />
                  <div>
                    <div className="source-name">{source.name}</div>
                    <div className="source-path">{source.file_path}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
