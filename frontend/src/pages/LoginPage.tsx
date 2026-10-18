import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { BrandMark } from '../components/BrandMark';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [email, setEmail] = useState('recruiter@codexero.com');
  const [password, setPassword] = useState('Demo@123');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    try {
      await login(email, password);
      const stored = localStorage.getItem('codexero_user');
      const parsed = stored ? JSON.parse(stored) : null;
      if (parsed && parsed.role === 'creator') {
        navigate('/requests');
      } else {
        navigate('/discover');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to sign in');
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickFill = (demoEmail: string, demoPass: string) => {
    setEmail(demoEmail);
    setPassword(demoPass);
    setError('');
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center px-gutter py-space-xl">
      <div className="max-w-md w-full bg-surface-container-low rounded-2xl p-space-lg md:p-space-xl border border-outline-variant/40 shadow-sm space-y-space-md">
        <div className="text-center space-y-space-xs">
          <div className="flex justify-center">
            <BrandMark size="lg" />
          </div>
          <h1 className="font-headline-md text-headline-md text-on-surface">
            Sign in to CODE XERO
          </h1>
          <p className="font-body-sm text-body-sm text-on-surface-variant">
            Enter your email and password to access workspaces and projects.
          </p>

          {/* Demo Accounts — Password: Demo@123 */}
          <div className="pt-2 space-y-1.5">
            <p className="font-label-sm text-label-sm uppercase tracking-wider text-on-surface-variant">
              Demo accounts — Password: Demo@123
            </p>
            <div className="flex flex-wrap justify-center gap-2">
              <button
                type="button"
                onClick={() => handleQuickFill('recruiter@codexero.com', 'Demo@123')}
                className="px-2.5 py-1 text-xs rounded-full bg-secondary/10 hover:bg-secondary/20 text-secondary font-semibold transition-colors cursor-pointer border border-secondary/30"
              >
                Demo Recruiter
              </button>
              <button
                type="button"
                onClick={() => handleQuickFill('creator@codexero.com', 'Demo@123')}
                className="px-2.5 py-1 text-xs rounded-full bg-secondary/10 hover:bg-secondary/20 text-secondary font-semibold transition-colors cursor-pointer border border-secondary/30"
              >
                Demo Content Creator
              </button>
            </div>
            <div className="flex flex-wrap justify-center gap-2 pt-0.5">
              <button
                type="button"
                onClick={() => handleQuickFill('cleanrecruiter@codexero.com', 'Demo@123')}
                className="px-2.5 py-1 text-xs rounded-full bg-surface-container-high hover:bg-surface-container-highest text-on-surface-variant transition-colors cursor-pointer"
              >
                Clean Recruiter
              </button>
              <button
                type="button"
                onClick={() => handleQuickFill('cleancreator@codexero.com', 'Demo@123')}
                className="px-2.5 py-1 text-xs rounded-full bg-surface-container-high hover:bg-surface-container-highest text-on-surface-variant transition-colors cursor-pointer"
              >
                Clean Creator
              </button>
            </div>
          </div>
        </div>

        {error && (
          <div className="p-3 bg-error-container/40 text-on-error-container rounded-lg text-body-sm border border-error/20">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-space-md">
          <div className="space-y-1">
            <label className="font-label-sm text-label-sm uppercase tracking-wider text-on-surface-variant block">
              Email Address
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@studio.com"
              className="w-full bg-surface text-on-surface px-4 py-2.5 rounded-lg border border-outline-variant focus:outline-none focus:ring-1 focus:ring-secondary/50 font-body-md"
            />
          </div>

          <div className="space-y-1">
            <div className="flex items-center justify-between">
              <label className="font-label-sm text-label-sm uppercase tracking-wider text-on-surface-variant block">
                Password
              </label>
              <a href="#" className="font-label-sm text-secondary hover:underline">
                Forgot?
              </a>
            </div>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full bg-surface text-on-surface px-4 py-2.5 rounded-lg border border-outline-variant focus:outline-none focus:ring-1 focus:ring-secondary/50 font-body-md"
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-3 bg-primary text-on-primary font-label-lg text-label-lg rounded-full hover:bg-primary-container hover:text-on-surface transition-all shadow-sm cursor-pointer disabled:opacity-50"
          >
            {isLoading ? 'Signing in...' : 'Sign in'}
          </button>
        </form>

        <div className="text-center pt-space-xs border-t border-surface-container-high">
          <span className="font-body-sm text-body-sm text-on-surface-variant">
            Don't have an account?{' '}
          </span>
          <Link to="/register" className="font-label-md text-secondary hover:underline">
            Create Your Account
          </Link>
        </div>
      </div>
    </div>
  );
};
