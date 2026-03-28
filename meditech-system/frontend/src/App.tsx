import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'sonner'
import { AuthProvider, useAuth } from './context/AuthContext'

// Páginas
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Patients from './pages/Patients'
import Invoices from './pages/Invoices'
import Results from './pages/Results'
import Settings from './pages/Settings'
import SetupRoot from './pages/SetupRoot'

// Componentes de layout
import Sidebar from './components/Sidebar'

// Protected Route Component
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}

// Layout principal
const MainLayout = ({ children }: { children: React.ReactNode }) => {
  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar />
      <main className="flex-1 overflow-auto p-8">
        {children}
      </main>
    </div>
  )
}

function AppRoutes() {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <Routes>
      <Route path="/login" element={!isAuthenticated ? <Login /> : <Navigate to="/dashboard" />} />
      <Route path="/setup" element={<SetupRoot />} />
      
      <Route path="/dashboard" element={
        <ProtectedRoute>
          <MainLayout><Dashboard /></MainLayout>
        </ProtectedRoute>
      } />
      
      <Route path="/patients" element={
        <ProtectedRoute>
          <MainLayout><Patients /></MainLayout>
        </ProtectedRoute>
      } />
      
      <Route path="/invoices" element={
        <ProtectedRoute>
          <MainLayout><Invoices /></MainLayout>
        </ProtectedRoute>
      } />
      
      <Route path="/results" element={
        <ProtectedRoute>
          <MainLayout><Results /></MainLayout>
        </ProtectedRoute>
      } />
      
      <Route path="/settings" element={
        <ProtectedRoute>
          <MainLayout><Settings /></MainLayout>
        </ProtectedRoute>
      } />
      
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Toaster 
          position="top-right"
          richColors
          closeButton
          duration={4000}
        />
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App
