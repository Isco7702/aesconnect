import { Routes, Route, Link, useLocation } from 'react-router-dom';
import { useState } from 'react';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Feed from './pages/Feed';
import Profile from './pages/Profile';
import Search from './pages/Search';
import Notifications from './pages/Notifications';
import { useAuth } from './context/AuthContext';
import './App.css';

function App() {
  const { isAuthenticated, logout, user } = useAuth();
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  const isActive = (path: string) => {
    return location.pathname === path ? 'active' : '';
  };

  return (
    <>
      <nav className="main-nav">
        <div className="nav-container">
          <div className="nav-logo">
            <Link to="/">
              <span className="logo-icon">🌍</span>
              <span className="logo-text">AESConnect</span>
            </Link>
          </div>
          
          <button className="mobile-menu-toggle" onClick={toggleMobileMenu}>
            <span className="menu-icon">{isMobileMenuOpen ? '✕' : '☰'}</span>
          </button>

          <ul className={`nav-links ${isMobileMenuOpen ? 'mobile-open' : ''}`}>
            {isAuthenticated ? (
              <>
                <li>
                  <Link to="/feed" className={isActive('/feed')} onClick={() => setIsMobileMenuOpen(false)}>
                    <span className="nav-icon">📰</span>
                    <span className="nav-text">Fil d'actualité</span>
                  </Link>
                </li>
                <li>
                  <Link to="/search" className={isActive('/search')} onClick={() => setIsMobileMenuOpen(false)}>
                    <span className="nav-icon">🔍</span>
                    <span className="nav-text">Recherche</span>
                  </Link>
                </li>
                <li>
                  <Link to="/notifications" className={isActive('/notifications')} onClick={() => setIsMobileMenuOpen(false)}>
                    <span className="nav-icon">🔔</span>
                    <span className="nav-text">Notifications</span>
                  </Link>
                </li>
                <li>
                  <Link to="/profile" className={isActive('/profile')} onClick={() => setIsMobileMenuOpen(false)}>
                    <span className="nav-icon">👤</span>
                    <span className="nav-text">Profil</span>
                  </Link>
                </li>
                <li className="user-info">
                  <div className="user-avatar">
                    {user?.avatar_url ? (
                      <img src={user.avatar_url} alt={user.username} />
                    ) : (
                      <span className="default-avatar">👤</span>
                    )}
                  </div>
                  <span className="username">{user?.username}</span>
                </li>
                <li>
                  <button className="logout-btn" onClick={() => { logout(); setIsMobileMenuOpen(false); }}>
                    <span className="nav-icon">🚪</span>
                    <span className="nav-text">Déconnexion</span>
                  </button>
                </li>
              </>
            ) : (
              <>
                <li>
                  <Link to="/" className={isActive('/')} onClick={() => setIsMobileMenuOpen(false)}>
                    <span className="nav-icon">🏠</span>
                    <span className="nav-text">Accueil</span>
                  </Link>
                </li>
                <li>
                  <Link to="/login" className={`login-link ${isActive('/login')}`} onClick={() => setIsMobileMenuOpen(false)}>
                    <span className="nav-icon">🔑</span>
                    <span className="nav-text">Connexion</span>
                  </Link>
                </li>
                <li>
                  <Link to="/register" className={`register-link ${isActive('/register')}`} onClick={() => setIsMobileMenuOpen(false)}>
                    <span className="nav-icon">📝</span>
                    <span className="nav-text">Inscription</span>
                  </Link>
                </li>
              </>
            )}
          </ul>
        </div>
      </nav>
      
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/feed" element={<Feed />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/search" element={<Search />} />
          <Route path="/notifications" element={<Notifications />} />
        </Routes>
      </main>
      
      <div id="notification-container" className="notification-container"></div>
    </>
  );
}

export default App;
