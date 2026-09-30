import React from 'react';
import type { NotificationToast as ToastType } from '../../types';
import { ShieldAlert, Zap, Info, X } from 'lucide-react';
import { formatTimestamp } from '../../utils/formatters';

interface NotificationToastContainerProps {
  toasts: ToastType[];
  onDismiss: (id: string) => void;
}

export const NotificationToastContainer: React.FC<NotificationToastContainerProps> = ({
  toasts,
  onDismiss,
}) => {
  if (toasts.length === 0) return null;

  return (
    <div
      aria-live="polite"
      aria-label="Real-time alert notifications"
      className="fixed bottom-6 right-6 z-50 flex flex-col gap-3 max-w-sm w-full pointer-events-none"
    >
      {toasts.map((toast) => {
        let borderClass = 'border-slate-700 bg-slate-900/90 text-slate-100';
        let icon = <Info className="w-4 h-4 text-cyan-400 shrink-0" />;

        if (toast.type === 'ALERT') {
          borderClass = 'border-rose-700/80 bg-rose-950/90 text-rose-100 shadow-[0_0_20px_-3px_rgba(244,63,94,0.4)]';
          icon = <ShieldAlert className="w-4 h-4 text-rose-400 shrink-0" />;
        } else if (toast.type === 'FORECAST') {
          borderClass = 'border-cyan-700/80 bg-cyan-950/90 text-cyan-100 shadow-[0_0_20px_-3px_rgba(6,182,212,0.4)]';
          icon = <Zap className="w-4 h-4 text-cyan-400 shrink-0" />;
        }

        return (
          <div
            key={toast.id}
            className={`pointer-events-auto rounded-lg p-3.5 border backdrop-blur-md transition-all duration-300 transform translate-y-0 opacity-100 flex items-start gap-3 text-xs font-mono ${borderClass}`}
          >
            <div className="mt-0.5">{icon}</div>

            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between gap-2">
                <span className="font-bold tracking-wider uppercase text-[11px]">
                  {toast.title}
                </span>
                <span className="text-[10px] text-slate-400">
                  {formatTimestamp(toast.timestamp)}
                </span>
              </div>
              <p className="mt-1 text-slate-300 leading-relaxed break-words font-sans text-xs">
                {toast.message}
              </p>
              {toast.incidentId && (
                <div className="mt-1.5 text-[10px] text-slate-400">
                  Ref: <span className="text-cyan-300">{toast.incidentId}</span>
                </div>
              )}
            </div>

            <button
              onClick={() => onDismiss(toast.id)}
              className="text-slate-400 hover:text-white transition-colors shrink-0 p-0.5"
              aria-label="Dismiss notification"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        );
      })}
    </div>
  );
};
