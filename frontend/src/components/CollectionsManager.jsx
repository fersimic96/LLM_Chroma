import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';

function CollectionsManager() {
  const [collections, setCollections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastFetchTime, setLastFetchTime] = useState(0);

  // Usar useCallback para debounce
  const fetchCollections = useCallback(async () => {
    // Si ha pasado menos de 5 segundos desde la última petición, no hacer nada
    const now = Date.now();
    if (now - lastFetchTime < 5000 && collections.length > 0) {
      return;
    }
    setLastFetchTime(now);
    
    setLoading(true);
    try {
      const response = await fetch('/api/qdrant-collections');
      if (!response.ok) {
        throw new Error('Error al cargar las colecciones');
      }
      const data = await response.json();
      setCollections(data.collections);
      setError(null);
    } catch (err) {
      setError('Error al cargar las colecciones: ' + err.message);
      setCollections([]);
    } finally {
      setLoading(false);
    }
  }, [lastFetchTime, collections.length]);

  useEffect(() => {
    fetchCollections();
  }, [fetchCollections]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-medium">Gestión de Colecciones</h2>
        <div className="flex gap-2">
          <button 
            onClick={fetchCollections} 
            className="btn btn-outline btn-sm"
            disabled={loading}
          >
            {loading ? 'Cargando...' : 'Actualizar'}
          </button>
          <Link to="/" className="btn btn-outline btn-sm">
            Volver al inicio
          </Link>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center gap-2 text-content-secondary">
          <svg className="w-5 h-5 animate-spin" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span>Cargando colecciones...</span>
        </div>
      ) : error ? (
        <div className="p-3 bg-error/10 text-error rounded-lg">
          {error}
        </div>
      ) : collections.length === 0 ? (
        <div className="p-4 bg-background-secondary rounded-lg text-content-secondary">
          No hay colecciones disponibles
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {collections.map((collection) => (
            <div
              key={collection.name}
              className="p-4 border border-border rounded-lg bg-background hover:bg-background-secondary transition-colors"
            >
              <div className="flex justify-between items-start mb-3">
                <h3 className="text-lg font-medium">{collection.name}</h3>
                <div className="flex items-center gap-1">
                  {collection.status === 'active' ? (
                    <span className="text-green-500">●</span>
                  ) : (
                    <span className="text-red-500">●</span>
                  )}
                  <span className="text-xs text-content-secondary">
                    {collection.status === 'active' ? 'Activa' : 'Error'}
                  </span>
                </div>
              </div>

              <div className="text-sm text-content-secondary mb-4">
                <div className="flex items-center gap-2">
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                  </svg>
                  <span>{collection.vectors_count.toLocaleString()} vectores</span>
                </div>
              </div>

              <Link
                to={`/collections/${collection.name}`}
                className="btn btn-primary w-full"
              >
                Ver archivos
              </Link>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default CollectionsManager; 