import React, { useState, useEffect } from 'react';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';
import type { Notification } from '../types';



const Notifications: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchNotifications = async () => {
    if (!isAuthenticated) return;
    setLoading(true);
    try {
      const response = await api.get('/notifications/');
      setNotifications((response.data as { notifications: Notification[] }).notifications);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Erreur lors du chargement des notifications');
    } finally {
      setLoading(false);
    }
  };

  const markAllAsRead = async () => {
    try {
      await api.post('/notifications/mark_read');
      setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
    } catch (err: any) {
      setError(err.response?.data?.message || 'Erreur lors du marquage comme lu');
    }
  };

  useEffect(() => {
    fetchNotifications();
  }, [isAuthenticated]);

  if (!isAuthenticated) return null;
  if (loading) return <div className="notifications-container">Chargement des notifications...</div>;
  if (error) return <div className="notifications-container error">{error}</div>;

  const unreadCount = notifications.filter(n => !n.is_read).length;

  return (
    <div className="notifications-container">
      <h3>Notifications ({unreadCount} non lues)</h3>
      {notifications.length === 0 ? (
        <p>Vous n'avez aucune notification.</p>
      ) : (
        <>
          {unreadCount > 0 && (
            <button onClick={markAllAsRead} className="mark-read-button">
              Marquer tout comme lu
            </button>
          )}
          <div className="notifications-list">
            {notifications.map((n) => (
              <div key={n.id} className={`notification-item ${n.is_read ? 'read' : 'unread'}`}>
                <p>{n.content}</p>
                <span className="notification-date">
                  {new Date(n.created_at).toLocaleDateString()}
                </span>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
};

export default Notifications;
