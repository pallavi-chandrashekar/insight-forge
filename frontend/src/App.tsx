import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import Layout from './components/layout/Layout'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Upload from './pages/Upload'
import Datasets from './pages/Datasets'
import Dataset from './pages/Dataset'
import Query from './pages/Query'
import Visualize from './pages/Visualize'
import Contexts from './pages/Contexts'
import ContextDetail from './pages/ContextDetail'
import ContextCreate from './pages/ContextCreate'
import Chat from './pages/Chat'
import Settings from './pages/Settings'

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useAuthStore()

  if (isLoading) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>
  }

  return user ? <>{children}</> : <Navigate to="/login" />
}

function PublicRoute({ children }: { children: React.ReactNode }) {
  const { user } = useAuthStore()
  return user ? <Navigate to="/dashboard" /> : <>{children}</>
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={
          <PublicRoute>
            <Login />
          </PublicRoute>
        } />
        <Route path="/register" element={
          <PublicRoute>
            <Register />
          </PublicRoute>
        } />

        <Route path="/" element={
          <PrivateRoute>
            <Layout />
          </PrivateRoute>
        }>
          <Route index element={<Navigate to="/dashboard" />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="upload" element={<Upload />} />
          <Route path="datasets" element={<Datasets />} />
          <Route path="datasets/:id" element={<Dataset />} />
          <Route path="query" element={<Query />} />
          <Route path="visualize" element={<Visualize />} />
          <Route path="contexts" element={<Contexts />} />
          <Route path="contexts/new" element={<ContextCreate />} />
          <Route path="contexts/:id" element={<ContextDetail />} />
          <Route path="chat" element={<Chat />} />
          <Route path="settings" element={<Settings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
