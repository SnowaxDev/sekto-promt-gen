import * as React from "react";
import * as TabsPrimitive from "@radix-ui/react-tabs";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

/* Button */
const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-xl text-sm font-semibold transition-colors focus-visible:outline-none disabled:opacity-50 disabled:pointer-events-none",
  {
    variants: {
      variant: {
        default:
          "text-white shadow-glow bg-gradient-to-br from-bright via-primary to-forest hover:brightness-110",
        ghost: "border border-line bg-white/[0.03] text-ink hover:bg-white/[0.07]",
        subtle: "bg-white/[0.06] text-ink hover:bg-white/[0.1]",
        danger: "border border-red/40 text-red hover:bg-red/10",
      },
      size: { default: "h-10 px-4 py-2", sm: "h-8 px-3 text-xs", icon: "h-9 w-9" },
    },
    defaultVariants: { variant: "default", size: "default" },
  }
);
export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}
export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, ...props }, ref) => (
    <button ref={ref} className={cn(buttonVariants({ variant, size }), className)} {...props} />
  )
);
Button.displayName = "Button";

/* Card */
export const Card = ({ className, ...p }: React.HTMLAttributes<HTMLDivElement>) => (
  <div
    className={cn(
      "rounded-2xl border border-line bg-panel/70 backdrop-blur-sm shadow-[0_1px_0_rgba(255,255,255,0.04)_inset]",
      className
    )}
    {...p}
  />
);
export const CardHeader = ({ className, ...p }: React.HTMLAttributes<HTMLDivElement>) => (
  <div className={cn("p-4 border-b border-line", className)} {...p} />
);
export const CardTitle = ({ className, ...p }: React.HTMLAttributes<HTMLDivElement>) => (
  <div className={cn("text-sm font-semibold tracking-tight", className)} {...p} />
);
export const CardContent = ({ className, ...p }: React.HTMLAttributes<HTMLDivElement>) => (
  <div className={cn("p-4", className)} {...p} />
);

/* Inputs */
export const Input = React.forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(
  ({ className, ...p }, ref) => (
    <input
      ref={ref}
      className={cn(
        "flex h-10 w-full rounded-xl border border-line bg-void/40 px-3 py-2 text-sm text-ink placeholder:text-dim focus-visible:outline-none focus-visible:border-primary",
        className
      )}
      {...p}
    />
  )
);
Input.displayName = "Input";

export const Textarea = React.forwardRef<
  HTMLTextAreaElement,
  React.TextareaHTMLAttributes<HTMLTextAreaElement>
>(({ className, ...p }, ref) => (
  <textarea
    ref={ref}
    className={cn(
      "flex w-full rounded-xl border border-line bg-void/40 px-3 py-2 text-sm text-ink placeholder:text-dim focus-visible:outline-none focus-visible:border-primary font-mono",
      className
    )}
    {...p}
  />
));
Textarea.displayName = "Textarea";

export const Select = React.forwardRef<
  HTMLSelectElement,
  React.SelectHTMLAttributes<HTMLSelectElement>
>(({ className, children, ...p }, ref) => (
  <select
    ref={ref}
    className={cn(
      "flex h-10 w-full rounded-xl border border-line bg-void/40 px-3 py-2 text-sm text-ink focus-visible:outline-none focus-visible:border-primary",
      className
    )}
    {...p}
  >
    {children}
  </select>
));
Select.displayName = "Select";

export const Label = ({ className, ...p }: React.HTMLAttributes<HTMLLabelElement>) => (
  <label className={cn("block text-xs text-dim mb-1 mt-3", className)} {...p} />
);

/* Badge */
export function Badge({
  tone = "muted",
  className,
  ...p
}: React.HTMLAttributes<HTMLSpanElement> & { tone?: "ok" | "bad" | "muted" | "gold" }) {
  const tones = {
    ok: "bg-primary/15 text-blade border-primary/30",
    bad: "bg-red/15 text-red border-red/40",
    muted: "bg-white/[0.06] text-muted border-line",
    gold: "bg-yellow/15 text-yellow border-yellow/30",
  };
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-xs font-medium",
        tones[tone],
        className
      )}
      {...p}
    />
  );
}

/* Tabs (Radix) */
export const Tabs = TabsPrimitive.Root;
export const TabsList = ({
  className,
  ...p
}: React.ComponentPropsWithoutRef<typeof TabsPrimitive.List>) => (
  <TabsPrimitive.List
    className={cn("inline-flex items-center gap-1 rounded-2xl border border-line bg-panel/60 p-1", className)}
    {...p}
  />
);
export const TabsTrigger = ({
  className,
  ...p
}: React.ComponentPropsWithoutRef<typeof TabsPrimitive.Trigger>) => (
  <TabsPrimitive.Trigger
    className={cn(
      "inline-flex items-center gap-2 rounded-xl px-3 py-1.5 text-sm text-muted transition-colors data-[state=active]:bg-forest data-[state=active]:text-white",
      className
    )}
    {...p}
  />
);
export const TabsContent = TabsPrimitive.Content;
