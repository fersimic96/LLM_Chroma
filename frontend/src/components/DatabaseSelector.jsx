import { useState, useEffect } from 'react'

function DatabaseSelector({ onSelect, disabled, basePath }) {
  const [databases, setDatabases] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [selectedDb, setSelectedDb] = useState('')
  const [currentPath, setCurrentPath] = useState('')

  useEffect(() => {
    if (basePath) {
      // Primero actualizamos el path en el backend
      updateBackendPath(basePath)
    }
  }, [basePath])

  const updateBackendPath = async (path) => {
    try {
      const response = await fetch('http://localhost:8000/update_path', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ base_path: path })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      console.log('Backend path updated:', data)
      
      // Una vez actualizado el path, buscamos las bases de datos
      await fetchDatabases()
    } catch (error) {
      console.error('Error updating backend path:', error)
      setError('Error al actualizar la ruta en el backend: ' + error.message)
    }
  }

  const fetchDatabases = async () => {
    if (!basePath) return;
    
    setLoading(true)
    try {
      console.log('Fetching databases...')
      const response = await fetch('http://localhost:8000/databases', {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      })
      
      if (!response.ok) {
        const errorText = await response.text()
        console.error('Server error:', errorText)
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const data = await response.json()
      console.log('Received databases:', data)
      
      if (!data.databases) {
        throw new Error('No se recibieron datos válidos del servidor')
      }
      
      // Actualizar el estado con los datos recibidos
      setDatabases(data.databases)
      setCurrentPath(data.base_path)
      setError(null)
      
      // Si solo hay una base de datos, seleccionarla automáticamente
      if (data.databases.length === 1) {
        setSelectedDb(data.databases[0])
        onSelect(data.databases[0])
      } else if (data.databases.length === 0) {
        // Si no hay bases de datos, limpiar la selección
        setSelectedDb('')
        onSelect('')
      }
    } catch (error) {
      console.error('Error fetching databases:', error)
      setError('Error al cargar las bases de datos: ' + error.message)
      setDatabases([])
      setSelectedDb('')
      onSelect('')
    } finally {
      setLoading(false)
    }
  }

  const handleSelect = (e) => {
    const value = e.target.value
    console.log('Selected database:', value)
    setSelectedDb(value)
    onSelect(value)
  }

  if (!basePath) {
    return (
      <div className="card space-y-2">
        <p className="text-sm text-content-secondary">
          Por favor, selecciona primero una carpeta de bases de datos.
        </p>
      </div>
    )
  }

  return (
    <div className="card space-y-2">
      <div className="mb-4">
        <label className="block text-xs font-medium text-content-secondary mb-1">
          Ruta actual
        </label>
        <div className="text-sm text-content-primary bg-background-secondary p-2 rounded border border-border break-all">
          {currentPath || basePath}
        </div>
      </div>

      <label className="block text-sm font-medium text-content-primary">
        Base de datos
      </label>
      
      <div className="relative w-full">
        <select
          value={selectedDb}
          onChange={handleSelect}
          disabled={disabled || loading}
          className="select w-full truncate pr-8"
          style={{ maxWidth: '100%' }}
        >
          <option value="">Seleccionar base de datos</option>
          {databases.map((db) => (
            <option 
              key={db} 
              value={db} 
              title={db}
              style={{ width: 'auto', whiteSpace: 'normal', overflow: 'visible' }}
            >
              {db}
            </option>
          ))}
        </select>

        <div className="absolute inset-y-0 right-0 flex items-center px-2 pointer-events-none">
          <svg className="w-4 h-4 text-content-tertiary" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
          </svg>
        </div>
      </div>

      {loading && (
        <div className="flex items-center gap-2 text-sm text-content-secondary animate-fade-in">
          <svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span>Cargando bases de datos...</span>
        </div>
      )}

      {error && !loading && (
        <div className="flex items-center gap-2 text-sm text-error animate-fade-in">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>{error}</span>
        </div>
      )}

      {!loading && databases.length === 0 && !error && (
        <p className="text-sm text-content-secondary">
          No se encontraron bases de datos en esta carpeta
        </p>
      )}

      {!loading && databases.length > 0 && (
        <p className="text-xs text-content-secondary mt-1">
          {databases.length} {databases.length === 1 ? 'base de datos encontrada' : 'bases de datos encontradas'}
        </p>
      )}
    </div>
  )
}

export default DatabaseSelector
