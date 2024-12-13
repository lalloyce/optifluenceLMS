import React from 'react';
import { Layout, Menu, Home, FileText, DollarSign, User, Bell, Settings } from 'lucide-react';
import { Link, Outlet } from 'react-router-dom';

export function DashboardLayout() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center">
            <DollarSign className="h-8 w-8 text-blue-600" />
            <span className="ml-2 text-xl font-bold text-gray-900">LoanPro</span>
          </div>
          <div className="flex items-center space-x-4">
            <Bell className="h-6 w-6 text-gray-500 cursor-pointer" />
            <div className="h-8 w-8 rounded-full bg-blue-600 text-white flex items-center justify-center">
              <User className="h-5 w-5" />
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex gap-6">
          {/* Sidebar */}
          <aside className="w-64 flex-shrink-0">
            <nav className="space-y-1">
              <Link to="/dashboard" className="flex items-center px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-md">
                <Home className="h-5 w-5 mr-3" />
                Dashboard
              </Link>
              <Link to="/loans" className="flex items-center px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-md">
                <FileText className="h-5 w-5 mr-3" />
                My Loans
              </Link>
              <Link to="/payments" className="flex items-center px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-md">
                <DollarSign className="h-5 w-5 mr-3" />
                Payments
              </Link>
              <Link to="/profile" className="flex items-center px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-md">
                <User className="h-5 w-5 mr-3" />
                Profile
              </Link>
              <Link to="/settings" className="flex items-center px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-md">
                <Settings className="h-5 w-5 mr-3" />
                Settings
              </Link>
            </nav>
          </aside>

          {/* Main Content */}
          <main className="flex-1">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  );
}