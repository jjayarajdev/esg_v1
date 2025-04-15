import { useState, useEffect } from 'react';
import { Chart } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
} from 'chart.js';

ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
);

interface ESGMetric {
  id: string;
  category: string;
  goal: string;
  actual: string;
  rag_status: string;
  extracted_by: string;
}

interface ESGDashboardProps {
  documentId: string;
}

export default function ESGDashboard({ documentId }: ESGDashboardProps) {
  const [metrics, setMetrics] = useState<ESGMetric[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [view, setView] = useState<'table' | 'chart'>('table');

  useEffect(() => {
    fetchMetrics();
  }, [documentId]);

  const fetchMetrics = async () => {
    try {
      const response = await fetch(`http://localhost:8000/metrics/${documentId}`);
      if (!response.ok) throw new Error('Failed to fetch metrics');
      const data = await response.json();
      setMetrics(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch metrics');
    } finally {
      setLoading(false);
    }
  };

  const handleExtractMetrics = async () => {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/metrics/extract/${documentId}`, {
        method: 'POST',
      });
      if (!response.ok) throw new Error('Failed to extract metrics');
      await fetchMetrics();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to extract metrics');
    } finally {
      setLoading(false);
    }
  };

  const getRAGColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'red': return 'bg-red-100 text-red-800';
      case 'amber': return 'bg-yellow-100 text-yellow-800';
      case 'green': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const chartData = {
    labels: metrics.map(m => m.category),
    datasets: [{
      label: 'ESG Performance',
      data: metrics.map(m => {
        const goal = parseFloat(m.goal.replace(/[^0-9.]/g, ''));
        const actual = parseFloat(m.actual.replace(/[^0-9.]/g, ''));
        return (actual / goal) * 100;
      }),
      backgroundColor: 'rgba(99, 102, 241, 0.2)',
      borderColor: 'rgb(99, 102, 241)',
      borderWidth: 1,
    }]
  };

  const chartOptions = {
    scales: {
      r: {
        angleLines: {
          display: true
        },
        suggestedMin: 0,
        suggestedMax: 100
      }
    }
  };

  if (loading) {
    return <div className="text-center py-8">Loading metrics...</div>;
  }

  if (error) {
    return <div className="text-center py-8 text-red-500">{error}</div>;
  }

  return (
    <div className="w-full max-w-6xl mx-auto p-4 space-y-6">
      <div className="flex justify-between items-center">
        <div className="space-x-2">
          <button
            onClick={() => setView('table')}
            className={`px-4 py-2 rounded ${
              view === 'table'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Table View
          </button>
          <button
            onClick={() => setView('chart')}
            className={`px-4 py-2 rounded ${
              view === 'chart'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Chart View
          </button>
        </div>
        <button
          onClick={handleExtractMetrics}
          className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
        >
          Extract Metrics
        </button>
      </div>

      {view === 'table' ? (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Category
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Target/Goal
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actual
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {metrics.map((metric) => (
                <tr key={metric.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {metric.category}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {metric.goal}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {metric.actual}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <span className={`px-2 py-1 rounded-full ${getRAGColor(metric.rag_status)}`}>
                      {metric.rag_status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="h-[600px]">
          <Chart type="radar" data={chartData} options={chartOptions} />
        </div>
      )}
    </div>
  );
} 