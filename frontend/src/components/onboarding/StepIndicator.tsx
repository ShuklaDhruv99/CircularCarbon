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

function StepIndicator({ currentStep }: StepIndicatorProps) {
  return (
    <ol className="step-list">
      {STEPS.map(({ number, label }) => {
        const status = statusFor(number, currentStep);
        return (
          <li
            key={number}
            data-testid={`step-${number}`}
            data-status={status}
            className=""
          >
            <span
              className="step-bullet"
            >
              {number}
            </span>
            <span>{label}</span>
          </li>
        );
      })}
    </ol>
  );
}

export default StepIndicator;
