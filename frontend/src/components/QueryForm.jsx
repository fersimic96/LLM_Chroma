import { useState, useRef, useEffect } from 'react'
import CollectionSelector from './CollectionSelector'

function QueryForm({ onSubmit, disabled }) {
  const [query, setQuery] = useState('')
  const [selectedCollections, setSelectedCollections] = useState([])
  const textareaRef = useRef(null)

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!query.trim() || disabled || selectedCollections.length === 0) return

    onSubmit({
      query: query.trim(),
      collections: selectedCollections
    })
    setQuery('')
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`
    }
  }, [query])

  return (
    <div className="space-y-4">
      <CollectionSelector 
        onSelect={setSelectedCollections}
      />

      <form onSubmit={handleSubmit} className="relative">
        <div className="relative flex items-end gap-2">
          <div className="flex-1">
            <textarea
              ref={textareaRef}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={
                disabled 
                  ? "Selecciona una base de datos..." 
                  : selectedCollections.length === 0
                  ? "Selecciona al menos una colección..."
                  : "Escribe tu pregunta..."
              }
              disabled={disabled || selectedCollections.length === 0}
              className="input min-h-[48px] max-h-[200px] resize-none"
              rows={1}
            />
          </div>

          <button
            type="submit"
            disabled={!query.trim() || disabled || selectedCollections.length === 0}
            className="btn btn-primary hover-effect"
          >
            <span className="text-content-primary">Enviar</span>
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
            </svg>
          </button>
        </div>
      </form>
    </div>
  )
}

export default QueryForm
