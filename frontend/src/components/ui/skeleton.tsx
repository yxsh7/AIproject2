'use client';

import { cn } from '../../lib/utils';

interface SkeletonProps {
  className?: string;
}

export function Skeleton({ className }: SkeletonProps) {
  return (
    <div
      className={cn(
        'animate-pulse rounded-md bg-slate-700/50',
        className
      )}
    />
  );
}

export function DashboardSkeleton() {
  return (
    <div className="space-y-6 animate-fade-in">
      {/* Score Card Skeleton */}
      <div className="grid md:grid-cols-3 gap-6">
        <div className="md:col-span-1 p-8 rounded-2xl bg-slate-800/30 border border-slate-700/50">
          <Skeleton className="h-4 w-24 mb-4" />
          <Skeleton className="h-16 w-32 mb-2" />
          <Skeleton className="h-3 w-20" />
        </div>
        <div className="md:col-span-2 p-6 rounded-2xl bg-slate-800/30 border border-slate-700/50">
          <Skeleton className="h-5 w-36 mb-4" />
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="p-4 rounded-xl bg-slate-900/50">
                <Skeleton className="h-3 w-16 mb-2" />
                <Skeleton className="h-8 w-12 mb-2" />
                <Skeleton className="h-1.5 w-full" />
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Activity Summary Skeleton */}
      <div className="p-6 rounded-2xl bg-slate-800/30 border border-slate-700/50">
        <Skeleton className="h-5 w-36 mb-4" />
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="p-4 rounded-xl bg-slate-900/50 text-center">
              <Skeleton className="h-8 w-16 mx-auto mb-2" />
              <Skeleton className="h-3 w-20 mx-auto" />
            </div>
          ))}
        </div>
      </div>

      {/* Insights Skeleton */}
      <div className="p-6 rounded-2xl bg-slate-800/30 border border-slate-700/50">
        <Skeleton className="h-5 w-28 mb-4" />
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="p-4 rounded-xl bg-slate-900/50 border border-slate-700/30">
              <Skeleton className="h-4 w-48 mb-2" />
              <Skeleton className="h-3 w-full mb-1" />
              <Skeleton className="h-3 w-3/4" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export function IntegrationsSkeleton() {
  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <Skeleton className="h-7 w-36 mb-2" />
        <Skeleton className="h-4 w-64" />
      </div>
      <div className="grid gap-6">
        {[1, 2].map((i) => (
          <div key={i} className="p-6 rounded-2xl bg-slate-800/30 border border-slate-700/50">
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-4">
                <Skeleton className="w-12 h-12 rounded-xl" />
                <div>
                  <Skeleton className="h-5 w-24 mb-1" />
                  <Skeleton className="h-3 w-32" />
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Skeleton className="h-6 w-16 rounded-full" />
                <Skeleton className="h-9 w-24 rounded-lg" />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function ProfileSkeleton() {
  return (
    <div className="space-y-6 animate-fade-in max-w-lg">
      <div>
        <Skeleton className="h-7 w-48 mb-2" />
        <Skeleton className="h-4 w-72" />
      </div>
      <div className="p-6 rounded-2xl bg-slate-800/30 border border-slate-700/50 space-y-6">
        {[1, 2, 3, 4].map((i) => (
          <div key={i}>
            <Skeleton className="h-4 w-32 mb-2" />
            <Skeleton className="h-10 w-full rounded-md" />
          </div>
        ))}
        <Skeleton className="h-10 w-full rounded-xl" />
      </div>
    </div>
  );
}
