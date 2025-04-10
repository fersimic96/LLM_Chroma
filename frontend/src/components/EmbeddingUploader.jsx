import { useState, useEffect } from 'react';

function EmbeddingUploader() {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [collections, setCollections] = useState([]);
  const [selectedCollection, setSelectedCollection] = useState('');
  const [showNewCollectionForm, setShowNewCollectionForm] = useState(false);
  const [newCollectionName, setNewCollectionName] = useState('');
  const [isCreatingCollection, setIsCreatingCollection] = useState(false);

  // Cargar colecciones al montar el componente
  useEffect(() => {
    fetchCollections();
  }, []);

  const fetchCollections = async () => {
    try {
      const response = await fetch('/api/qdrant-collections');
      if (!response.ok) {
        throw new Error('Error al cargar las colecciones');
      }
      const data = await response.json();
      setCollections(data.collections);
    } catch (err) {
      setError('Error al cargar las colecciones: ' + err.message);
    }
  };

  const handleCreateCollection = async (e) => {
    e.preventDefault();
    setIsCreatingCollection(true);
    setError(null);

    try {
      const response = await fetch('/api/qdrant-collections', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          collection_name: newCollectionName
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al crear la colección');
      }

      await fetchCollections();
      setShowNewCollectionForm(false);
      setNewCollectionName('');
      setSelectedCollection(newCollectionName);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsCreatingCollection(false);
    }
  };

  const handleFileChange = (event) => {
    const files = Array.from(event.target.files).filter(file => file.type === 'application/pdf');
    if (files.length === 0) {
      setError('Solo se permiten archivos PDF');
      return;
    }
    setSelectedFiles(files);
    setError(null);
    setSuccess(false);
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) {
      setError('Por favor selecciona al menos un archivo PDF');
      return;
    }

    if (!selectedCollection) {
      setError('Por favor selecciona una colección');
      return;
    }

    setUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      selectedFiles.forEach((file) => {
        formData.append('files', file);
      });
      formData.append('collection_name', selectedCollection);

      const response = await fetch('/api/upload-embeddings', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al procesar los archivos');
      }

      const data = await response.json();
      setSuccess(true);
      setSelectedFiles([]);
      console.log('Archivos procesados:', data);
      
      // Actualizar la lista de colecciones para mostrar el nuevo conteo
      await fetchCollections();
    } catch (err) {
      setError(`Error al procesar los archivos: ${err.message}`);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="p-4 border border-border rounded-lg bg-background">
      <h3 className="text-lg font-medium mb-4">Cargar Embeddings</h3>
      
      <div className="space-y-4">
        {/* Selector de colección */}
        <div className="space-y-2">
          <label className="block text-sm font-medium">Colección</label>
          <div className="flex gap-2">
            <select
              value={selectedCollection}
              onChange={(e) => setSelectedCollection(e.target.value)}
              className="select select-bordered flex-1"
              disabled={uploading}
            >
              <option value="">Seleccionar colección</option>
              {collections.map((col) => (
                <option key={col.name} value={col.name}>
                  {col.name} ({col.vectors_count || 0} vectores)
                </option>
              ))}
            </select>
            <button
              onClick={() => setShowNewCollectionForm(true)}
              className="btn btn-secondary"
              disabled={uploading}
            >
              Nueva
            </button>
          </div>
        </div>

        {/* Formulario para nueva colección */}
        {showNewCollectionForm && (
          <div className="p-4 border border-border rounded-lg">
            <h4 className="text-sm font-medium mb-3">Nueva Colección</h4>
            <form onSubmit={handleCreateCollection} className="space-y-3">
              <div>
                <label className="block text-sm mb-1">Nombre de la colección</label>
                <input
                  type="text"
                  value={newCollectionName}
                  onChange={(e) => setNewCollectionName(e.target.value)}
                  className="input input-bordered w-full"
                  placeholder="Ingresa el nombre de la colección"
                  required
                  disabled={isCreatingCollection}
                />
              </div>
              <div className="flex gap-2">
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={isCreatingCollection || !newCollectionName}
                >
                  {isCreatingCollection ? 'Creando...' : 'Crear'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowNewCollectionForm(false)}
                  className="btn btn-ghost"
                  disabled={isCreatingCollection}
                >
                  Cancelar
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Selector de archivos */}
        <div className="space-y-2">
          <label className="block text-sm font-medium">Archivos PDF</label>
          <input
            type="file"
            onChange={handleFileChange}
            accept=".pdf"
            multiple
            className="file-input file-input-bordered w-full"
            disabled={uploading || !selectedCollection}
          />
        </div>

        {/* Mensajes de estado */}
        {error && (
          <div className="alert alert-error">
            {error}
          </div>
        )}
        
        {success && (
          <div className="alert alert-success">
            Archivos procesados exitosamente
          </div>
        )}

        {/* Botón de carga */}
        <button
          onClick={handleUpload}
          disabled={uploading || selectedFiles.length === 0 || !selectedCollection}
          className="btn btn-primary w-full"
        >
          {uploading ? (
            <>
              <span className="loading loading-spinner"></span>
              Procesando...
            </>
          ) : (
            'Procesar archivos'
          )}
        </button>
      </div>
    </div>
  );
}

export default EmbeddingUploader; 