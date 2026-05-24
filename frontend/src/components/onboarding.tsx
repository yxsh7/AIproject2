'use client';

import { useState } from 'react';
import { Button } from './ui/button';

interface OnboardingProps {
  hasProfile: boolean;
  hasIntegrations: boolean;
  hasSyncedData: boolean;
  onGoToProfile: () => void;
  onGoToIntegrations: () => void;
  onDismiss: () => void;
}

export function Onboarding({
  hasProfile,
  hasIntegrations,
  hasSyncedData,
  onGoToProfile,
  onGoToIntegrations,
  onDismiss,
}: OnboardingProps) {
  const [dismissed, setDismissed] = useState(false);

  if (dismissed) return null;

  // Calculate progress
  const steps = [
    { done: hasProfile, label: 'Create Profile' },
    { done: hasIntegrations, label: 'Connect Tools' },
    { done: hasSyncedData, label: 'Sync Data' },
  ];
  const completedSteps = steps.filter((s) => s.done).length;
  const progress = (completedSteps / steps.length) * 100;

  // If all done, don't show
  if (completedSteps === steps.length) return null;

  return (
    <div className="mb-8 p-6 rounded-2xl bg-gradient-to-br from-blue-600/10 to-cyan-600/10 border border-blue-500/20">
      <div className="flex items-start justify-between mb-4">
        <div>
          <h2 className="text-xl font-bold text-white mb-1">Welcome to DevMetrics AI</h2>
          <p className="text-slate-400 text-sm">Complete these steps to start tracking your productivity</p>
        </div>
        <button
          onClick={() => {
            setDismissed(true);
            onDismiss();
          }}
          className="text-slate-400 hover:text-white transition-colors"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      {/* Progress bar */}
      <div className="mb-6">
        <div className="flex justify-between text-xs text-slate-400 mb-2">
          <span>{completedSteps} of {steps.length} completed</span>
          <span>{Math.round(progress)}%</span>
        </div>
        <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-blue-500 to-cyan-500 transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Steps */}
      <div className="space-y-3">
        {/* Step 1: Profile */}
        <div className={`flex items-center gap-4 p-4 rounded-xl ${hasProfile ? 'bg-emerald-500/10 border border-emerald-500/20' : 'bg-slate-800/50 border border-slate-700/50'}`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${hasProfile ? 'bg-emerald-500/20 text-emerald-400' : 'bg-blue-500/20 text-blue-400'}`}>
            {hasProfile ? (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            ) : (
              <span className="text-sm font-bold">1</span>
            )}
          </div>
          <div className="flex-1">
            <h3 className={`font-medium ${hasProfile ? 'text-emerald-400' : 'text-white'}`}>Set Up Your Profile</h3>
            <p className="text-sm text-slate-400">Add your GitHub and Jira usernames</p>
          </div>
          {!hasProfile && (
            <Button
              onClick={onGoToProfile}
              size="sm"
              className="bg-blue-600 hover:bg-blue-500 text-white"
            >
              Set Up
            </Button>
          )}
        </div>

        {/* Step 2: Integrations */}
        <div className={`flex items-center gap-4 p-4 rounded-xl ${hasIntegrations ? 'bg-emerald-500/10 border border-emerald-500/20' : hasProfile ? 'bg-slate-800/50 border border-slate-700/50' : 'bg-slate-800/30 border border-slate-700/30 opacity-60'}`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${hasIntegrations ? 'bg-emerald-500/20 text-emerald-400' : 'bg-blue-500/20 text-blue-400'}`}>
            {hasIntegrations ? (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            ) : (
              <span className="text-sm font-bold">2</span>
            )}
          </div>
          <div className="flex-1">
            <h3 className={`font-medium ${hasIntegrations ? 'text-emerald-400' : 'text-white'}`}>Connect Your Tools</h3>
            <p className="text-sm text-slate-400">Link GitHub and/or Jira accounts</p>
          </div>
          {!hasIntegrations && hasProfile && (
            <Button
              onClick={onGoToIntegrations}
              size="sm"
              className="bg-blue-600 hover:bg-blue-500 text-white"
            >
              Connect
            </Button>
          )}
        </div>

        {/* Step 3: Sync Data */}
        <div className={`flex items-center gap-4 p-4 rounded-xl ${hasSyncedData ? 'bg-emerald-500/10 border border-emerald-500/20' : hasIntegrations ? 'bg-slate-800/50 border border-slate-700/50' : 'bg-slate-800/30 border border-slate-700/30 opacity-60'}`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${hasSyncedData ? 'bg-emerald-500/20 text-emerald-400' : 'bg-blue-500/20 text-blue-400'}`}>
            {hasSyncedData ? (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            ) : (
              <span className="text-sm font-bold">3</span>
            )}
          </div>
          <div className="flex-1">
            <h3 className={`font-medium ${hasSyncedData ? 'text-emerald-400' : 'text-white'}`}>Sync Your Data</h3>
            <p className="text-sm text-slate-400">Pull your commits, PRs, and tickets</p>
          </div>
          {!hasSyncedData && hasIntegrations && (
            <Button
              onClick={onGoToIntegrations}
              size="sm"
              className="bg-blue-600 hover:bg-blue-500 text-white"
            >
              Sync Now
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
