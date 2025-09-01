import { AuthProvider } from './Context/AuthContext'
import { Route, Routes } from 'react-router-dom'
import Layout from './Layout/Layout'
import LandingPage from './pages/LandingPage'
import AuthPage from './pages/AuthPage'
import Dashboard from './pages/Dashboard'
import './App.css'
import ProtectedRoute from './Components/ProtectedRoute'

function App() {
  return (
    <AuthProvider> 
      <Routes>
        {/* Routes that use Layout */}
        <Route element={<Layout />}>
          <Route path="/" element={<LandingPage />} />
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } 
            />
          </Route>
        {/* Fullscreen route without Layout */}
        <Route path="/auth" element={<AuthPage />} />
      </Routes>
    </AuthProvider>
  )
}

export default App
