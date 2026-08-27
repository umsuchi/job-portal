import { cn } from '@/lib/cn'

/** Multi-select as a row of toggle chips — used for the candidate's preferences. */
export function CheckboxGroup<T extends string>({
  options, value, onChange,
}: {
  options: Record<string, string>
  value: T[]
  onChange: (next: T[]) => void
}) {
  return (
    <div className="flex flex-wrap gap-2">
      {Object.entries(options).map(([key, label]) => {
        const active = value.includes(key as T)
        return (
          <button
            key={key}
            type="button"
            role="checkbox"
            aria-checked={active}
            onClick={() =>
              onChange(active
                ? value.filter((v) => v !== key)
                : [...value, key as T])
            }
            className={cn(
              'rounded-full border px-3 py-1.5 text-sm transition-colors',
              active
                ? 'border-primary bg-primary text-primary-foreground'
                : 'border-input hover:bg-accent',
            )}
          >
            {label}
          </button>
        )
      })}
    </div>
  )
}
