import React, { useState, useEffect } from 'react';
import LoadingSpinner from './LoadingSpinner';
import ErrorMessage from './ErrorMessage';

interface QueryField {
  [category: string]: string[];
}

interface QueryValues {
  [field: string]: string[];
}

interface QueryResult {
  symbol: string;
  name: string;
  sector: string;
  industry: string;
  marketCap: number;
  trailingPE: number;
  regularMarketPrice: number;
  regularMarketChange: number;
  regularMarketChangePercent: number;
  regularMarketVolume: number;
  fiftyTwoWeekHigh: number;
  fiftyTwoWeekLow: number;
}

interface QueryBuilderProps {
  onResults?: (results: QueryResult[]) => void;
}

const QueryBuilder: React.FC<QueryBuilderProps> = ({ onResults }) => {
  const [queryType, setQueryType] = useState<'equity' | 'fund'>('equity');
  const [fields, setFields] = useState<QueryField>({});
  const [values, setValues] = useState<QueryValues>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<QueryResult[]>([]);
  const [query, setQuery] = useState<any>({
    operator: 'AND',
    operands: []
  });

  useEffect(() => {
    fetchFieldsAndValues();
  }, [queryType]);

  const fetchFieldsAndValues = async () => {
    try {
      setLoading(true);
      setError(null);

      const [fieldsResponse, valuesResponse] = await Promise.all([
        fetch(`http://localhost:8000/query-builder/fields?query_type=${queryType}`),
        fetch(`http://localhost:8000/query-builder/values?query_type=${queryType}`)
      ]);

      if (!fieldsResponse.ok || !valuesResponse.ok) {
        throw new Error('Failed to fetch query data');
      }

      const fieldsData = await fieldsResponse.json();
      const valuesData = await valuesResponse.json();

      setFields(fieldsData.fields);
      setValues(valuesData.values);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const addCondition = () => {
    const newCondition = {
      operator: 'GT',
      operands: ['marketCap', 0]
    };
    
    setQuery(prev => ({
      ...prev,
      operands: [...prev.operands, newCondition]
    }));
  };

  const updateCondition = (index: number, field: string, value: any) => {
    setQuery(prev => ({
      ...prev,
      operands: prev.operands.map((operand: any, i: number) => 
        i === index ? { ...operand, operands: [field, value] } : operand
      )
    }));
  };

  const removeCondition = (index: number) => {
    setQuery(prev => ({
      ...prev,
      operands: prev.operands.filter((_: any, i: number) => i !== index)
    }));
  };

  const executeQuery = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`http://localhost:8000/query-builder/execute/${queryType}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query })
      });

      if (!response.ok) {
        throw new Error('Failed to execute query');
      }

      const data = await response.json();
      setResults(data.results);
      onResults?.(data.results);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const formatNumber = (value: number) => {
    if (value >= 1e12) return `$${(value / 1e12).toFixed(2)}T`;
    if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`;
    if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`;
    if (value >= 1e3) return `$${(value / 1e3).toFixed(2)}K`;
    return `$${value.toFixed(2)}`;
  };

  const formatPercentage = (value: number) => {
    return `${value.toFixed(2)}%`;
  };

  if (loading && Object.keys(fields).length === 0) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Stock Screener</h2>
        <div className="flex items-center space-x-4">
          <select
            value={queryType}
            onChange={(e) => setQueryType(e.target.value as 'equity' | 'fund')}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="equity">Stocks</option>
            <option value="fund">Funds</option>
          </select>
          <button
            onClick={executeQuery}
            disabled={loading || query.operands.length === 0}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
      </div>

      {/* Query Builder */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Build Your Query</h3>
        
        <div className="space-y-4">
          {query.operands.map((condition: any, index: number) => (
            <div key={index} className="flex items-center space-x-4 p-4 border border-gray-200 rounded-lg">
              <select
                value={condition.operator}
                onChange={(e) => updateCondition(index, condition.operands[0], e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg"
              >
                <option value="GT">Greater Than</option>
                <option value="LT">Less Than</option>
                <option value="GTE">Greater or Equal</option>
                <option value="LTE">Less or Equal</option>
                <option value="EQ">Equals</option>
                <option value="BTWN">Between</option>
              </select>

              <select
                value={condition.operands[0] || ''}
                onChange={(e) => updateCondition(index, e.target.value, condition.operands[1])}
                className="px-3 py-2 border border-gray-300 rounded-lg flex-1"
              >
                <option value="">Select Field</option>
                {Object.entries(fields).map(([category, fieldList]) => (
                  <optgroup key={category} label={category}>
                    {fieldList.map(field => (
                      <option key={field} value={field}>{field}</option>
                    ))}
                  </optgroup>
                ))}
              </select>

              {condition.operator === 'BTWN' ? (
                <div className="flex items-center space-x-2">
                  <input
                    type="number"
                    value={condition.operands[1] || ''}
                    onChange={(e) => updateCondition(index, condition.operands[0], [e.target.value, condition.operands[2]])}
                    placeholder="Min"
                    className="px-3 py-2 border border-gray-300 rounded-lg w-24"
                  />
                  <span>to</span>
                  <input
                    type="number"
                    value={condition.operands[2] || ''}
                    onChange={(e) => updateCondition(index, condition.operands[0], [condition.operands[1], e.target.value])}
                    placeholder="Max"
                    className="px-3 py-2 border border-gray-300 rounded-lg w-24"
                  />
                </div>
              ) : (
                <input
                  type={values[condition.operands[0]] ? 'text' : 'number'}
                  value={condition.operands[1] || ''}
                  onChange={(e) => updateCondition(index, condition.operands[0], e.target.value)}
                  placeholder="Value"
                  className="px-3 py-2 border border-gray-300 rounded-lg w-32"
                />
              )}

              <button
                onClick={() => removeCondition(index)}
                className="px-3 py-2 text-red-600 hover:text-red-800"
              >
                Remove
              </button>
            </div>
          ))}

          <button
            onClick={addCondition}
            className="w-full px-4 py-2 border-2 border-dashed border-gray-300 rounded-lg text-gray-600 hover:border-gray-400 hover:text-gray-700"
          >
            + Add Condition
          </button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <ErrorMessage message={error} />
      )}

      {/* Results */}
      {results.length > 0 && (
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">
              Search Results ({results.length} found)
            </h3>
          </div>
          
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Symbol</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Sector</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Price</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Change</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">P/E</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Market Cap</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {results.map((result, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {result.symbol}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {result.name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {result.sector}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatNumber(result.regularMarketPrice)}
                    </td>
                    <td className={`px-6 py-4 whitespace-nowrap text-sm ${
                      result.regularMarketChange >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {formatPercentage(result.regularMarketChangePercent)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {result.trailingPE ? result.trailingPE.toFixed(2) : 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatNumber(result.marketCap)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default QueryBuilder;
