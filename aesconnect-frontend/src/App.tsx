import { Routes, Route, Link } from 'react-router-dom';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Feed from './pages/Feed';
import { useAuth } from './context/AuthContext';
import './App.css';

function App() {
  const { isAuthenticated, logout, user } = useAuth();
  return (
    <>
      <nav>
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
          {/* Les autres routes (Feed, Profile, etc.) seront ajoutées ici */}
        </Routes>
      </div>
    </>
  );
}

export default App;
