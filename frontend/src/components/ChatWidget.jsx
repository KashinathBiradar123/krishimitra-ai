// Chat widget
import React, { useState, useRef, useEffect } from "react";
import toast from "react-hot-toast";
import "./ChatWidget.css";

const API_BASE_URL = "http://localhost:8000/api";

function ChatWidget() {
  const [messages, setMessages] = useState([
    { 
      text: "Hello! I am KrishiMitra AI 🌱. How can I help you with your farm today?", 
      sender: "bot",
      timestamp: new Date().toLocaleTimeString()
    }
  ]);

  const [input, setInput] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Generate session ID on mount
  useEffect(() => {
    const newSessionId = Math.random().toString(36).substring(2, 10);
    setSessionId(newSessionId);
  }, []);

  // Auto-scroll to bottom
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Focus input when chat opens
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { 
      text: input, 
      sender: "user",
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setIsTyping(true);

    try {
      // Call backend API
      const response = await fetch(`${API_BASE_URL}/chat/message`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: input,
          session_id: sessionId,
          history: messages.slice(-5) // Send last 5 messages for context
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to get response");
      }

      const data = await response.json();

      // Add bot response
      const botMessage = {
        text: data.response || "I'm here to help with your farming questions!",
        sender: "bot",
        timestamp: new Date().toLocaleTimeString(),
        suggestions: data.suggestions || []
      };

      setMessages(prev => [...prev, botMessage]);

    } catch (error) {
      console.error("Chat error:", error);
      
      // Fallback response
      const fallbackMessage = {
        text: "I'm having trouble connecting. Please try again in a moment.",
        sender: "bot",
        timestamp: new Date().toLocaleTimeString(),
        isError: true
      };
      
      setMessages(prev => [...prev, fallbackMessage]);
      toast.error("Failed to get response from AI");
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setInput(suggestion);
    setTimeout(() => sendMessage(), 100);
  };

  const clearChat = () => {
    setMessages([
      { 
        text: "Hello! I am KrishiMitra AI 🌱. How can I help you with your farm today?", 
        sender: "bot",
        timestamp: new Date().toLocaleTimeString()
      }
    ]);
    toast.success("Chat cleared");
  };

  // Suggested questions
  const suggestions = [
    "How to grow wheat?",
    "Best fertilizer for tomato",
    "Aphid control",
    "Current potato price",
    "Weather for farming"
  ];

  return (
    <div className="chat-widget-container">
      
      {/* Chat Toggle Button */}
      <button 
        className={`chat-toggle-btn ${isOpen ? 'open' : ''}`}
        onClick={() => setIsOpen(!isOpen)}
      >
        {isOpen ? "✕" : "💬"}
        {!isOpen && <span className="notification-dot"></span>}
      </button>

      {/* Chat Window */}
      {isOpen && (
        <div className="chat-window">
          
          {/* Header */}
          <div className="chat-header">
            <div className="chat-header-info">
              <h3>🤖 KrishiMitra AI</h3>
              <span className="chat-status">Online</span>
            </div>
            <div className="chat-header-actions">
              <button onClick={clearChat} className="clear-btn" title="Clear chat">🗑️</button>
              <button onClick={() => setIsOpen(false)} className="close-btn">✕</button>
            </div>
          </div>

          {/* Messages */}
          <div className="chat-messages">
            {messages.map((msg, index) => (
              <div
                key={index}
                className={`message ${msg.sender === "user" ? "user-message" : "bot-message"} ${msg.isError ? 'error-message' : ''}`}
              >
                <div className="message-avatar">
                  {msg.sender === "user" ? "👤" : "🤖"}
                </div>
                <div className="message-content">
                  <div className="message-text">{msg.text}</div>
                  <div className="message-time">{msg.timestamp}</div>
                </div>
              </div>
            ))}
            
            {/* Typing indicator */}
            {isTyping && (
              <div className="message bot-message">
                <div className="message-avatar">🤖</div>
                <div className="message-content">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Suggestions */}
          {messages.length < 3 && (
            <div className="suggestions">
              <p className="suggestions-title">Try asking:</p>
              <div className="suggestion-chips">
                {suggestions.map((suggestion, index) => (
                  <button
                    key={index}
                    className="suggestion-chip"
                    onClick={() => handleSuggestionClick(suggestion)}
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Input Area */}
          <div className="chat-input-area">
            <input
              ref={inputRef}
              type="text"
              placeholder="Ask about crops, pests, weather..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              className="chat-input"
              disabled={isTyping}
            />
            <button 
              onClick={sendMessage} 
              className="send-btn"
              disabled={!input.trim() || isTyping}
            >
              {isTyping ? "..." : "📤"}
            </button>
          </div>

          {/* Footer */}
          <div className="chat-footer">
            <span>AI-powered farming assistant</span>
          </div>
        </div>
      )}
    </div>
  );
}

export default ChatWidget;