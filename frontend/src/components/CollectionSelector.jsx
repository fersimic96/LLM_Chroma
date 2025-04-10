import { useState, useEffect } from 'react';

function CollectionSelector({ onSelect, disabled }) {
  const [collections, setCollections] = useState([]);
  const [selectedCollections, setSelectedCollections] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchCollections();
  }, []);

  const fetchCollections = async () => {
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
  };

  const handleCollectionToggle = (collectionName) => {
    const newSelected = selectedCollections.includes(collectionName)
      ? selectedCollections.filter(name => name !== collectionName)
      : [...selectedCollections, collectionName];
    
    setSelectedCollections(newSelected);
    onSelect(newSelected);
  };

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-content-primary">
        Colecciones para búsqueda
      </label>

      {loading ? (
        <div className="flex items-center gap-2 text-sm text-content-secondary">
          <svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span>Cargando colecciones...</span>
        </div>
      ) : error ? (
        <div className="text-sm text-error bg-error/10 p-2 rounded">
          {error}
        </div>
      ) : collections.length === 0 ? (
        <div className="text-sm text-content-secondary">
          No hay colecciones disponibles
        </div>
      ) : (
        <div className="space-y-2">
          {collections.map((collection) => (
            <label
              key={collection.name}
              className={`flex items-center gap-2 p-2 rounded border ${
                selectedCollections.includes(collection.name)
                  ? 'border-primary bg-primary/5'
                  : 'border-border bg-background'
              } cursor-pointer hover:bg-background-secondary transition-colors`}
            >
              <input
                type="checkbox"
                checked={selectedCollections.includes(collection.name)}
                onChange={() => handleCollectionToggle(collection.name)}
                disabled={disabled}
                className="checkbox"
              />
              <div className="flex-1">
                <div className="font-medium">{collection.name}</div>
                <div className="text-xs text-content-secondary flex items-center gap-2">
                  <span>{collection.vectors_count.toLocaleString()} vectores</span>
                  {collection.status === 'active' ? (
                    <span className="text-green-500">●</span>
                  ) : (
                    <span className="text-red-500">●</span>
                  )}
                </div>
              </div>
            </label>
          ))}
        </div>
      )}

      {selectedCollections.length > 0 && (
        <div className="text-xs text-content-secondary mt-1">
          {selectedCollections.length} {selectedCollections.length === 1 ? 'colección seleccionada' : 'colecciones seleccionadas'}
        </div>
      )}
    </div>
  );
}

export default CollectionSelector; 