import type { PropsWithChildren, ReactNode } from "react";

type ModuleCardProps = PropsWithChildren<{
  title: string;
  rightSlot?: ReactNode;
  className?: string;
}>;

export function ModuleCard({ title, rightSlot, className = "", children }: ModuleCardProps) {
  return (
    <section className={`rounded-lg border border-slate-700 bg-terminal-panel p-4 shadow-bloomberg ${className}`}>
      <header className="mb-3 flex items-center justify-between border-b border-slate-700 pb-2">
        <h2 className="text-sm font-semibold uppercase tracking-widest text-slate-300">{title}</h2>
        {rightSlot}
      </header>
      {children}
    </section>
  );
}
