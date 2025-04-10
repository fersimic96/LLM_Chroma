import { useState } from 'react';
import EmbeddingUploader from './EmbeddingUploader';

function Sidebar() {
  return (
    <div className="w-64 bg-background border-r border-border p-4">
      <div className="space-y-4">
        <div className="mt-2">
          <h3 className="text-sm font-medium mb-2">Cargar Archivos</h3>
          <EmbeddingUploader />
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
