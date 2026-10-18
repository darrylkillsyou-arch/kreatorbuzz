import React, { useState, useEffect } from 'react';
import { NavLink, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import { BrandMark } from './BrandMark';
import { api } from '../lib/api';
import type { AppNotification } from '../types';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const [showSearchModal, setShowSearchModal] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [notifications, setNotifications] = useState<AppNotification[]>([]);

  useEffect(() => {
    if (user) {
      loadNotifications();
      // Periodically refresh notifications every 15 seconds
      const interval = setInterval(loadNotifications, 15000);
      return () => clearInterval(interval);
    }
  }, [user]);

  const loadNotifications = async () => {
    try {
      const data = await api.notifications.list();
      setNotifications(data);
    } catch {
      // ignore
    }
  };

  const handleMarkAllRead = async () => {
    await api.notifications.markAllRead();
    setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
  };

  const unreadCount = notifications.filter((n) => !n.is_read).length;

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      setShowSearchModal(false);
      navigate(`/discover?search=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  const roleLabel =
    user?.role === 'brand'
      ? 'Recruiter'
      : user?.role === 'creator' || user?.role === 'director'
      ? 'Content Creator'
      : user?.role;

  const navItemClass = ({ isActive }: { isActive: boolean }) =>
    isActive
      ? 'font-label-lg transition-colors text-on-surface bg-surface-container-high px-space-sm py-1.5 rounded-full'
      : 'font-label-lg text-label-lg text-on-surface-variant hover:text-on-surface transition-colors';

  return (
    <>
      <header className="fixed top-0 w-full z-50 bg-surface/90 backdrop-blur-md shadow-[0_1px_8px_rgba(0,0,0,0.04)]">
        <div className="h-20 max-w-7xl mx-auto px-gutter flex items-center justify-between gap-space-md">
          {/* Logo & Navigation */}
          <div className="flex items-center gap-space-lg">
            <Link className="flex items-center gap-space-xs group" to="/discover">
              <BrandMark markClassName="group-hover:scale-105 transition-transform" />
            </Link>

            <nav className="hidden lg:flex items-center gap-space-md">
              <NavLink to="/discover" className={navItemClass}>
                Discover
              </NavLink>
              <NavLink to="/community" className={navItemClass}>
                Community
              </NavLink>
              <NavLink to="/briefs" className={navItemClass}>
                AI Project Assistant
              </NavLink>
              <NavLink to="/workspaces" className={navItemClass}>
                Workspaces
              </NavLink>
              {user?.role === 'creator' && (
                <NavLink to="/requests" className={navItemClass}>
                  Project Requests
                </NavLink>
              )}
              <NavLink to="/leaderboard" className={navItemClass}>
                Leaderboard
              </NavLink>
            </nav>
          </div>

          {/* Actions & User state */}
          <div className="flex items-center gap-space-sm">
            <button
              aria-label="Search creators and projects"
              className="w-9 h-9 rounded-full flex items-center justify-center text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-colors cursor-pointer"
              type="button"
              onClick={() => setShowSearchModal(true)}
            >
              <span className="material-symbols-outlined text-[20px]">search</span>
            </button>

            {/* Theme Toggle */}
            <button
              aria-label={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
              title={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
              className="w-9 h-9 rounded-full flex items-center justify-center text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-colors cursor-pointer"
              type="button"
              onClick={toggleTheme}
            >
              <span className="material-symbols-outlined text-[20px]">
                {theme === 'dark' ? 'light_mode' : 'dark_mode'}
              </span>
            </button>

            <Link
              to="/saved-creators"
              aria-label="Saved Creators"
              title="Saved Creators"
              className="relative w-9 h-9 rounded-full flex items-center justify-center text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-colors"
            >
              <span className="material-symbols-outlined text-[20px]">bookmark</span>
            </Link>

            {/* Notifications Popover */}
            <div className="relative">
              <button
                aria-label="Notifications"
                onClick={() => setShowNotifications(!showNotifications)}
                className="relative w-9 h-9 rounded-full flex items-center justify-center text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-colors cursor-pointer"
                type="button"
              >
                <span className="material-symbols-outlined text-[20px]">notifications</span>
                {unreadCount > 0 && (
                  <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-secondary"></span>
                )}
              </button>

              {showNotifications && (
                <div className="absolute right-0 mt-2 w-80 sm:w-96 bg-surface-container-lowest border border-outline-variant/50 rounded-2xl shadow-xl py-2 z-50 animate-fade-in">
                  <div className="flex items-center justify-between px-4 py-2 border-b border-surface-container">
                    <span className="font-label-md text-on-surface font-semibold">Notifications</span>
                    {unreadCount > 0 && (
                      <button
                        onClick={handleMarkAllRead}
                        className="font-label-sm text-xs text-secondary hover:underline cursor-pointer"
                      >
                        Mark all as read
                      </button>
                    )}
                  </div>

                  <div className="max-h-80 overflow-y-auto divide-y divide-surface-container/60">
                    {notifications.length === 0 ? (
                      <div className="p-6 text-center text-on-surface-variant text-body-sm">
                        No notifications yet.
                      </div>
                    ) : (
                      notifications.map((n) => (
                        <div
                          key={n.id}
                          onClick={() => {
                            setShowNotifications(false);
                            if (n.link) navigate(n.link);
                          }}
                          className={`p-3.5 hover:bg-surface-container cursor-pointer transition-colors ${
                            !n.is_read ? 'bg-secondary/5' : ''
                          }`}
                        >
                          <div className="flex items-start gap-2.5">
                            <span
                              className={`material-symbols-outlined text-[18px] mt-0.5 ${
                                n.type === 'proposal_accepted'
                                  ? 'text-secondary'
                                  : n.type === 'proposal_declined'
                                  ? 'text-error'
                                  : 'text-primary'
                              }`}
                            >
                              {n.type === 'proposal_accepted'
                                ? 'check_circle'
                                : n.type === 'proposal_declined'
                                ? 'cancel'
                                : 'mail'}
                            </span>
                            <div className="flex-1 min-w-0">
                              <p className="font-label-md text-on-surface font-medium text-xs">
                                {n.title}
                              </p>
                              <p className="font-body-sm text-xs text-on-surface-variant mt-0.5 leading-relaxed">
                                {n.message}
                              </p>
                              <span className="font-label-sm text-[10px] text-on-surface-variant/70 block mt-1">
                                {new Date(n.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                              </span>
                            </div>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              )}
            </div>

            {user ? (
              <div className="relative">
                <button
                  onClick={() => setShowUserMenu(!showUserMenu)}
                  className="flex items-center gap-2 pl-2 cursor-pointer"
                >
                  <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-on-primary font-label-md">
                    {user.name ? user.name[0].toUpperCase() : 'U'}
                  </div>
                  <span className="hidden sm:inline font-label-md text-on-surface max-w-[120px] truncate">
                    {user.name}
                  </span>
                </button>

                {showUserMenu && (
                  <div className="absolute right-0 mt-2 w-48 bg-surface-container-lowest border border-outline-variant/50 rounded-lg shadow-lg py-1 z-50">
                    <div className="px-4 py-2 border-b border-surface-container">
                      <p className="font-label-md text-on-surface font-semibold truncate">{user.name}</p>
                      <p className="font-label-sm text-on-surface-variant uppercase">{roleLabel}</p>
                    </div>
                    {user?.role === 'creator' && (
                      <Link
                        to="/requests"
                        onClick={() => setShowUserMenu(false)}
                        className="block px-4 py-2 text-body-sm text-on-surface hover:bg-surface-container transition-colors"
                      >
                        Project Requests
                      </Link>
                    )}
                    <Link
                      to="/workspaces"
                      onClick={() => setShowUserMenu(false)}
                      className="block px-4 py-2 text-body-sm text-on-surface hover:bg-surface-container transition-colors"
                    >
                      My Workspaces
                    </Link>
                    <button
                      onClick={() => {
                        setShowUserMenu(false);
                        logout();
                      }}
                      className="w-full text-left px-4 py-2 text-body-sm text-error hover:bg-error-container/20 transition-colors"
                    >
                      Sign Out
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <div className="hidden sm:flex items-center gap-space-sm ml-space-xs">
                <Link
                  className="px-space-md py-2 font-label-lg text-label-lg text-on-surface-variant hover:text-on-surface transition-colors"
                  to="/login"
                >
                  Sign in
                </Link>
                <Link
                  className="px-space-md py-2 bg-primary text-on-primary font-label-lg text-label-lg rounded-full hover:bg-primary-container hover:text-on-surface transition-all"
                  to="/register"
                >
                  Get started
                </Link>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Quick Search Modal */}
      {showSearchModal && (
        <div className="fixed inset-0 z-50 bg-inverse-surface/40 backdrop-blur-sm flex items-start justify-center pt-28 px-4">
          <div className="bg-surface-container-lowest w-full max-w-2xl rounded-2xl p-space-md shadow-2xl border border-outline-variant/40 animate-fade-in">
            <form onSubmit={handleSearchSubmit} className="flex items-center gap-space-sm">
              <span className="material-symbols-outlined text-secondary text-[24px]">search</span>
              <input
                autoFocus
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search creators, styles, videos, fashion..."
                className="w-full bg-transparent border-0 outline-none font-body-lg text-on-surface placeholder:text-outline"
              />
              <button
                type="button"
                onClick={() => setShowSearchModal(false)}
                className="p-1 rounded-full text-on-surface-variant hover:bg-surface-container"
              >
                <span className="material-symbols-outlined text-[20px]">close</span>
              </button>
            </form>
          </div>
        </div>
      )}
    </>
  );
};
