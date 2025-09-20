import React, { useState, useEffect } from 'react';
import DomainCard from './DomainCard';
import LoadingSpinner from './LoadingSpinner';
import ErrorMessage from './ErrorMessage';

interface TopCompany {
  symbol: string;
  name: string;
  rating?: string;
  market_weight?: number;
}

interface DomainOverview {
  companies_count?: number;
  market_cap?: number;
  description?: string;
  industries_count?: number;
  market_weight?: number;
  employee_count?: number;
}

interface DomainData {
  key: string;
  name: string;
  symbol: string;
  overview: DomainOverview;
  top_companies: TopCompany[];
  research_reports: Array<{
    title: string;
    url: string;
    date: string;
  }>;
  last_updated: string;
}

interface DomainPanelProps {
  type: 'sectors' | 'industries';
}

const DomainPanel: React.FC<DomainPanelProps> = ({ type }) => {
  const [domains, setDomains] = useState<DomainData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredDomains, setFilteredDomains] = useState<DomainData[]>([]);

  useEffect(() => {
    fetchDomains();
  }, [type]);

  useEffect(() => {
    if (searchQuery.trim() === '') {
      setFilteredDomains(domains);
    } else {
      const filtered = domains.filter(domain =>
        domain.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        domain.key.toLowerCase().includes(searchQuery.toLowerCase()) ||
        domain.symbol.toLowerCase().includes(searchQuery.toLowerCase())
      );
      setFilteredDomains(filtered);
    }
  }, [searchQuery, domains]);

  const fetchDomains = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`http://localhost:8000/${type}`);
      if (!response.ok) {
        throw new Error(`Failed to fetch ${type}`);
      }
      
      const data = await response.json();
      setDomains(data);
      setFilteredDomains(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
  };

  const handleRefresh = () => {
    fetchDomains();
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <ErrorMessage message={error} />
        <button
          onClick={handleRefresh}
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 capitalize">
            {type} Analysis
          </h2>
          <p className="text-gray-600">
            Explore financial {type} and their top companies
          </p>
        </div>
        <button
          onClick={handleRefresh}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Refresh
        </button>
      </div>

      {/* Search */}
      <div className="mb-6">
        <div className="relative">
          <input
            type="text"
            placeholder={`Search ${type}...`}
            value={searchQuery}
            onChange={handleSearch}
            className="w-full px-4 py-2 pl-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>
      </div>

      {/* Results Count */}
      <div className="mb-4">
        <p className="text-sm text-gray-600">
          Showing {filteredDomains.length} of {domains.length} {type}
        </p>
      </div>

      {/* Domain Cards */}
      {filteredDomains.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-gray-400 mb-4">
            <svg className="mx-auto h-12 w-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No {type} found</h3>
          <p className="text-gray-500">
            {searchQuery ? 'Try adjusting your search terms' : `No ${type} data available`}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredDomains.map((domain) => (
            <DomainCard
              key={domain.key}
              {...domain}
              type={type === 'sectors' ? 'sector' : 'industry'}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default DomainPanel;
