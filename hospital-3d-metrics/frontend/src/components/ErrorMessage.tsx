import React from 'react';

interface ErrorMessageProps {
  message: string;
  onRetry?: () => void;
}

export const ErrorMessage: React.FC<ErrorMessageProps> = ({ message, onRetry }) => {
  return (
    <div className="error-container" style={styles.container}>
      <div style={styles.content}>
        <h2 style={styles.heading}>Error Loading Data</h2>
        <p style={styles.message}>{message}</p>
        {onRetry && (
          <button onClick={onRetry} style={styles.button}>
            Retry
          </button>
        )}
      </div>
    </div>
  );
};

const styles = {
  container: {
    position: 'fixed' as const,
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
    zIndex: 1000,
  },
  content: {
    backgroundColor: 'white',
    padding: '2rem',
    borderRadius: '8px',
    boxShadow: '0 2px 10px rgba(0, 0, 0, 0.1)',
    textAlign: 'center' as const,
    maxWidth: '400px',
  },
  heading: {
    color: '#dc3545',
    marginBottom: '1rem',
    fontSize: '1.5rem',
  },
  message: {
    color: '#666',
    marginBottom: '1.5rem',
  },
  button: {
    backgroundColor: '#007dc3',
    color: 'white',
    border: 'none',
    padding: '0.5rem 1.5rem',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '1rem',
    transition: 'background-color 0.2s',
    ':hover': {
      backgroundColor: '#0056b3',
    },
  },
} as const;
