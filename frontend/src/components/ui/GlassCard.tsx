import * as React from "react";

interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  className?: string;
}

const GlassCard = React.forwardRef<HTMLDivElement, GlassCardProps>(({ className = '', children, ...props }, ref) => (
  <div
    ref={ref}
    className={`glass fade-in-up ${className}`.trim()}
    {...props}
  >
    {children}
  </div>
));
GlassCard.displayName = "GlassCard";
export { GlassCard }; 