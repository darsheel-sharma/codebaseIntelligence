import React, { useState, useRef, useEffect } from 'react';
import { Database, Terminal, Send, Loader2 } from 'lucide-react';
import { ChatMessage, type Message } from './components/ChatMessage';
import { ingestCodebase, queryCodebase } from './services/api';

function App() {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'ai', content: 'Hello! I am your Codebase Intelligence Assistant. What would you like to know about your code?' }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  
  const [directory, setDirectory] = useState('D:/Work/InternPrep/AIML/Project1/server/app');
  const [isIngesting, setIsIngesting] = useState(false);
  const [ingestStatus, setIngestStatus] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsTyping(true);

    try {
      const response = await queryCodebase(userMessage);
      setMessages(prev => [...prev, { 
        role: 'ai', 
        content: response.answer,
        sources: response.sources
      }]);
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      setMessages(prev => [...prev, { 
        role: 'ai', 
        content: `**Error:** ${errorMessage}` 
      }]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleIngest = async () => {
    if (!directory) return;
    
    setIsIngesting(true);
    setIngestStatus('Ingesting chunks... This may take a moment.');
    try {
      const res = await ingestCodebase(directory);
      setIngestStatus(`Success! Ingested ${res.chunks_ingested} code chunks.`);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : String(err);
      setIngestStatus(`Error: ${errorMessage}`);
    } finally {
      setIsIngesting(false);
    }
  };

  return (
    <div className="app-container">
      {/* Sidebar Configuration Panel */}
      <div className="sidebar">
        <div className="logo">
          <Terminal size={24} />
          Codebase Intelligence
        </div>
        
        <div className="card">
          <h3>Codebase Indexing</h3>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
            Point the assistant to a local directory to parse, chunk, and embed the code into the vector database.
          </p>
          
          <input 
            type="text" 
            value={directory}
            onChange={(e) => setDirectory(e.target.value)}
            placeholder="C:/path/to/project"
            style={{ marginBottom: '1rem' }}
          />
          
          <button 
            onClick={handleIngest} 
            disabled={isIngesting}
          >
            {isIngesting ? <Loader2 size={18} className="animate-spin" /> : <Database size={18} />}
            {isIngesting ? 'Ingesting...' : 'Ingest Codebase'}
          </button>
          
          {ingestStatus && (
            <div style={{ marginTop: '1rem', fontSize: '0.8rem', color: ingestStatus.includes('Error') ? 'var(--error)' : 'var(--success)' }}>
              {ingestStatus}
            </div>
          )}
        </div>
      </div>

      {/* Main Chat Interface */}
      <div className="chat-container">
        <div className="chat-history">
          {messages.map((msg, idx) => (
            <ChatMessage key={idx} message={msg} />
          ))}
          
          {isTyping && (
            <div className="message ai">
              <div className="avatar">
                <Terminal size={20} />
              </div>
              <div className="message-content">
                <div className="typing-indicator">
                  <div className="dot"></div>
                  <div className="dot"></div>
                  <div className="dot"></div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form className="input-area" onSubmit={handleSendMessage}>
          <div className="input-wrapper">
            <input 
              type="text" 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question about your code..."
              disabled={isTyping}
            />
            <button type="submit" className="send-btn" disabled={!input.trim() || isTyping}>
              <Send size={18} />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default App;
