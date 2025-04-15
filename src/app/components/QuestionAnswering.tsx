import { useState, useEffect } from 'react';

interface Citation {
  text: string;
  chunk_index: number;
}

interface QAInteraction {
  id: string;
  question: string;
  answer: string;
  citations: Citation[];
  validated: boolean | null;
  created_at: string;
}

interface QuestionAnsweringProps {
  documentId: string;
}

export default function QuestionAnswering({ documentId }: QuestionAnsweringProps) {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<QAInteraction[]>([]);

  useEffect(() => {
    fetchHistory();
  }, [documentId]);

  const fetchHistory = async () => {
    try {
      const response = await fetch(`http://localhost:8000/qa/history/${documentId}`);
      if (!response.ok) throw new Error('Failed to fetch history');
      const data = await response.json();
      setHistory(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch history');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/qa/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          document_id: documentId,
          question: question.trim(),
        }),
      });

      if (!response.ok) throw new Error('Failed to get answer');
      
      const data = await response.json();
      
      // Ensure citations is an array
      const processedData = {
        ...data,
        id: data.interaction_id || data.id || `temp-${Date.now()}`,
        citations: Array.isArray(data.citations) ? data.citations : []
      };
      
      setHistory(prev => [...prev, processedData]);
      setQuestion('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get answer');
    } finally {
      setLoading(false);
    }
  };

  const handleValidate = async (interactionId: string, isValid: boolean) => {
    try {
      await fetch('http://localhost:8000/qa/validate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          interaction_id: interactionId,
          is_valid: isValid,
        }),
      });

      setHistory(prev =>
        prev.map(interaction =>
          interaction.id === interactionId
            ? { ...interaction, validated: isValid }
            : interaction
        )
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to validate answer');
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto p-4 space-y-6">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question about the document..."
            className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !question.trim()}
            className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
          >
            {loading ? 'Asking...' : 'Ask'}
          </button>
        </div>
        {error && (
          <p className="text-red-500">{error}</p>
        )}
      </form>

      <div className="space-y-6">
        {history.map((interaction) => (
          <div key={interaction.id} className="border rounded-lg p-4 space-y-4">
            <div className="font-medium text-gray-600">
              Q: {interaction.question}
            </div>
            <div className="text-gray-800">
              A: {interaction.answer}
            </div>
            {interaction.citations && Array.isArray(interaction.citations) && interaction.citations.length > 0 && (
              <div className="space-y-2">
                <h4 className="font-medium text-gray-600">Sources:</h4>
                {interaction.citations.map((citation, index) => (
                  <div key={`${interaction.id}-citation-${index}`} className="text-sm text-gray-600 bg-gray-50 p-2 rounded">
                    {citation?.text || `Citation ${index + 1}`}
                  </div>
                ))}
              </div>
            )}
            <div className="flex gap-2">
              <button
                onClick={() => handleValidate(interaction.id, true)}
                className={`px-3 py-1 rounded ${
                  interaction.validated === true
                    ? 'bg-green-500 text-white'
                    : 'border border-green-500 text-green-500 hover:bg-green-50'
                }`}
              >
                ✓ Correct
              </button>
              <button
                onClick={() => handleValidate(interaction.id, false)}
                className={`px-3 py-1 rounded ${
                  interaction.validated === false
                    ? 'bg-red-500 text-white'
                    : 'border border-red-500 text-red-500 hover:bg-red-50'
                }`}
              >
                ✗ Incorrect
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
} 