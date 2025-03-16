import { useState, useEffect } from 'react'
import Sidebar from './components/Sidebar'
import QueryForm from './components/QueryForm'
import ResponseDisplay from './components/ResponseDisplay'
import DatabaseSelector from './components/DatabaseSelector'
import ApiKeyInput from './components/ApiKeyInput'

function App() {
  const [selectedDatabase, setSelectedDatabase] = useState(null)
  const [databasePath, setDatabasePath] = useState('')
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [isPathSelected, setIsPathSelected] = useState(false)
  const [currentResponse, setCurrentResponse] = useState('')
  const [isApiKeyConfigured, setIsApiKeyConfigured] = useState(false)

  // Cargar la ruta guardada al iniciar
  useEffect(() => {
    const savedPath = localStorage.getItem('databasePath')
    if (savedPath) {
      console.log('Loading saved path:', savedPath)
      handleDatabasePathChange(savedPath)
    }

    // Verificar si hay una API key guardada
    const savedKey = localStorage.getItem('openai_api_key')
    if (savedKey) {
      setIsApiKeyConfigured(true)
    }
  }, [])

  const handleDatabasePathChange = async (path) => {
    console.log('Database path changed:', path)
    
    // Limpiar el estado actual
    setSelectedDatabase(null)
    setDatabasePath(path)
    setIsPathSelected(true)
    setMessages([])
    
    // Guardar la ruta en localStorage
    localStorage.setItem('databasePath', path)
  }

  const handleDatabaseSelect = (database) => {
    console.log('Database selected:', database)
    setSelectedDatabase(database)
  }

  const handleSubmit = async (query) => {
    if (!selectedDatabase || !query.trim()) {
      console.log('Cannot submit: no database selected or empty query')
      return
    }

    // Agregar mensaje del usuario
    const userMessage = { role: 'user', content: query }
    setMessages(prev => [...prev, userMessage])
    
    console.log('Submitting query:', { database: selectedDatabase, path: databasePath, query })
    setIsLoading(true)
    setCurrentResponse('')

    try {
      const response = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query,
          database: selectedDatabase,
          base_path: databasePath
        }),
      })

      if (!response.ok) throw new Error('Error en la consulta')

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let fullResponse = ''

      while (true) {
        const { value, done } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(5))
              if (data.done) {
                fullResponse = data.text
                setCurrentResponse(data.text)
              } else {
                fullResponse += data.delta || ''
                setCurrentResponse(prev => prev + (data.delta || ''))
              }
            } catch (e) {
              console.error('Error parsing JSON:', e)
            }
          }
        }
      }

      // Separar la respuesta y las fuentes
      const [content, sourcesText] = fullResponse.split('\n\nFuentes:\n')
      const sources = sourcesText 
        ? sourcesText.split('\nFuente [').filter(Boolean).map(s => 'Fuente [' + s) 
        : []

      // Agregar mensaje del asistente
      const assistantMessage = {
        role: 'assistant',
        content: content,
        sources: sources
      }
      setMessages(prev => [...prev, assistantMessage])

    } catch (error) {
      console.error('Error:', error)
      const errorMessage = {
        role: 'assistant',
        content: 'Error al procesar la consulta',
        error: true
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
      setCurrentResponse('')
    }
  }

  return (
    <div className="flex h-screen bg-background text-content-primary">
      <Sidebar 
        onDatabasePathChange={handleDatabasePathChange}
        currentPath={databasePath}
      />
      
      <main className="flex-1 flex flex-col">
        {!isPathSelected ? (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center space-y-4">
              <p className="text-lg text-content-secondary">
                Selecciona una carpeta para comenzar
              </p>
            </div>
          </div>
        ) : (
          <>
            <div className="p-4 border-b border-border">
              <ApiKeyInput onApiKeySet={setIsApiKeyConfigured} />
            </div>

            {isApiKeyConfigured && (
              <>
                <div className="p-4 border-b border-border">
                  <DatabaseSelector
                    onSelect={handleDatabaseSelect}
                    disabled={!isPathSelected}
                    basePath={databasePath}
                  />
                </div>

                <div className="flex-1 overflow-auto p-4">
                  <ResponseDisplay 
                    messages={messages} 
                    loading={isLoading} 
                    currentResponse={currentResponse}
                  />
                </div>

                <div className="p-4 border-t border-border">
                  <QueryForm
                    onSubmit={handleSubmit}
                    disabled={!selectedDatabase || !isApiKeyConfigured}
                  />
                </div>
              </>
            )}
          </>
        )}
      </main>
    </div>
  )
}

export default App
