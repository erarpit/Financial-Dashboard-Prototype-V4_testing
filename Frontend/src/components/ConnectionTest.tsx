import React, { useEffect, useState } from 'react';
import { healthCheck } from '../api';

const ConnectionTest: React.FC = () => {
  const [status, setStatus] = useState<string>('checking...');
  const [error, setError] = useState<string>('');

  useEffect(() => {
    const checkConnection = async () => {
      try {
        const result = await healthCheck();
        setStatus(result.status || 'connected');
        setError('');
      } catch (err) {
        setStatus('disconnected');
        setError(err instanceof Error ? err.message : 'Unknown error');
      }
    };

    checkConnection();
  }, []);

  return (
    <div className="p-4 bg-white shadow rounded-lg">
      <h2 className="text-lg font-semibold mb-2">Backend Connection Test</h2>
      <div className={`p-2 rounded ${
        status === 'connected' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
      }`}>
        Status: {status}
      </div>
      {error && (
        <div className="mt-2 p-2 bg-yellow-100 text-yellow-800 rounded">
          Error: {error}
        </div>
      )}
    </div>
  );
};

export default ConnectionTest;
