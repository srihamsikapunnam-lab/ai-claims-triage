import React, { useState, useRef, useEffect } from 'react';
import './Chatbot.css';

const Chatbot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage = {
      id: Date.now(),
      text: inputValue,
      sender: 'user',
      timestamp: new Date().toLocaleTimeString(),
    };

    // Add user message to chat and clear input
    setMessages((prev) => [...prev, userMessage]);
    const messageToSend = inputValue; // Capture message before clearing
    setInputValue('');
    setIsLoading(true);

    try {
      console.log('[CHATBOT] Sending message to backend:', messageToSend);

      const response = await fetch('http://localhost:8001/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: messageToSend,
        }),
      });

      if (!response.ok) {
        // Handle HTTP errors
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.detail || `Server error (${response.status})`
        );
      }

      const data = await response.json();
      console.log('[CHATBOT] Backend response:', data);

      // Extract reply from backend response
      const reply = data.reply || data.response || data.message || 'No response from server';
      const intent = data.intent || 'unknown';

      const botMessage = {
        id: Date.now() + 1,
        text: reply,
        sender: 'bot',
        timestamp: new Date().toLocaleTimeString(),
        intent: intent,
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error('[CHATBOT] Error:', error);

      // User-friendly error message
      let errorText = 'Sorry, I encountered an issue.';
      
      if (error.message.includes('Failed to fetch')) {
        errorText = 'Cannot connect to chat service. Is the server running on port 8001?';
      } else if (error.message.includes('Server error')) {
        errorText = `Server error: ${error.message}`;
      } else {
        errorText = `Sorry, an error occurred: ${error.message}`;
      }

      const errorMessage = {
        id: Date.now() + 2,
        text: errorText,
        sender: 'bot',
        timestamp: new Date().toLocaleTimeString(),
        isError: true,
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    const allowedTypes = ['application/pdf', 'image/jpeg', 'image/png'];
    if (!allowedTypes.includes(file.type)) {
      const errorMessage = {
        id: Date.now(),
        text: '❌ Invalid file type. Please upload PDF, JPG, or PNG only.',
        sender: 'bot',
        timestamp: new Date().toLocaleTimeString(),
        isError: true,
      };
      setMessages((prev) => [...prev, errorMessage]);
      return;
    }

    // Validate file size (5MB)
    const maxSize = 5 * 1024 * 1024; // 5MB in bytes
    if (file.size > maxSize) {
      const errorMessage = {
        id: Date.now(),
        text: `❌ File too large. Maximum size is 5MB (your file: ${(file.size / 1024 / 1024).toFixed(2)}MB)`,
        sender: 'bot',
        timestamp: new Date().toLocaleTimeString(),
        isError: true,
      };
      setMessages((prev) => [...prev, errorMessage]);
      return;
    }

    setSelectedFile(file);
    console.log('[CHATBOT] File selected:', file.name);
  };

  const handleUploadFile = async () => {
    if (!selectedFile) return;

    const userMessage = {
      id: Date.now(),
      text: `📎 Uploaded: ${selectedFile.name}`,
      sender: 'user',
      timestamp: new Date().toLocaleTimeString(),
      isFile: true,
      fileName: selectedFile.name,
    };

    setMessages((prev) => [...prev, userMessage]);
    setSelectedFile(null);
    setIsLoading(true);

    try {
      console.log('[CHATBOT] Uploading file:', selectedFile.name);

      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await fetch('http://localhost:8001/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.detail || `Upload failed (${response.status})`
        );
      }

      const data = await response.json();
      console.log('[CHATBOT] Upload response:', data);

      const botMessage = {
        id: Date.now() + 1,
        text: `✅ ${data.message || 'File uploaded successfully!'}`,
        sender: 'bot',
        timestamp: new Date().toLocaleTimeString(),
        isSuccess: true,
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error('[CHATBOT] Upload error:', error);

      let errorText = 'Failed to upload file.';
      
      if (error.message.includes('Failed to fetch')) {
        errorText = 'Cannot connect to upload service. Is the server running?';
      } else if (error.message.includes('File type not supported')) {
        errorText = '❌ ' + error.message;
      } else if (error.message.includes('File size exceeds')) {
        errorText = '❌ ' + error.message;
      } else {
        errorText = `❌ ${error.message}`;
      }

      const errorMessage = {
        id: Date.now() + 2,
        text: errorText,
        sender: 'bot',
        timestamp: new Date().toLocaleTimeString(),
        isError: true,
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chatbot-container">
      {/* Floating Button */}
      {!isOpen && (
        <button
          className="chatbot-bubble"
          onClick={() => setIsOpen(true)}
          aria-label="Open chat"
        >
          💬
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div className="chatbot-window">
          {/* Header */}
          <div className="chatbot-header">
            <h3>Chat Support</h3>
            <button
              className="chatbot-close"
              onClick={() => setIsOpen(false)}
              aria-label="Close chat"
            >
              ✕
            </button>
          </div>

          {/* Messages */}
          <div className="chatbot-messages">
            {messages.length === 0 && (
              <div className="chatbot-welcome">
                <p>👋 How can we help?</p>
              </div>
            )}
            {messages.map((msg) => (
              <div key={msg.id} className={`message message-${msg.sender}`}>
                <div className="message-bubble">{msg.text}</div>
                <span className="message-time">{msg.timestamp}</span>
              </div>
            ))}
            {isLoading && (
              <div className="message message-bot">
                <div className="typing-indicator">
                  <span></span><span></span><span></span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="chatbot-input-area">
            <input
              type="text"
              placeholder="Type a message..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={isLoading}
            />
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileSelect}
              style={{ display: 'none' }}
              accept=".pdf,.jpg,.jpeg,.png"
              aria-label="File attachment"
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={isLoading}
              className="chatbot-attach-btn"
              aria-label="Attach file"
              title="Upload file (PDF, JPG, PNG)"
            >
              📎
            </button>
            {selectedFile && (
              <button
                onClick={handleUploadFile}
                disabled={isLoading}
                className="chatbot-upload-btn"
                aria-label="Upload selected file"
                title={`Upload: ${selectedFile.name}`}
              >
                ↑
              </button>
            )}
            <button
              onClick={handleSendMessage}
              disabled={isLoading || !inputValue.trim()}
              aria-label="Send message"
            >
              Send
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Chatbot;
