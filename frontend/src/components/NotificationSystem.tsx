/**
 * NotificationSystem Component
 * Advanced notification system with animations and smart positioning
 */
import React, { useState, useEffect, useCallback } from 'react';

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
  persistent?: boolean;
}

interface NotificationSystemProps {
  maxNotifications?: number;
}

const NotificationSystem: React.FC<NotificationSystemProps> = ({ 
  maxNotifications = 5 
}) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);

  // Add notification function (can be called from anywhere)
  const addNotification = useCallback((notification: Omit<Notification, 'id'>) => {
    const id = Math.random().toString(36).substr(2, 9);
    const newNotification: Notification = {
      id,
      duration: 5000,
      ...notification
    };

    setNotifications(prev => {
      const updated = [newNotification, ...prev];
      return updated.slice(0, maxNotifications);
    });

    // Auto remove notification
    if (!newNotification.persistent && newNotification.duration) {
      setTimeout(() => {
        removeNotification(id);
      }, newNotification.duration);
    }
  }, [maxNotifications]);

  const removeNotification = useCallback((id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  }, []);

  // Expose addNotification globally
  useEffect(() => {
    (window as any).orbisNotifications = {
      add: addNotification,
      remove: removeNotification
    };
  }, [addNotification, removeNotification]);

  const getNotificationIcon = (type: Notification['type']) => {
    switch (type) {
      case 'success':
        return '✅';
      case 'error':
        return '❌';
      case 'warning':
        return '⚠️';
      case 'info':
        return 'ℹ️';
      default:
        return '📢';
    }
  };

  const getNotificationStyles = (type: Notification['type']) => {
    switch (type) {
      case 'success':
        return 'bg-green-500 border-green-400';
      case 'error':
        return 'bg-red-500 border-red-400';
      case 'warning':
        return 'bg-yellow-500 border-yellow-400';
      case 'info':
        return 'bg-blue-500 border-blue-400';
      default:
        return 'bg-gray-500 border-gray-400';
    }
  };

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2 max-w-sm">
      {notifications.map((notification, index) => (
        <div
          key={notification.id}
          className={`
            transform transition-all duration-300 ease-in-out
            ${getNotificationStyles(notification.type)}
            border rounded-lg shadow-lg p-4 text-white
            animate-slide-in-right
          `}
          style={{
            transform: `translateX(${index * 10}px) translateY(${index * 5}px)`,
            zIndex: 1000 - index
          }}
        >
          <div className="flex items-start gap-3">
            <div className="text-xl flex-shrink-0">
              {getNotificationIcon(notification.type)}
            </div>
            
            <div className="flex-1 min-w-0">
              <h4 className="font-semibold text-sm mb-1">
                {notification.title}
              </h4>
              <p className="text-sm opacity-90 leading-relaxed">
                {notification.message}
              </p>
              
              {notification.action && (
                <button
                  onClick={notification.action.onClick}
                  className="mt-2 text-xs underline hover:no-underline transition-all"
                >
                  {notification.action.label}
                </button>
              )}
            </div>
            
            <button
              onClick={() => removeNotification(notification.id)}
              className="flex-shrink-0 text-white opacity-70 hover:opacity-100 transition-opacity"
            >
              <span className="sr-only">Close</span>
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          </div>
          
          {/* Progress bar for auto-dismiss */}
          {!notification.persistent && notification.duration && (
            <div className="absolute bottom-0 left-0 right-0 h-1 bg-black bg-opacity-20 rounded-b-lg overflow-hidden">
              <div 
                className="h-full bg-white bg-opacity-30 animate-progress-bar"
                style={{ 
                  animationDuration: `${notification.duration}ms`,
                  animationFillMode: 'forwards'
                }}
              />
            </div>
          )}
        </div>
      ))}
      
      {/* Custom animations */}
      <style>{`
        @keyframes slide-in-right {
          from {
            transform: translateX(100%);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }
        
        @keyframes progress-bar {
          from {
            width: 100%;
          }
          to {
            width: 0%;
          }
        }
        
        .animate-slide-in-right {
          animation: slide-in-right 0.3s ease-out;
        }
        
        .animate-progress-bar {
          animation: progress-bar linear;
        }
      `}</style>
    </div>
  );
};

// Utility functions for easy notification management
export const notify = {
  success: (title: string, message: string, options?: Partial<Notification>) => {
    (window as any).orbisNotifications?.add({
      type: 'success',
      title,
      message,
      ...options
    });
  },
  
  error: (title: string, message: string, options?: Partial<Notification>) => {
    (window as any).orbisNotifications?.add({
      type: 'error',
      title,
      message,
      persistent: true, // Errors are persistent by default
      ...options
    });
  },
  
  warning: (title: string, message: string, options?: Partial<Notification>) => {
    (window as any).orbisNotifications?.add({
      type: 'warning',
      title,
      message,
      ...options
    });
  },
  
  info: (title: string, message: string, options?: Partial<Notification>) => {
    (window as any).orbisNotifications?.add({
      type: 'info',
      title,
      message,
      ...options
    });
  }
};

export default NotificationSystem;

