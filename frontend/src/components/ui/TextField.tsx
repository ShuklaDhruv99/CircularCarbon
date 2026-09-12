interface TextFieldProps {
  label: string;
  name: string;
  value: string;
  onChange: (value: string) => void;
  type?: "text" | "number";
  required?: boolean;
  error?: string;
  placeholder?: string;
  helpText?: string;
}

function TextField({
  label,
  name,
  value,
  onChange,
  type = "text",
  required = false,
  error,
  placeholder,
  helpText,
}: TextFieldProps) {
  return (
    <div className="flex flex-col gap-1">
      <label htmlFor={name} className="text-sm font-medium text-text">
        {label}
        {required && <span className="text-danger"> *</span>}
      </label>
      <input
        id={name}
        name={name}
        type={type}
        value={value}
        placeholder={placeholder}
        onChange={(e) => onChange(e.target.value)}
        className={`rounded-md border px-3 py-2 text-sm text-text focus:outline-none focus:ring-2 focus:ring-secondary ${
          error ? "border-danger" : "border-border"
        }`}
      />
      {error ? (
        <p className="text-xs text-danger">{error}</p>
      ) : helpText ? (
        <p className="text-xs text-muted">{helpText}</p>
      ) : null}
    </div>
  );
}

export default TextField;
