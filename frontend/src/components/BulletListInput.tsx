import { Button, Input } from '@/components/ui'

/**
 * One-line-per-item editor for the job post's bullet sections.
 *
 * Backed by a plain string[], with a trailing blank row so there is always
 * somewhere to type. Blank rows are stripped on change, so the caller never
 * sees them.
 */
export function BulletListInput({
  value, onChange, placeholder, addLabel = 'Add another',
}: {
  value: string[]
  onChange: (next: string[]) => void
  placeholder?: string
  addLabel?: string
}) {
  const rows = value.length ? value : ['']

  function update(index: number, text: string) {
    const next = [...rows]
    next[index] = text
    onChange(next.filter((line, i) => line.trim() || i === next.length - 1))
  }

  return (
    <div className="space-y-2">
      {rows.map((line, index) => (
        <div key={index} className="flex gap-2">
          <Input
            value={line}
            placeholder={placeholder}
            onChange={(e) => update(index, e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault()
                onChange([...rows.filter((l) => l.trim()), ''])
              }
            }}
          />
          <Button
            type="button"
            variant="ghost"
            size="icon"
            aria-label={`Remove item ${index + 1}`}
            disabled={rows.length === 1 && !line}
            onClick={() => onChange(rows.filter((_, i) => i !== index))}
          >
            ×
          </Button>
        </div>
      ))}
      <Button
        type="button" variant="outline" size="sm"
        onClick={() => onChange([...rows.filter((l) => l.trim()), ''])}
      >
        {addLabel}
      </Button>
    </div>
  )
}
