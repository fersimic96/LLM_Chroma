import { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';

function CollectionFilesManager() {
  const { collectionName } = useParams();
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastFetchTime, setLastFetchTime] = useState(0);

  // Usar useCallback para implementar debounce
  const fetchCollectionFiles = useCallback(async () => {
    if (!collectionName) return;
    
    // Si ha pasado menos de 5 segundos desde la última petición, no hacer nada
    const now = Date.now();
    if (now - lastFetchTime < 5000 && files.length > 0) {
      return;
    }
    setLastFetchTime(now);
    
    setLoading(true);
    try {
      const response = await fetch(`/api/collection-files/${collectionName}`);
      if (!response.ok) {
        throw new Error('Error al cargar los archivos de la colección');
      }
      const data = await response.json();
      setFiles(data.files);
      setError(null);
    } catch (err) {
      setError('Error al cargar los archivos: ' + err.message);
      setFiles([]);
    } finally {
      setLoading(false);
    }
  }, [collectionName, lastFetchTime, files.length]);

  useEffect(() => {
    fetchCollectionFiles();
  }, [fetchCollectionFiles]);

  const handleDeleteFile = async (fileName) => {
    if (!confirm(`¿Estás seguro de eliminar el archivo "${fileName}" de la colección "${collectionName}"?`)) {
      return;
    }

    try {
      setLoading(true);
      const response = await fetch(`/api/collection-files/${collectionName}/${fileName}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Error al eliminar el archivo');
      }

      // Actualizar la lista de archivos
      setFiles(files.filter(file => file.name !== fileName));
      setError(null);
    } catch (err) {
      setError('Error al eliminar el archivo: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  if (!collectionName) {
    return (
      <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
        <h3 className="text-lg font-medium text-yellow-800 mb-2">Selecciona una colección</h3>
        <p className="text-yellow-700">
          Debes seleccionar una colección para ver sus archivos.
        </p>
        <Link to="/collections" className="mt-4 inline-block btn btn-primary">
          Ir a seleccionar colección
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-medium">
          Archivos en la colección: <span className="text-primary">{collectionName}</span>
        </h2>
        <div className="flex gap-2">
          <button 
            onClick={fetchCollectionFiles} 
            className="btn btn-outline btn-sm"
            disabled={loading}
          >
            {loading ? 'Cargando...' : 'Actualizar'}
          </button>
          <Link to="/collections" className="btn btn-outline btn-sm">
            Volver a colecciones
          </Link>
        </div>
      </div>

      {loading && (
        <div className="flex items-center gap-2 text-content-secondary">
          <svg className="w-5 h-5 animate-spin" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span>Cargando archivos...</span>
        </div>
      )}

      {error && (
        <div className="p-3 bg-error/10 text-error rounded-lg">
          {error}
        </div>
      )}

      {!loading && !error && files.length === 0 && (
        <div className="p-4 bg-background-secondary rounded-lg text-content-secondary">
          No hay archivos en esta colección
        </div>
      )}

      {files.length > 0 && (
        <div className="grid gap-3">
          {files.map((file) => (
            <div
              key={file.name}
              className="p-3 border border-border rounded-lg flex items-center justify-between bg-background"
            >
              <div className="flex gap-3 items-center">
                <div className="p-2 bg-primary/10 rounded-lg">
                  <svg className="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                  </svg>
                </div>
                
                <div>
                  <div className="font-medium">{file.name}</div>
                  <div className="text-xs text-content-secondary flex items-center gap-3">
                    <span>{file.chunks} chunks</span>
                    <span>{file.vectors} vectores</span>
                    <span>Página {file.pages}</span>
                  </div>
                </div>
              </div>

              <button
                onClick={() => handleDeleteFile(file.name)}
                className="btn btn-error btn-sm"
                disabled={loading}
              >
                Eliminar
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default CollectionFilesManager; 