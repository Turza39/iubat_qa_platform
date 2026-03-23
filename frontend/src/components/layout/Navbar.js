'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import Button from '@/components/ui/Button';
import VerificationBadge from '@/components/common/VerificationBadge';
import { LogOut, User, PenSquare, Menu, X } from 'lucide-react';
import { useState } from 'react';

export default function Navbar() {
  const { user, logout }          = useAuth();
  const router                    = useRouter();
  const [menuOpen, setMenuOpen]   = useState(false);

  const handleLogout = () => {
    logout();
    router.push('/');
    setMenuOpen(false);
  };

  return (
    <nav className="sticky top-0 z-50 bg-white border-b border-slate-200 shadow-sm">
      <div className="max-w-5xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">

          {/* Logo */}
          <Link
            href="/"
            className="text-lg font-bold text-blue-600 hover:text-blue-700 transition-colors"
          >
            IUBAT Q&A
          </Link>

          {/* Desktop Nav */}
          <div className="hidden md:flex items-center gap-3">
            {user ? (
              <>
                <VerificationBadge status={user.verification_status} />
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => router.push('/ask')}
                >
                  <PenSquare size={15} />
                  Ask Question
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => router.push('/profile')}
                >
                  <User size={15} />
                  {user.username}
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleLogout}
                >
                  <LogOut size={15} />
                  Logout
                </Button>
              </>
            ) : (
              <>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => router.push('/login')}
                >
                  Login
                </Button>
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => router.push('/register')}
                >
                  Register
                </Button>
              </>
            )}
          </div>

          {/* Mobile Menu Toggle */}
          <button
            className="md:hidden p-2 rounded-lg text-slate-500 hover:bg-slate-100"
            onClick={() => setMenuOpen(!menuOpen)}
          >
            {menuOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>

        {/* Mobile Menu */}
        {menuOpen && (
          <div className="md:hidden py-3 border-t border-slate-100 flex flex-col gap-2">
            {user ? (
              <>
                <div className="px-2 py-1">
                  <VerificationBadge status={user.verification_status} />
                </div>
                <button
                  onClick={() => { router.push('/ask'); setMenuOpen(false); }}
                  className="text-left px-3 py-2 text-sm rounded-lg hover:bg-slate-100 text-slate-700"
                >
                  Ask Question
                </button>
                <button
                  onClick={() => { router.push('/profile'); setMenuOpen(false); }}
                  className="text-left px-3 py-2 text-sm rounded-lg hover:bg-slate-100 text-slate-700"
                >
                  Profile
                </button>
                <button
                  onClick={handleLogout}
                  className="text-left px-3 py-2 text-sm rounded-lg hover:bg-slate-100 text-red-500"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <button
                  onClick={() => { router.push('/login'); setMenuOpen(false); }}
                  className="text-left px-3 py-2 text-sm rounded-lg hover:bg-slate-100 text-slate-700"
                >
                  Login
                </button>
                <button
                  onClick={() => { router.push('/register'); setMenuOpen(false); }}
                  className="text-left px-3 py-2 text-sm rounded-lg hover:bg-slate-100 text-blue-600 font-medium"
                >
                  Register
                </button>
              </>
            )}
          </div>
        )}
      </div>
    </nav>
  );
}