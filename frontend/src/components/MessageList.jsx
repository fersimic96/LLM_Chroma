import { useEffect, useRef } from 'react'

function MessageList({ messages = [], loading = false }) {
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  return (
    <div className="h-full overflow-y-auto p-4 space-y-4">
      {messages.map((message, index) => (
        <div
          key={index}
          className={`flex ${message.role === 'assistant' ? 'justify-start' : 'justify-end'}`}
        >
          <div className={`flex gap-3 max-w-[85%] ${message.role === 'assistant' ? 'flex-row' : 'flex-row-reverse'}`}>
            {/* Avatar */}
            <div className={`flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center
              ${message.role === 'assistant' ? 'bg-success' : 'bg-primary'}`}
            >
              <span className="text-lg">
                {message.role === 'assistant' ? '🤖' : '👤'}
              </span>
            </div>

            {/* Message content */}
            <div className={`flex flex-col space-y-2 ${message.role === 'assistant' ? 'items-start' : 'items-end'}`}>
              {/* Role label */}
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-content-secondary">
                  {message.role === 'assistant' ? 'Asistente' : 'Tú'}
                </span>
              </div>

              {/* Message bubble */}
              <div
                className={`p-3 rounded-lg ${
                  message.role === 'assistant'
                    ? message.error
                      ? 'bg-error/10 text-error'
                      : 'bg-success/10'
                    : 'bg-primary/10'
                }`}
              >
                <p className="whitespace-pre-wrap">{message.content}</p>
              </div>

              {/* Sources */}
              {message.sources && message.sources.length > 0 && (
                <div className="flex flex-col gap-1 mt-2">
                  <span className="text-sm font-medium text-content-secondary">Fuentes:</span>
                  <div className="space-y-1">
                    {message.sources.map((source, idx) => (
                      <div key={idx} className="flex items-center gap-2 text-sm text-content-secondary">
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        <span>{source}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      ))}

      {/* Loading indicator */}
      {loading && (
        <div className="flex justify-start">
          <div className="flex gap-3 max-w-[85%]">
            <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-success flex items-center justify-center">
              <span className="text-lg">🤖</span>
            </div>
            <div className="flex flex-col space-y-2">
              <span className="text-sm font-medium text-content-secondary">Asistente</span>
              <div className="p-3 rounded-lg bg-success/10">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-content-secondary rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-2 h-2 bg-content-secondary rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-2 h-2 bg-content-secondary rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  )
}

export default MessageList
