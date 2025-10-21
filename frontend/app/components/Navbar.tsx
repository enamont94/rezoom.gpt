'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Menu, X, User } from 'lucide-react'

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <nav className="bg-white/80 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <Link href="/" className="flex-shrink-0">
              <h1 className="text-2xl font-bold text-primary">Rezoom.ai</h1>
            </Link>
          </div>
          
          {/* Desktop Navigation */}
          <div className="hidden md:block">
            <div className="ml-10 flex items-baseline space-x-4">
              <Link href="/dashboard" className="text-gray-600 hover:text-primary px-3 py-2 rounded-md text-sm font-medium">
                Dashboard
              </Link>
              <Link href="/pricing" className="text-gray-600 hover:text-primary px-3 py-2 rounded-md text-sm font-medium">
                Pricing
              </Link>
              <Link href="/about" className="text-gray-600 hover:text-primary px-3 py-2 rounded-md text-sm font-medium">
                About
              </Link>
              <div className="flex items-center space-x-4">
                <Link href="/login" className="text-gray-600 hover:text-primary px-3 py-2 rounded-md text-sm font-medium">
                  Sign In
                </Link>
                <button className="btn-primary">
                  Get Started
                </button>
              </div>
            </div>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="text-gray-600 hover:text-primary focus:outline-none focus:text-primary"
            >
              {isOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isOpen && (
          <div className="md:hidden">
            <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3 bg-white border-t border-gray-200">
              <Link href="/dashboard" className="text-gray-600 hover:text-primary block px-3 py-2 rounded-md text-base font-medium">
                Dashboard
              </Link>
              <Link href="/pricing" className="text-gray-600 hover:text-primary block px-3 py-2 rounded-md text-base font-medium">
                Pricing
              </Link>
              <Link href="/about" className="text-gray-600 hover:text-primary block px-3 py-2 rounded-md text-base font-medium">
                About
              </Link>
              <div className="pt-4 pb-3 border-t border-gray-200">
                <div className="flex items-center px-3">
                  <div className="flex-shrink-0">
                    <User className="h-8 w-8 text-gray-400" />
                  </div>
                  <div className="ml-3">
                    <div className="text-base font-medium text-gray-800">Welcome</div>
                    <div className="text-sm font-medium text-gray-500">Sign in to your account</div>
                  </div>
                </div>
                <div className="mt-3 px-2 space-y-1">
                  <Link href="/login" className="text-gray-600 hover:text-primary block px-3 py-2 rounded-md text-base font-medium">
                    Sign In
                  </Link>
                  <button className="btn-primary w-full mt-2">
                    Get Started
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </nav>
  )
}
