import React from 'react';
import NewsCard from './NewsCard';
import { NewsItem } from '../types';

interface NewsPanelProps {
  news: NewsItem[];
}

const NewsPanel: React.FC<NewsPanelProps> = ({ news }) => {
  return (
    <div className="space-y-3 max-h-96 overflow-y-auto">
      {news.length === 0 ? (
        <p className="text-gray-500 text-sm">No news available</p>
      ) : (
        news.slice(0, 5).map((item, index) => (
          <NewsCard key={index} news={item} />
        ))
      )}
    </div>
  );
};

export default NewsPanel;
