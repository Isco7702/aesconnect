import React from 'react';
import Notifications from '../components/Notifications';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const NotificationsPage: React.FC = () => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) return <div>Chargement...</div>;
  if (!isAuthenticated) return <Navigate to="/login" />;

  return (
    <div className="notifications-page">
      <Notifications />
    </div>
  );
};

export default NotificationsPage;
