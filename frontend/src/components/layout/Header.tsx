import { useAuthStore } from '../../store/authStore'
import { LogOut, User } from 'lucide-react'

export default function Header() {
  const { user, logout } = useAuthStore()

  return (
    <header className="bg-white border-b border-gray-200 px-8 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-lg">IF</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-900">InsightForge</h1>
        </div>

        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 text-gray-700">
            <User className="w-5 h-5" />
            <span>{user?.email}</span>
          </div>
          <button
            onClick={logout}
            className="flex items-center space-x-2 px-4 py-2 text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <LogOut className="w-5 h-5" />
            <span>Logout</span>
          </button>
        </div>
      </div>
    </header>
  )
}
