import { useState } from 'react';
import { Link } from 'react-router-dom';
import EmbeddingUploader from './EmbeddingUploader';

function Sidebar() {
  const [isCollapsed, setIsCollapsed] = useState(false);

  const toggleSidebar = () => {
    setIsCollapsed(!isCollapsed);
  };

  return (
    <aside
      className={`bg-background-secondary border-r border-border transition-all ${
        isCollapsed ? 'w-16' : 'w-64'
      }`}
    >
      <div className="flex flex-col h-full">
        <div className="p-4 border-b border-border flex items-center justify-between">
          {!isCollapsed && (
            <div className="flex items-center gap-2">
              <img src="/chatbot.svg" alt="Logo" className="w-6 h-6" />
              <h1 className="text-lg font-bold">ChatBot</h1>
            </div>
          )}
          {isCollapsed && <img src="/chatbot.svg" alt="Logo" className="w-6 h-6 mx-auto" />}
          <button
            onClick={toggleSidebar}
            className="text-content-secondary hover:text-content-primary transition-colors"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              {isCollapsed ? (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 5l7 7-7 7M5 5l7 7-7 7"
                />
              ) : (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M11 19l-7-7 7-7m8 14l-7-7 7-7"
                />
              )}
            </svg>
          </button>
        </div>

        <nav className="p-2 flex-1 overflow-y-auto">
          <ul className="space-y-1">
            <li>
              <Link
                to="/"
                className="flex items-center gap-3 p-2 rounded-md hover:bg-background text-content-primary hover:text-primary transition-colors"
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
                  />
                </svg>
                {!isCollapsed && <span>Inicio</span>}
              </Link>
            </li>
            <li>
              <Link
                to="/collections"
                className="flex items-center gap-3 p-2 rounded-md hover:bg-background text-content-primary hover:text-primary transition-colors"
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
                  />
                </svg>
                {!isCollapsed && <span>Colecciones</span>}
              </Link>
            </li>
          </ul>
        </nav>

        <div className="p-2 border-t border-border">
          <div className="text-xs text-content-tertiary p-2">
            {!isCollapsed && <span>v1.0.0</span>}
          </div>
        </div>
      </div>
    </aside>
  );
}

export default Sidebar;
