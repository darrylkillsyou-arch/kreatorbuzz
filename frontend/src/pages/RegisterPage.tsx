import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { BrandMark } from '../components/BrandMark';

export const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const { register } = useAuth();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [company, setCompany] = useState('');
  const [role, setRole] = useState<'brand' | 'creator'>('brand');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    try {
      await register({ name, email, password: password || 'demo1234', role, company });
      const stored = localStorage.getItem('codexero_user');
      const parsed = stored ? JSON.parse(stored) : null;
      if (parsed && parsed.role === 'creator') {
        navigate('/requests');
      } else {
        navigate('/discover');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to create account');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-[85vh] flex items-center justify-center px-gutter py-space-xl">
      <div className="max-w-lg w-full bg-surface-container-low rounded-2xl p-space-lg md:p-space-xl border border-outline-variant/40 shadow-sm space-y-space-md">
        <div className="text-center space-y-space-xs">
          <div className="flex justify-center">
            <BrandMark size="lg" />
          </div>
          <h1 className="font-headline-md text-headline-md text-on-surface">
            Create Your Account
          </h1>
          <p className="font-body-sm text-body-sm text-on-surface-variant">
            Join the marketplace to hire AI content creators or showcase your work.
          </p>
        </div>

        {error && (
          <div className="p-3 bg-error-container/40 text-on-error-container rounded-lg text-body-sm border border-error/20">
            {error}
          </div>
        )}

        <div className="space-y-2">
          <div className="grid grid-cols-2 gap-2 p-1 bg-surface-container rounded-xl">
            <button
              type="button"
              onClick={() => setRole('brand')}
              className={`py-2 px-3 rounded-lg font-label-md text-label-md transition-all cursor-pointer ${
                role === 'brand'
                  ? 'bg-primary text-on-primary shadow-sm'
                  : 'text-on-surface-variant hover:text-on-surface'
              }`}
            >
              Recruiter / Client
            </button>
            <button
              type="button"
              onClick={() => setRole('creator')}
              className={`py-2 px-3 rounded-lg font-label-md text-label-md transition-all cursor-pointer ${
                role === 'creator'
                  ? 'bg-primary text-on-primary shadow-sm'
                  : 'text-on-surface-variant hover:text-on-surface'
              }`}
            >
              Content Creator
            </button>
          </div>
          <p className="font-body-sm text-body-sm text-on-surface-variant px-1">
            {role === 'brand'
              ? 'I want to find and hire AI content creators.'
              : 'I create AI images, videos, designs or other digital content.'}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-space-sm">
          <div className="space-y-1">
            <label className="font-label-sm text-label-sm uppercase tracking-wider text-on-surface-variant block">
              Full Name
            </label>
            <input
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g., Alexandra Vance"
              className="w-full bg-surface text-on-surface px-4 py-2.5 rounded-lg border border-outline-variant focus:outline-none focus:ring-1 focus:ring-secondary/50 font-body-md"
            />
          </div>

          <div className="space-y-1">
            <label className="font-label-sm text-label-sm uppercase tracking-wider text-on-surface-variant block">
              Email Address
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="alexandra@studio.com"
              className="w-full bg-surface text-on-surface px-4 py-2.5 rounded-lg border border-outline-variant focus:outline-none focus:ring-1 focus:ring-secondary/50 font-body-md"
            />
          </div>

          <div className="space-y-1">
            <label className="font-label-sm text-label-sm uppercase tracking-wider text-on-surface-variant block">
              Password
            </label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full bg-surface text-on-surface px-4 py-2.5 rounded-lg border border-outline-variant focus:outline-none focus:ring-1 focus:ring-secondary/50 font-body-md"
            />
          </div>

          <div className="space-y-1">
            <label className="font-label-sm text-label-sm uppercase tracking-wider text-on-surface-variant block">
              Organization / Studio Name
            </label>
            <input
              type="text"
              value={company}
              onChange={(e) => setCompany(e.target.value)}
              placeholder="e.g., Monolith Heritage Studio"
              className="w-full bg-surface text-on-surface px-4 py-2.5 rounded-lg border border-outline-variant focus:outline-none focus:ring-1 focus:ring-secondary/50 font-body-md"
            />
          </div>

          <div className="pt-space-xs">
            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3 bg-primary text-on-primary font-label-lg text-label-lg rounded-full hover:bg-primary-container hover:text-on-surface transition-all shadow-sm cursor-pointer disabled:opacity-50"
            >
              {isLoading ? 'Creating Account...' : 'Create Account'}
            </button>
          </div>
        </form>

        <div className="text-center pt-space-xs border-t border-surface-container-high">
          <span className="font-body-sm text-body-sm text-on-surface-variant">
            Already have an active account?{' '}
          </span>
          <Link to="/login" className="font-label-md text-secondary hover:underline">
            Sign in
          </Link>
        </div>
      </div>
    </div>
  );
};
