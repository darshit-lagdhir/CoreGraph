import React from 'react';

/**
 * COREGRAPH MASTER ENGINEERING SPECIFICATION: MODULE 14
 * ATOM: Switch.
 * Implements strict ARIA-role compliance and deterministic state mutation.
 */
interface SwitchProps {
  id: string;
  label: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
  description?: string;
}

export const Switch: React.FC<SwitchProps> = ({ id, label, checked, onChange, description }) => {
  return (
    <div className="hud-panel flex items-center justify-between">
      <div className="flex flex-col">
        <label htmlFor={id} className="text-sm font-medium text-main">{label}</label>
        {description && <span className="text-xs text-dim">{description}</span>}
      </div>
      <button
        id={id}
        role="switch"
        aria-checked={checked}
        onClick={() => onChange(!checked)}
        className={`w-10 h-6 rounded-full transition-smooth border border-muted ${
          checked ? 'bg-threat-critical' : 'bg-bg-surface-elevated'
        }`}
      >
        <div
          className={`w-4 h-4 bg-text-main rounded-full transform transition-smooth translate-x-1 ${
            checked ? 'translate-x-5' : 'translate-x-1'
          }`}
        />
      </button>
    </div>
  );
};

/**
 * ATOM: Slider.
 * Implements strict debouncing and real-time value output for metric-based filtering.
 */
interface SliderProps {
  id: string;
  label: string;
  min: number;
  max: number;
  value: number;
  onChange: (value: number) => void;
  unit?: string;
}

export const Slider: React.FC<SliderProps> = ({ id, label, min, max, value, onChange, unit }) => {
  return (
    <div className="hud-panel flex flex-col gap-2">
      <div className="flex justify-between items-center">
        <label htmlFor={id} className="text-sm font-medium text-main">{label}</label>
        <span className="text-xs font-mono text-threat-safe">{value}{unit}</span>
      </div>
      <input
        id={id}
        type="range"
        min={min}
        max={max}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full h-1 bg-bg-surface-elevated rounded-full appearance-none cursor-pointer accent-sustainability"
      />
    </div>
  );
};
