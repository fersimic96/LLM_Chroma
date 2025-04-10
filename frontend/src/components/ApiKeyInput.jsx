import { useState, useEffect } from 'react';

const ApiKeyInput = ({ onApiKeySet }) => {
  const [apiKey, setApiKey] = useState('');
  const [isConfigured, setIsConfigured] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState('');
  const [organizationInfo, setOrganizationInfo] = useState(null);

  useEffect(() => {
    // Al iniciar, intentamos validar con el backend
    validateWithBackend();
  }, []);

  const validateWithBackend = async (key = null) => {
    try {
      // Si no se proporciona una key, intentamos obtenerla del localStorage
      const keyToValidate = key || localStorage.getItem('openai_api_key');
      
      if (!keyToValidate) {
        handleReset();
        return;
      }

      const response = await fetch('http://localhost:8000/validate_api_key', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ api_key: keyToValidate }),
      });

      const data = await response.json();
      
      if (response.ok) {
        setOrganizationInfo(data.details);
        localStorage.setItem('openai_org_info', JSON.stringify(data.details));
        setIsConfigured(true);
        onApiKeySet(true);
        if (key) {
          localStorage.setItem('openai_api_key', key);
          setApiKey('');
        }
      } else {
        handleReset();
        if (key) {
          throw new Error(data.detail?.message || 'API key inválida');
        }
      }
    } catch (error) {
      console.error('Error validando API key:', error);
      if (key) {
        setError('Error al validar la API key: ' + error.message);
      } else {
        handleReset();
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!apiKey.trim()) {
      setError('Por favor ingresa una API key');
      return;
    }

    setIsSaving(true);
    setError('');

    try {
      await validateWithBackend(apiKey);
    } finally {
      setIsSaving(false);
    }
  };

  const handleReset = () => {
    localStorage.removeItem('openai_api_key');
    localStorage.removeItem('openai_org_info');
    setApiKey('');
    setIsConfigured(false);
    setOrganizationInfo(null);
    onApiKeySet(false);
  };

  if (isConfigured) {
    return (
      <div className="p-4 bg-success/10 rounded-lg space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-success flex items-center gap-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            API Key configurada correctamente
          </span>
          <button
            onClick={handleReset}
            className="text-sm px-3 py-1 bg-surface hover:bg-surface/80 rounded-md"
          >
            Cambiar
          </button>
        </div>
        
        {organizationInfo && (
          <div className="text-sm text-content-secondary space-y-1">
            <p>Organización: {organizationInfo.organization || 'Personal'}</p>
            <p>Modelo: {organizationInfo.model}</p>
          </div>
        )}
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 p-4 bg-surface rounded-lg border border-border">
      <div className="space-y-2">
        <label htmlFor="apiKey" className="block text-sm font-medium">
          OpenAI API Key
        </label>
        <div className="relative">
          <input
            id="apiKey"
            type="password"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="sk-..."
            className="w-full p-2 pr-10 rounded border border-border bg-background focus:outline-none focus:ring-2 focus:ring-primary"
          />
          <div className="absolute inset-y-0 right-0 flex items-center pr-3">
            <svg className="w-5 h-5 text-content-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
            </svg>
          </div>
        </div>
      </div>
      
      {error && (
        <div className="text-sm text-error bg-error/10 p-2 rounded">
          {error}
        </div>
      )}

      <button
        type="submit"
        disabled={isSaving}
        className="w-full py-2 px-4 bg-primary text-white rounded hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
      >
        {isSaving ? (
          <>
            <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            <span>Validando...</span>
          </>
        ) : (
          <>
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
            <span>Configurar API Key</span>
          </>
        )}
      </button>
    </form>
  );
};

export default ApiKeyInput;
