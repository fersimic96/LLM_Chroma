import MessageList from './MessageList';

const ResponseDisplay = ({ messages, loading, currentResponse }) => {
  // Si hay una respuesta en streaming, la agregamos temporalmente a los mensajes
  const displayMessages = [...messages];
  if (currentResponse) {
    displayMessages.push({
      role: 'assistant',
      content: currentResponse
    });
  }

  if (!messages || messages.length === 0 && !currentResponse) {
    return (
      <div className="flex-1 flex items-center justify-center text-content-secondary">
        <div className="text-center space-y-4">
          <div className="flex justify-center">
            <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center">
              <span className="text-4xl">🤖</span>
            </div>
          </div>
          <h2 className="text-xl font-semibold">¡Bienvenido al ChatBot!</h2>
          <p className="text-content-secondary max-w-md">
            Selecciona una base de datos y haz una pregunta para comenzar.
            El ChatBot te ayudará a encontrar la información que necesitas.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-hidden">
      <MessageList messages={displayMessages} loading={loading} />
    </div>
  );
};

export default ResponseDisplay;
