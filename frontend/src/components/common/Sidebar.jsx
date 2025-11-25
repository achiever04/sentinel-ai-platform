// ============================================================================
// frontend/src/components/common/Sidebar.jsx
// ============================================================================

import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  Video,
  Users,
  AlertTriangle,
  BarChart3,
  Settings,
  Shield,
  LogOut
} from 'lucide-react';
import { useAuthStore } from '../../store/authStore';

export default function Sidebar({ role = 'operator' }) {
  const location = useLocation();
  const logout = useAuthStore(state => state.logout);
  
  const adminLinks = [
    { name: 'Dashboard', href: '/admin', icon: LayoutDashboard },
    { name: 'Cameras', href: '/admin/cameras', icon: Video },
    { name: 'Watchlist', href: '/watchlist', icon: Users },
    { name: 'Alerts', href: '/admin/alerts', icon: AlertTriangle },
    { name: 'Analytics', href: '/analytics', icon: BarChart3 },
    { name: 'Federated', href: '/federated', icon: Shield },
    { name: 'Settings', href: '/settings', icon: Settings },
  ];
  
  const operatorLinks = [
    { name: 'Dashboard', href: '/operator', icon: LayoutDashboard },
    { name: 'Live Monitor', href: '/live', icon: Video },
    { name: 'Watchlist', href: '/watchlist', icon: Users },
    { name: 'Alerts', href: '/operator/alerts', icon: AlertTriangle },
    { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  ];
  
  const links = role === 'admin' ? adminLinks : operatorLinks;
  
  const isActive = (href) => location.pathname === href;
  
  return (
    <div className="flex flex-col h-screen bg-gray-900 text-white w-64">
      {/* Logo */}
      <div className="flex items-center justify-center h-16 border-b border-gray-700">
        <Shield className="w-8 h-8 text-blue-500" />
        <span className="ml-2 text-xl font-bold">Sentinel AI</span>
      </div>
      
      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-4">
        {links.map((link) => (
          <Link
            key={link.name}
            to={link.href}
            className={`flex items-center px-6 py-3 text-sm font-medium transition-colors ${
              isActive(link.href)
                ? 'bg-blue-600 text-white'
                : 'text-gray-300 hover:bg-gray-800 hover:text-white'
            }`}
          >
            <link.icon className="w-5 h-5 mr-3" />
            {link.name}
          </Link>
        ))}
      </nav>
      
      {/* Logout */}
      <div className="border-t border-gray-700">
        <button
          onClick={logout}
          className="flex items-center w-full px-6 py-3 text-sm font-medium text-gray-300 hover:bg-gray-800 hover:text-white transition-colors"
        >
          <LogOut className="w-5 h-5 mr-3" />
          Logout
        </button>
      </div>
    </div>
  );
}
