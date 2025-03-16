import { useState } from 'react';

function Sidebar({ onDatabasePathChange }) {
  const [selectedPath, setSelectedPath] = useState('');
  const [error, setError] = useState(null);

  const handleSelectDirectory = async () => {
    try {
      const response = await fetch('http://localhost:8000/select_folder', {
        method: 'POST'
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      const selectedPath = data.selected_path;
      console.log('Selected directory path:', selectedPath);

      if (selectedPath) {
        setSelectedPath(selectedPath);
        onDatabasePathChange(selectedPath);
      }
    } catch (error) {
      console.error('Error selecting directory:', error);
      setError('Error al seleccionar el directorio: ' + error.message);
    }
  };

  return (
    <div className="w-64 bg-background border-r border-border p-4">
      <div className="space-y-4">
        <button
          onClick={handleSelectDirectory}
          className="btn btn-primary w-full flex items-center justify-center gap-2"
        >
          <svg 
            className="w-5 h-5" 
            fill="none" 
            viewBox="0 0 24 24" 
            stroke="currentColor"
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" 
            />
          </svg>
          Seleccionar DB
        </button>

        {selectedPath && (
          <div className="text-sm text-content-secondary break-all">
            <p className="font-medium mb-1">Ruta actual:</p>
            <div className="p-2 bg-background-secondary rounded border border-border">
              {selectedPath}
            </div>
          </div>
        )}

        {error && (
          <div className="mt-2 text-sm text-error">
            {error}
          </div>
        )}
      </div>
    </div>
  );
};

export default Sidebar;
