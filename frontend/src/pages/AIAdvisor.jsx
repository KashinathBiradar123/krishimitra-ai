// AI advisor page
import React, { useState, useEffect, useContext, useRef } from "react";
import { Link } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import toast from "react-hot-toast";
import "./AIAdvisor.css";

const API_BASE_URL = "http://localhost:8000/api";

function AIAdvisor() {
  const { user } = useContext(AuthContext);
  const messagesEndRef = useRef(null);
  
  // State for chat
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: "👋 **Namaste!** I'm your KrishiMitra AI farming assistant. How can I help you with your farm today?",
      timestamp: new Date().toISOString()
    }
  ]);
  const [inputMessage, setInputMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [suggestions, setSuggestions] = useState([
    "How to grow wheat?",
    "Best fertilizer for tomato",
    "Aphid control in mustard",
    "Current potato price",
    "Weather impact on crops"
  ]);
  const [chatInfo, setChatInfo] = useState(null);

  // Scroll to bottom when messages update
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Fetch chat info on mount
  useEffect(() => {
    fetchChatInfo();
    // Generate or get session ID
    const existingSession = localStorage.getItem("chatSessionId");
    if (existingSession) {
      setSessionId(existingSession);
    } else {
      const newSession = Math.random().toString(36).substring(2, 10);
      localStorage.setItem("chatSessionId", newSession);
      setSessionId(newSession);
    }
  }, []);

  // 👈 FIX 2: Added safety check for scroll
  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  };

  // Fetch chat info from backend
  const fetchChatInfo = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/chat/`);
      if (response.ok) {
        const data = await response.json();
        setChatInfo(data);
      }
    } catch (error) {
      console.error("Failed to fetch chat info:", error);
    }
  };

  // Send message to backend
  const sendMessage = async (messageText = inputMessage) => {
    // 👈 FIX 3: Prevent double messages
    if (loading) return;
    
    if (!messageText.trim()) return;
    
    if (!user) {
      toast.error("Please login to chat with AI Advisor", {
        icon: "🔒",
        duration: 3000
      });
      return;
    }

    // Add user message to UI
    const userMessage = {
      role: "user",
      content: messageText,
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, userMessage]);
    setInputMessage(""); // Clear input immediately
    setLoading(true);

    try {
      // Prepare chat history for context
      const chatHistory = messages
        .filter(msg => msg.role !== "system")
        .slice(-6); // Last 6 messages for context

      const response = await fetch(`${API_BASE_URL}/chat/message`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: messageText,
          session_id: sessionId,
          history: chatHistory,
          language: "english",
          farmer_id: user?.id || null
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to get response");
      }

      const data = await response.json();

      // Add assistant response to UI
      const assistantMessage = {
        role: "assistant",
        content: data.response,
        timestamp: data.timestamp,
        confidence: data.confidence,
        category: data.category,
        follow_up: data.follow_up_questions,
        action_items: data.action_items
      };
      
      setMessages(prev => [...prev, assistantMessage]);

      // Update suggestions if available
      if (data.suggestions && data.suggestions.length > 0) {
        setSuggestions(data.suggestions);
      }

      // Show confidence for debugging (optional)
      if (data.confidence < 0.5) {
        toast("I'm not fully confident about this answer. Please verify with local experts.", {
          icon: "⚠️",
          duration: 4000
        });
      }

    } catch (error) {
      toast.error(error.message || "Failed to send message");
      console.error("Chat error:", error);
    } finally {
      setLoading(false);
    }
  };

  // Handle form submit
  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage();
  };

  // 👈 FIX 1: Fixed suggestion click handler
  const handleSuggestionClick = (suggestion) => {
    sendMessage(suggestion);
  };

  // Handle key press for Enter key
  const handleKeyDown = (e) => {
    // 👈 NEW: Enter to send (like WhatsApp/ChatGPT)
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault(); // Prevent new line
      sendMessage();
    }
  };

  // Clear chat history
  const handleClearChat = () => {
    if (window.confirm("Clear chat history?")) {
      setMessages([
        {
          role: "assistant",
          content: "👋 **Namaste!** I'm your KrishiMitra AI farming assistant. How can I help you with your farm today?",
          timestamp: new Date().toISOString()
        }
      ]);
      toast.success("Chat cleared");
    }
  };

  // Format timestamp
  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  // Render message content with markdown-like formatting
  const renderMessage = (content) => {
    // Simple formatting: bold text between ** **
    const parts = content.split(/(\*\*.*?\*\*)/g);
    return parts.map((part, index) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={index}>{part.slice(2, -2)}</strong>;
      }
      return part;
    });
  };

  // If not logged in, show login prompt
  if (!user) {
    return (
      <div className="advisor-login-prompt">
        <div className="lock-icon">🔒</div>
        <h2>Login Required</h2>
        <p>Please login to access the AI Advisor and get personalized farming advice.</p>
        <Link to="/login" className="btn btn-primary">
          Login to Continue
        </Link>
        <p className="guest-note">
          New here? <Link to="/signup">Create an account</Link> - It's free!
        </p>
      </div>
    );
  }

  return (
    <div className="advisor-page">
      
      {/* Header */}
      <div className="advisor-header">
        <div className="advisor-title">
          <h1>🤖 AI Farming Advisor</h1>
          <p>Ask me anything about farming, crops, pests, or markets</p>
        </div>
        <div className="advisor-actions">
          <button onClick={handleClearChat} className="btn btn-outline" title="Clear chat">
            🗑️ Clear
          </button>
        </div>
      </div>

      {/* Chat Info Banner */}
      {chatInfo && (
        <div className="chat-info-banner">
          <span>✨ {chatInfo.capabilities?.length || 5}+ farming topics</span>
          <span>🌱 {chatInfo.languages_supported?.[0] || "English"}</span>
          <span className="disclaimer">{chatInfo.disclaimer}</span>
        </div>
      )}

      {/* Chat Container */}
      <div className="chat-container">
        
        {/* Messages Area */}
        <div className="messages-area">
          {messages.map((msg, index) => (
            <div 
              key={index} 
              className={`message ${msg.role === "user" ? "user-message" : "assistant-message"}`}
            >
              <div className="message-avatar">
                {msg.role === "user" ? "👤" : "🤖"}
              </div>
              <div className="message-content">
                <div className="message-header">
                  <span className="message-sender">
                    {msg.role === "user" ? "You" : "KrishiMitra AI"}
                  </span>
                  <span className="message-time">{formatTime(msg.timestamp)}</span>
                </div>
                <div className="message-text">
                  {renderMessage(msg.content)}
                </div>
                
                {/* Show confidence for assistant messages */}
                {msg.role === "assistant" && msg.confidence && (
                  <div className="message-confidence">
                    Confidence: {Math.round(msg.confidence * 100)}%
                  </div>
                )}
                
                {/* Show action items */}
                {msg.role === "assistant" && msg.action_items?.length > 0 && (
                  <div className="action-items">
                    <strong>📋 Action Items:</strong>
                    <ul>
                      {msg.action_items.map((item, i) => (
                        <li key={i}>{item}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {/* Show follow-up questions */}
                {msg.role === "assistant" && msg.follow_up?.length > 0 && (
                  <div className="follow-up">
                    <strong>💡 You might also ask:</strong>
                    <div className="follow-up-buttons">
                      {msg.follow_up.map((question, i) => (
                        <button
                          key={i}
                          className="follow-up-btn"
                          onClick={() => handleSuggestionClick(question)}
                        >
                          {question}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
          
          {/* Loading indicator */}
          {loading && (
            <div className="message assistant-message">
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

        {/* Suggestions Area */}
        {suggestions.length > 0 && !loading && (
          <div className="suggestions-area">
            <p className="suggestions-title">💬 Suggested questions:</p>
            <div className="suggestions-list">
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
        <form onSubmit={handleSubmit} className="chat-input-form">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyDown={handleKeyDown}  // 👈 NEW: Enter key handler
            placeholder="Ask about crops, fertilizers, pests, weather, markets... (Press Enter to send)"
            className="chat-input"
            disabled={loading}
          />
          <button 
            type="submit" 
            className="send-button"
            disabled={loading || !inputMessage.trim()}
          >
            {loading ? "..." : "📤 Send"}
          </button>
        </form>

        {/* Quick Actions */}
        <div className="quick-actions">
          <button 
            className="quick-action-btn"
            onClick={() => handleSuggestionClick("What crops should I plant this season?")}
          >
            🌱 Crop Planning
          </button>
          <button 
            className="quick-action-btn"
            onClick={() => handleSuggestionClick("How to control pests naturally?")}
          >
            🐛 Pest Control
          </button>
          <button 
            className="quick-action-btn"
            onClick={() => handleSuggestionClick("Best fertilizer for vegetables")}
          >
            🧪 Fertilizer
          </button>
          <button 
            className="quick-action-btn"
            onClick={() => handleSuggestionClick("Current market prices")}
          >
            💰 Market Prices
          </button>
        </div>
      </div>

      {/* Footer note */}
      <div className="advisor-footer">
        <p>
          ⚠️ AI-generated advice. Always consult with local agricultural experts for critical decisions.
          <br />
          <Link to="/feedback">Give Feedback</Link> to help us improve.
        </p>
      </div>
    </div>
  );
}

export default AIAdvisor;