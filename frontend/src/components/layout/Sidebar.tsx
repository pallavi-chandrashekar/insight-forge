import { NavLink } from 'react-router-dom'
import { LayoutDashboard, Upload, Search, BarChart3, FileText, MessageCircle } from 'lucide-react'

const navItems = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/upload', icon: Upload, label: 'Upload Data' },
  { to: '/contexts', icon: FileText, label: 'Contexts' },
  { to: '/chat', icon: MessageCircle, label: 'Chat' },
  { to: '/query', icon: Search, label: 'Query' },
  { to: '/visualize', icon: BarChart3, label: 'Visualize' },
]

export default function Sidebar() {
  return (
    <aside className="w-64 bg-white border-r border-gray-200 p-6">
      <nav className="space-y-2">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                isActive
                  ? 'bg-primary-50 text-primary-700 font-medium'
                  : 'text-gray-700 hover:bg-gray-100'
              }`
            }
          >
            <item.icon className="w-5 h-5" />
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
