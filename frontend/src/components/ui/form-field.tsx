// Shared form field components used across dashboard pages.

export function Field({
  label, value, onChange, opts = {},
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  opts?: { placeholder?: string; type?: string; disabled?: boolean; hint?: string; required?: boolean };
}) {
  return (
    <div>
      <label style={{ display: 'block', fontSize: 11, color: 'var(--txt-3)', marginBottom: 6 }}>
        {label}
      </label>
      <input
        className="dm-input"
        type={opts.type || 'text'}
        value={value}
        onChange={e => onChange(e.target.value)}
        placeholder={opts.placeholder || ''}
        disabled={opts.disabled}
        required={opts.required}
      />
      {opts.hint && (
        <p style={{ marginTop: 5, fontSize: 10, color: 'var(--txt-3)', fontFamily: 'var(--font-mono)' }}>
          {opts.hint}
        </p>
      )}
    </div>
  );
}

export function TextareaField({
  label, value, onChange, placeholder,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
}) {
  return (
    <div>
      <label style={{ display: 'block', fontSize: 11, color: 'var(--txt-3)', marginBottom: 6 }}>
        {label}
      </label>
      <textarea
        className="dm-input"
        value={value}
        onChange={e => onChange(e.target.value)}
        placeholder={placeholder || ''}
        rows={3}
        style={{ resize: 'vertical', minHeight: 72, fontFamily: 'var(--font-body)', lineHeight: 1.6 }}
      />
    </div>
  );
}

export function SelectField({
  label, value, onChange, options,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  options: readonly string[];
}) {
  return (
    <div>
      <label style={{ display: 'block', fontSize: 11, color: 'var(--txt-3)', marginBottom: 6 }}>
        {label}
      </label>
      <select
        className="dm-input"
        value={value}
        onChange={e => onChange(e.target.value)}
        style={{ cursor: 'pointer' }}
      >
        {options.map(opt => (
          <option key={opt} value={opt} style={{ background: 'var(--surf-1)', color: 'var(--txt-1)' }}>
            {opt.charAt(0).toUpperCase() + opt.slice(1)}
          </option>
        ))}
      </select>
    </div>
  );
}
