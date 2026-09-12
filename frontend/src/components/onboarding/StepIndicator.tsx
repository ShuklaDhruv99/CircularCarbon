interface StepIndicatorProps {
  currentStep: 1 | 2 | 3 | 4;
}

const STEPS = [
  { number: 1, label: "Factory" },
  { number: 2, label: "Production Process" },
  { number: 3, label: "Energy & Materials" },
  { number: 4, label: "Waste" },
] as const;

function statusFor(stepNumber: number, currentStep: number): "current" | "complete" | "upcoming" {
  if (stepNumber === currentStep) return "current";
  if (stepNumber < currentStep) return "complete";
  return "upcoming";
}

const statusClasses: Record<"current" | "complete" | "upcoming", string> = {
  current: "bg-primary text-white",
  complete: "bg-secondary text-white",
  upcoming: "bg-border text-muted",
};

function StepIndicator({ currentStep }: StepIndicatorProps) {
  return (
    <ol className="flex w-full items-center justify-between gap-2">
      {STEPS.map(({ number, label }) => {
        const status = statusFor(number, currentStep);
        return (
          <li
            key={number}
            data-testid={`step-${number}`}
            data-status={status}
            className="flex flex-1 flex-col items-center gap-1 text-center"
          >
            <span
              className={`flex h-8 w-8 items-center justify-center rounded-full text-sm font-semibold ${statusClasses[status]}`}
            >
              {number}
            </span>
            <span className="text-xs font-medium text-text">{label}</span>
          </li>
        );
      })}
    </ol>
  );
}

export default StepIndicator;
