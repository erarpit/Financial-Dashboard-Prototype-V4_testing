import React from 'react';
import { NewsItem } from '../types';

interface NewsCardProps {
  news: NewsItem;
}

const NewsCard: React.FC<NewsCardProps> = ({ news }) => {
  const getSentimentColor = (sentiment: string) => {
    switch (sentiment.toUpperCase()) {
      case 'POSITIVE':
        return {
          bg: 'bg-green-50',
          text: 'text-green-700',
          border: 'border-green-200',
          icon: '📈'
        };
      case 'NEGATIVE':
        return {
          bg: 'bg-red-50',
          text: 'text-red-700',
          border: 'border-red-200',
          icon: '📉'
        };
      case 'NEUTRAL':
        return {
          bg: 'bg-gray-50',
          text: 'text-gray-700',
          border: 'border-gray-200',
          icon: '📊'
        };
      default:
        return {
          bg: 'bg-gray-50',
          text: 'text-gray-700',
          border: 'border-gray-200',
          icon: '📰'
        };
    }
  };

  const sentimentStyle = getSentimentColor(news.sentiment);

  const getConfidenceWidth = (confidence: number) => {
    return Math.round(confidence * 100);
  };

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return dateString;
    }
  };

  return (
    <div className={`rounded-lg border ${sentimentStyle.border} ${sentimentStyle.bg} p-4 mb-3 hover:shadow-md transition-shadow cursor-pointer`}>
      {/* Header */}
      <div className="flex justify-between items-start mb-2">
        <div className="flex-1">
          <h4 className="text-sm font-semibold text-gray-900 line-clamp-2 mb-1 hover:text-blue-700 transition-colors">
            {news.title}
          </h4>
          <div className="flex items-center space-x-2 text-xs text-gray-500">
            <span className="font-medium">{news.source}</span>
            <span>•</span>
            <span>{formatDate(news.published_at)}</span>
          </div>
        </div>
        <div className={`ml-3 px-2 py-1 rounded text-xs font-medium ${sentimentStyle.bg} ${sentimentStyle.text} border ${sentimentStyle.border}`}>
          <span className="mr-1">{sentimentStyle.icon}</span>
          {news.sentiment}
        </div>
      </div>

      {/* Content Preview */}
      {news.content && (
        <p className="text-sm text-gray-700 line-clamp-3 mb-3 leading-relaxed">
          {news.content.length > 150 
            ? news.content.substring(0, 150) + '...' 
            : news.content
          }
        </p>
      )}

      {/* Sentiment Confidence Bar */}
      <div className="flex justify-between items-center mb-3">
        <span className="text-xs text-gray-500 font-medium">AI Confidence</span>
        <div className="flex items-center space-x-2">
          <div className="w-20 bg-gray-200 rounded-full h-2 shadow-inner">
            <div
              className={`h-2 rounded-full transition-all duration-700 shadow-sm ${
                news.sentiment.toUpperCase() === 'POSITIVE' ? 'bg-gradient-to-r from-green-400 to-green-500' :
                news.sentiment.toUpperCase() === 'NEGATIVE' ? 'bg-gradient-to-r from-red-400 to-red-500' :
                'bg-gradient-to-r from-gray-400 to-gray-500'
              }`}
              style={{ width: `${getConfidenceWidth(news.confidence)}%` }}
            ></div>
          </div>
          <span className="text-xs font-bold text-gray-700">
            {Math.round(news.confidence * 100)}%
          </span>
        </div>
      </div>

      {/* Read More Link */}
      {news.url && (
        <div className="pt-2 border-t border-gray-200">
          <a
            href={news.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs text-blue-600 hover:text-blue-800 hover:underline transition-colors font-medium"
          >
            Read full article →
          </a>
        </div>
      )}
    </div>
  );
};

export default NewsCard;