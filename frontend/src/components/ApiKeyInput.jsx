import { useState, useEffect } from 'react';

function ApiKeyInput({ onApiKeySet }) {
  const [apiKey, setApiKey] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState(null);
  const [isConfigured, setIsConfigured] = useState(false);
  
  // Verificar si hay una API key guardada al cargar el componente
  useEffect(() => {
    const savedKey = localStorage.getItem('openai_api_key');
    if (savedKey) {
      setApiKey(savedKey);
      setIsConfigured(true);
      checkApiKeyStatus();
    }
  }, []);

  // Verificar el estado de la API key en el servidor
  const checkApiKeyStatus = async () => {
    try {
      const response = await fetch('/api_key_status');
      if (response.ok) {
        const data = await response.json();
        setIsConfigured(data.is_configured);
        onApiKeySet(data.is_configured);
      }
    } catch (err) {
      console.error('Error al verificar estado de API key:', err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!apiKey.trim()) {
      setError('Por favor ingresa una API key válida');
      return;
    }
    
    setIsSaving(true);
    setError(null);
    
    try {
      const response = await fetch('/validate_api_key', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ api_key: apiKey }),
      });
      
      const data = await response.json();
      
      if (data.success) {
        // Guardar la API key en localStorage
        localStorage.setItem('openai_api_key', apiKey);
        setIsConfigured(true);
        onApiKeySet(true);
      } else {
        setError(data.message || 'API key inválida. Por favor verifica e intenta nuevamente.');
        localStorage.removeItem('openai_api_key');
        setIsConfigured(false);
        onApiKeySet(false);
      }
    } catch (err) {
      setError(`Error al validar la API key: ${err.message}`);
      setIsConfigured(false);
      onApiKeySet(false);
    } finally {
      setIsSaving(false);
    }
  };

  const handleReset = () => {
    localStorage.removeItem('openai_api_key');
    setApiKey('');
    setIsConfigured(false);
    setError(null);
    onApiKeySet(false);
  };

  return (
    <div className="p-4 rounded-lg border border-border bg-background">
      <h3 className="text-lg font-medium mb-4">Configuración de API Key</h3>
      
      {isConfigured ? (
        <div className="space-y-4">
          <div className="flex items-center gap-2 text-green-600">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            <span>API Key configurada correctamente</span>
          </div>
          
          <button
            onClick={handleReset}
            className="btn btn-outline btn-sm"
          >
            Cambiar API Key
          </button>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="apiKey" className="block text-sm mb-1">
              OpenAI API Key
            </label>
            <input
              type="password"
              id="apiKey"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              className="input w-full"
              placeholder="sk-..."
              required
            />
            <p className="text-xs text-content-secondary mt-1">
              Necesitas una API key de OpenAI para usar el chatbot.
            </p>
          </div>
          
          {error && (
            <div className="p-3 bg-error/10 text-error rounded-lg text-sm">
              {error}
            </div>
          )}
          
          <button
            type="submit"
            className="btn btn-primary"
            disabled={isSaving}
          >
            {isSaving ? (
              <>
                <svg className="w-4 h-4 animate-spin mr-2" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>Validando...</span>
              </>
            ) : (
              'Guardar API Key'
            )}
          </button>
        </form>
      )}
    </div>
  );
}

export default ApiKeyInput;
