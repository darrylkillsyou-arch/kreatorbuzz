import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import type { Creator } from '../types';
import { api } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';

interface ProposalModalProps {
  creator: Creator;
  onClose: () => void;
}

export const ProposalModal: React.FC<ProposalModalProps> = ({ creator, onClose }) => {
  const { user, login } = useAuth();
  const [projectTitle, setProjectTitle] = useState('');
  const [projectRequirement, setProjectRequirement] = useState('');
  const [budgetInRupees, setBudgetInRupees] = useState<number>(creator.rate_per_day || 25000);
  const [deadline, setDeadline] = useState('7 Days');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isLoggingIn, setIsLoggingIn] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');

  // Reset form whenever creator changes to prevent stale state retention
  useEffect(() => {
    setProjectTitle('');
    setProjectRequirement('');
    setBudgetInRupees(creator.rate_per_day || 25000);
    setDeadline('7 Days');
    setSuccessMessage('');
    setErrorMessage('');
  }, [creator.id, creator.name]);

  const handleQuickLogin = async () => {
    setIsLoggingIn(true);
    setErrorMessage('');
    try {
      await login('recruiter@codexero.com', 'Demo@123');
    } catch {
      try {
        await login('brand@maccall.demo', 'demo1234');
      } catch (err: any) {
        setErrorMessage(err.message || 'Failed to sign in as demo recruiter');
      }
    } finally {
      setIsLoggingIn(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage('');
    setIsSubmitting(true);
    try {
      const numProfileId = creator.profile_id ? Number(creator.profile_id) : (creator.id && !isNaN(Number(creator.id)) ? Number(creator.id) : undefined);
      const numUserId = creator.user_id ? Number(creator.user_id) : undefined;

      await api.proposals.send({
        creator_id: creator.id,
        creator_profile_id: numProfileId,
        creator_user_id: numUserId,
        project_title: projectTitle || `Project with ${creator.name}`,
        project_requirement: projectRequirement,
        budget_in_rupees: Number(budgetInRupees),
        deadline,
      });
      setSuccessMessage(
        'Proposal sent successfully. The creator has received your request. Once they accept it, a workspace will automatically be created.'
      );
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to send proposal. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-inverse-surface/50 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-surface-container-lowest w-full max-w-lg rounded-2xl p-space-lg shadow-2xl border border-outline-variant/40 animate-fade-in space-y-space-md">
        <div className="flex items-center justify-between pb-space-xs border-b border-surface-container">
          <div>
            <span className="font-label-sm text-secondary uppercase tracking-wider font-semibold block">
              Send Hiring Proposal
            </span>
            <h3 className="font-headline-md text-headline-md text-on-surface">
              Proposal for {creator.name}
            </h3>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1 rounded-full text-on-surface-variant hover:bg-surface-container cursor-pointer"
          >
            <span className="material-symbols-outlined text-[20px]">close</span>
          </button>
        </div>

        {successMessage ? (
          <div className="space-y-space-md py-space-sm text-center">
            <div className="w-12 h-12 rounded-full bg-secondary-container/40 text-secondary mx-auto flex items-center justify-center">
              <span className="material-symbols-outlined text-[28px]">task_alt</span>
            </div>
            <p className="font-body-md text-body-md text-on-surface leading-relaxed">
              {successMessage}
            </p>
            <button
              type="button"
              onClick={onClose}
              className="w-full py-2.5 bg-primary text-on-primary font-label-lg rounded-full hover:bg-primary-container transition-all cursor-pointer shadow-sm"
            >
              Close
            </button>
          </div>
        ) : !user ? (
          <div className="space-y-space-md py-space-sm text-center">
            <div className="w-12 h-12 rounded-full bg-surface-container-high text-on-surface-variant mx-auto flex items-center justify-center">
              <span className="material-symbols-outlined text-[28px]">lock</span>
            </div>
            <p className="font-body-md text-on-surface-variant leading-relaxed">
              You must be signed in as a recruiter to send a proposal.
            </p>
            {errorMessage && (
              <div className="p-3 bg-error-container/40 text-on-error-container rounded-lg text-body-sm border border-error/20">
                {errorMessage}
              </div>
            )}
            <button
              type="button"
              onClick={handleQuickLogin}
              disabled={isLoggingIn}
              className="w-full py-2.5 bg-primary text-on-primary font-label-lg rounded-full hover:bg-primary-container transition-all cursor-pointer shadow-sm disabled:opacity-50"
            >
              {isLoggingIn ? 'Signing in…' : 'Sign in as Demo Recruiter'}
            </button>
            <Link
              to="/login"
              onClick={onClose}
              className="block text-secondary font-label-md hover:underline"
            >
              Go to Sign In
            </Link>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-space-md">
            {errorMessage && (
              <div className="p-3 bg-error-container/40 text-on-error-container rounded-lg text-body-sm border border-error/20">
                {errorMessage}
              </div>
            )}

            <div className="space-y-1">
              <label className="font-label-sm text-label-sm uppercase tracking-wider text-on-surface-variant block font-semibold">
                Project Title
              </label>
              <input
                type="text"
                required
                value={projectTitle}
                onChange={(e) => setProjectTitle(e.target.value)}
                placeholder="e.g., Commercial AI Video Campaign"
                className="w-full bg-surface text-on-surface px-4 py-2.5 rounded-lg border border-outline-variant focus:outline-none focus:ring-1 focus:ring-secondary/50 font-body-md"
              />
            </div>

            <div className="space-y-1">
              <label className="font-label-sm text-label-sm uppercase tracking-wider text-on-surface-variant block font-semibold">
                Project Requirement
              </label>
              <textarea
                required
                rows={3}
                value={projectRequirement}
                onChange={(e) => setProjectRequirement(e.target.value)}
                placeholder="Describe your project goals, style requirements, and deliverables..."
                className="w-full bg-surface text-on-surface p-4 rounded-lg border border-outline-variant focus:outline-none focus:ring-1 focus:ring-secondary/50 font-body-md resize-none"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-space-md">
              <div className="space-y-1">
                <label className="font-label-sm text-label-sm uppercase tracking-wider text-on-surface-variant block font-semibold">
                  Budget (in ₹)
                </label>
                <div className="relative flex items-center">
                  <span className="absolute left-3 font-label-lg text-secondary font-bold">₹</span>
                  <input
                    type="number"
                    required
                    min={1000}
                    step={1000}
                    value={budgetInRupees}
                    onChange={(e) => setBudgetInRupees(Number(e.target.value))}
                    className="w-full bg-surface text-on-surface pl-8 pr-4 py-2.5 rounded-lg border border-outline-variant focus:outline-none focus:ring-1 focus:ring-secondary/50 font-body-md"
                  />
                </div>
              </div>

              <div className="space-y-1">
                <label className="font-label-sm text-label-sm uppercase tracking-wider text-on-surface-variant block font-semibold">
                  Deadline
                </label>
                <input
                  type="text"
                  required
                  value={deadline}
                  onChange={(e) => setDeadline(e.target.value)}
                  placeholder="e.g., 5 Business Days"
                  className="w-full bg-surface text-on-surface px-4 py-2.5 rounded-lg border border-outline-variant focus:outline-none focus:ring-1 focus:ring-secondary/50 font-body-md"
                />
              </div>
            </div>

            <div className="pt-space-xs flex items-center justify-end gap-space-sm">
              <button
                type="button"
                onClick={onClose}
                className="px-space-md py-2.5 rounded-full bg-surface-container hover:bg-surface-container-high text-on-surface font-label-md transition-colors cursor-pointer"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isSubmitting}
                className="px-space-lg py-2.5 bg-primary text-on-primary font-label-lg rounded-full hover:bg-primary-container transition-all cursor-pointer shadow-sm disabled:opacity-50"
              >
                {isSubmitting ? 'Sending...' : 'Send Proposal'}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};
