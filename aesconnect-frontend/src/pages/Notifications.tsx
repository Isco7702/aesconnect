import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Navigate } from 'react-router-dom';
import api from '../api/axios';
import { showNotification } from '../utils/notifications';

interface Notification {
  id: number;
  user_id: number;
  message: string;
  is_read: boolean;
  created_at: string;
  entity_type?: string;
  entity_id?: number;
}

const Notifications: React.FC = () => {
  const { isAuthenticated, loading: authLoading } = useAuth();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (isAuthenticated) {
      fetchNotifications();
    }
  }, [isAuthenticated]);

  const fetchNotifications = async () => {
    try {
      const response = await api.get('/notifications/notifications');
      setNotifications(response.data.notifications || []);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Erreur lors du chargement des notifications');
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (notificationId: number) => {
    try {
      await api.put(`/notifications/notifications/${notificationId}/read`);
      setNotifications(notifications.map(notif => 
        notif.id === notificationId ? { ...notif, is_read: true } : notif
      ));
      showNotification('Notification marquée comme lue', 'success');
    } catch (err: any) {
      showNotification('Erreur lors du marquage de la notification', 'error');
    }
  };

  const markAllAsRead = async () => {
    try {
      await api.put('/notifications/notifications/mark-all-read');
      setNotifications(notifications.map(notif => ({ ...notif, is_read: true })));
      showNotification('Toutes les notifications ont été marquées comme lues', 'success');
    } catch (err: any) {
      showNotification('Erreur lors du marquage des notifications', 'error');
    }
  };

  const deleteNotification = async (notificationId: number) => {
    try {
      await api.delete(`/notifications/notifications/${notificationId}`);
      setNotifications(notifications.filter(notif => notif.id !== notificationId));
      showNotification('Notification supprimée', 'success');
    } catch (err: any) {
      showNotification('Erreur lors de la suppression', 'error');
    }
  };

  if (authLoading || loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }

  const unreadCount = notifications.filter(n => !n.is_read).length;

  return (
    <div className="container" style={{ maxWidth: '800px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
        <h2>
          🔔 Notifications {unreadCount > 0 && (
            <span style={{ 
              background: 'var(--accent-color)', 
              color: 'white', 
              padding: '4px 12px', 
              borderRadius: '20px',
              fontSize: '0.8rem',
              marginLeft: '10px'
            }}>
              {unreadCount} nouvelle{unreadCount > 1 ? 's' : ''}
            </span>
          )}
        </h2>
        {notifications.length > 0 && unreadCount > 0 && (
          <button
            onClick={markAllAsRead}
            style={{
              padding: '10px 20px',
              background: 'var(--primary-color)',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontWeight: 'bold'
            }}
          >
            ✓ Tout marquer comme lu
          </button>
        )}
      </div>

      {error && <div className="error">{error}</div>}

      {notifications.length === 0 ? (
        <div style={{ 
          textAlign: 'center', 
          padding: '60px 20px',
          background: 'var(--bg-card)',
          borderRadius: '16px',
          border: '2px solid var(--border-color)'
        }}>
          <div style={{ fontSize: '4rem', marginBottom: '20px' }}>🔔</div>
          <h3 style={{ color: 'var(--text-muted)' }}>Aucune notification</h3>
          <p style={{ color: 'var(--text-muted)' }}>
            Vous serez notifié ici des nouvelles activités sur votre compte
          </p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
          {notifications.map((notif) => (
            <div
              key={notif.id}
              style={{
                background: notif.is_read ? 'var(--bg-card)' : 'rgba(34, 197, 94, 0.05)',
                border: notif.is_read ? '2px solid var(--border-color)' : '2px solid var(--primary-color)',
                borderRadius: '12px',
                padding: '20px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'flex-start',
                gap: '15px',
                transition: 'var(--transition)'
              }}
            >
              <div style={{ flex: 1 }}>
                <div style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: '10px',
                  marginBottom: '10px'
                }}>
                  <span style={{ fontSize: '1.5rem' }}>
                    {notif.entity_type === 'like' && '❤️'}
                    {notif.entity_type === 'comment' && '💬'}
                    {notif.entity_type === 'follow' && '👥'}
                    {!notif.entity_type && '📢'}
                  </span>
                  {!notif.is_read && (
                    <span style={{
                      width: '10px',
                      height: '10px',
                      background: 'var(--primary-color)',
                      borderRadius: '50%',
                      display: 'inline-block'
                    }}></span>
                  )}
                </div>
                <p style={{ 
                  margin: '0 0 8px 0', 
                  color: 'var(--text-light)',
                  fontWeight: notif.is_read ? 'normal' : 'bold'
                }}>
                  {notif.message}
                </p>
                <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                  {new Date(notif.created_at).toLocaleString('fr-FR')}
                </span>
              </div>
              <div style={{ display: 'flex', gap: '10px' }}>
                {!notif.is_read && (
                  <button
                    onClick={() => markAsRead(notif.id)}
                    style={{
                      padding: '8px 12px',
                      background: 'var(--primary-color)',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      fontSize: '0.9rem'
                    }}
                    title="Marquer comme lu"
                  >
                    ✓
                  </button>
                )}
                <button
                  onClick={() => deleteNotification(notif.id)}
                  style={{
                    padding: '8px 12px',
                    background: 'var(--accent-color)',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontSize: '0.9rem'
                  }}
                  title="Supprimer"
                >
                  🗑️
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Notifications;
