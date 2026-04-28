import { Routes, Route, Link } from 'react-router-dom';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Feed from './pages/Feed';
import Profile from './pages/Profile';
import NotificationsPage from './pages/NotificationsPage';
import { useAuth } from './context/AuthContext';
import './App.css';

function App() {
  const { isAuthenticated, logout, user } = useAuth();
  return (
    <>
      <nav>
        <div className="logo-section">
          <span className="flag-icon">🇲🇱</span>
          <span className="flag-icon">🇧🇫</span>
          <span className="flag-icon">🇳🇪</span>
          <Link to="/" className="app-title">AES Connect</Link>
          <span className="slogan">"Notre voix, notre espace, notre Sahel"</span>
        </div>
        <ul>
          <li>
            <Link to="/">Accueil</Link>
          </li>
          <li>
            <Link to="/login">Connexion</Link>
          </li>
          {isAuthenticated ? (
            <>
              <li>
                <Link to="/feed">Fil d'actualité</Link>
              </li>
              <li>
                <Link to="/profile">Profil</Link>
              </li>
              <li>
                <Link to="/notifications">Notifications</Link>
              </li>
              <li>
                <button onClick={logout}>Déconnexion ({user?.username})</button>
              </li>
            </>
          ) : (
            <>
              <li>
                <Link to="/login">Connexion</Link>
              </li>
              <li>
                <Link to="/register">Inscription</Link>
              </li>
            </>
          )}
        </ul>
      </nav>
      <div className="container">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/feed" element={<Feed />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/notifications" element={<NotificationsPage />} />
          {/* Les autres routes (Feed, Profile, etc.) seront ajoutées ici */}
        </Routes>
      </div>
    </>
  );
}

export default App;
