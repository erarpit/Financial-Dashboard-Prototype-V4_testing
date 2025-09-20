import React, { useState, useEffect, useRef } from 'react';

interface Message {
  id: string;
  sender: 'user' | 'ai' | 'system';
  content: string;
  timestamp: string;
}

interface ContextInfo {
  current_price?: number;
  price_change_pct?: number;
  volume_analysis?: {
    strength: string;
    trend: string;
  };
}

const AIChat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      sender: 'ai',
      content: "Hi! I'm your AI stock assistant. Ask me about any stock analysis, buy/sell decisions, or market insights. Select a stock above and ask away!",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [currentTicker, setCurrentTicker] = useState('RELIANCE.NS');
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const tickerOptions = [
    { value: 'RELIANCE.NS', label: 'Reliance' },
    { value: 'TCS.NS', label: 'TCS' },
    { value: 'HDFCBANK.NS', label: 'HDFC Bank' },
    { value: 'INFY.NS', label: 'Infosys' },
    { value: 'SBIN.NS', label: 'SBI' }
  ];

  const quickQuestions = [
    { text: '📊 Buy/Sell Analysis', question: 'Should I buy {ticker} right now?' },
    { text: '⚠️ Risk Assessment', question: 'What are the risks of {ticker}?' },
    { text: '🎯 Price Target', question: 'Price target for {ticker}?' },
    { text: '📈 Volume Analysis', question: 'Volume analysis for {ticker}?' }
  ];

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const addMessage = (sender: 'user' | 'ai' | 'system', content: string) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      sender,
      content,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    setMessages(prev => [...prev, newMessage]);
  };

  const addContextInfo = (context: ContextInfo) => {
    if (!context.current_price) return;

    const priceChange = context.price_change_pct || 0;
    const changeClass = priceChange >= 0 ? 'text-green-600' : 'text-red-600';
    const changeSymbol = priceChange >= 0 ? '+' : '';

    const contextContent = `
      <div class="bg-blue-50 p-3 rounded-lg mb-2">
        <div class="font-semibold text-blue-900 mb-2">📊 Current Market Data</div>
        <div class="space-y-1">
          <div class="flex items-center space-x-2">
            <span class="font-bold text-lg">₹${context.current_price.toFixed(2)}</span>
            <span class="${changeClass}">
              ${changeSymbol}${priceChange.toFixed(2)}%
            </span>
          </div>
          ${context.volume_analysis ? `
            <div class="text-sm text-gray-600">
              <span>Volume: ${context.volume_analysis.strength}</span>
              <span class="ml-2">${context.volume_analysis.trend}</span>
            </div>
          ` : ''}
        </div>
      </div>
    `;

    addMessage('ai', contextContent);
  };

  const sendMessage = async () => {
    const message = inputMessage.trim();
    if (!message || isLoading) return;

    addMessage('user', message);
    setInputMessage('');

    await askQuestion(message);
  };

  const askQuestion = async (question: string) => {
    setIsLoading(true);

    try {
      const response = await fetch(`http://localhost:8000/ask?q=${encodeURIComponent(question)}&ticker=${currentTicker}`);
      const data = await response.json();

      if (data.error) {
        addMessage('ai', `Sorry, I encountered an error: ${data.answer || 'Please try again.'}`);
      } else {
        addMessage('ai', data.answer);

        // Show context if available
        if (data.context && data.context.current_price) {
          addContextInfo(data.context);
        }
      }
    } catch (error) {
      addMessage('ai', "Sorry, I'm having trouble connecting. Please check your internet connection and try again.");
      console.error('AI Chat error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickQuestion = (question: string) => {
    const formattedQuestion = question.replace('{ticker}', currentTicker);
    askQuestion(formattedQuestion);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleTickerChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newTicker = e.target.value;
    setCurrentTicker(newTicker);
    const tickerLabel = tickerOptions.find(opt => opt.value === newTicker)?.label || newTicker;
    addMessage('system', `Switched to analyzing ${tickerLabel}`);
  };

  return (
    <div className={`ai-chat-container bg-white rounded-lg shadow-lg border border-gray-200 ${isMinimized ? 'h-12' : 'h-96'} transition-all duration-300`}>
      {/* Header */}
      <div className="chat-header bg-gray-50 p-4 rounded-t-lg flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">🤖 AI Stock Assistant</h3>
        <div className="flex items-center space-x-2">
          <select
            value={currentTicker}
            onChange={handleTickerChange}
            className="ticker-select px-2 py-1 border border-gray-300 rounded text-sm"
          >
            {tickerOptions.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          <button
            onClick={() => setIsMinimized(!isMinimized)}
            className="minimize-btn text-gray-500 hover:text-gray-700 text-lg font-bold"
          >
            {isMinimized ? '+' : '−'}
          </button>
        </div>
      </div>

      {!isMinimized && (
        <>
          {/* Messages */}
          <div className="chat-messages p-4 h-64 overflow-y-auto space-y-3">
            {messages.map(message => (
              <div key={message.id} className={`message ${message.sender}-message`}>
                <div 
                  className={`message-content p-3 rounded-lg ${
                    message.sender === 'user' 
                      ? 'bg-blue-600 text-white ml-8' 
                      : message.sender === 'system'
                      ? 'bg-yellow-100 text-yellow-800 text-center text-sm'
                      : 'bg-gray-100 text-gray-900 mr-8'
                  }`}
                  dangerouslySetInnerHTML={{ __html: message.content }}
                />
                <div className="message-time text-xs text-gray-500 mt-1 text-right">
                  {message.timestamp}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex items-center justify-center space-x-2 text-gray-500">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                <span>AI is analyzing...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Quick Questions */}
          <div className="quick-questions p-4 bg-gray-50 border-t">
            <div className="grid grid-cols-2 gap-2">
              {quickQuestions.map((q, index) => (
                <button
                  key={index}
                  onClick={() => handleQuickQuestion(q.question)}
                  disabled={isLoading}
                  className="quick-question p-2 text-xs bg-white border border-gray-200 rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {q.text}
                </button>
              ))}
            </div>
          </div>

          {/* Input */}
          <div className="chat-input-container p-4 border-t">
            <div className="flex space-x-2">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask about stocks, market trends, analysis..."
                disabled={isLoading}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50"
              />
              <button
                onClick={sendMessage}
                disabled={isLoading || !inputMessage.trim()}
                className="send-btn px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Send
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default AIChat;
