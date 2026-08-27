import * as React from 'react'
import { Badge, Input } from '@/components/ui'
import { cn } from '@/lib/cn'
import { canonicalize, normalize, searchSkills, type SkillEntry } from '@/lib/skills'

/* ------------------------------------------------------------------ shared */

/** The dropdown itself — shared by the tag input and the single-value filter. */
function SuggestionList({
  id, options, activeIndex, onPick, onHover,
}: {
  id: string
  options: SkillEntry[]
  activeIndex: number
  onPick: (entry: SkillEntry) => void
  onHover: (index: number) => void
}) {
  return (
    <ul
      id={id}
      role="listbox"
      className="absolute z-30 mt-1 max-h-64 w-full overflow-y-auto rounded-md border border-border bg-card py-1 shadow-lg"
    >
      {options.map((entry, index) => (
        <li
          key={entry.name}
          id={`${id}-opt-${index}`}
          role="option"
          aria-selected={index === activeIndex}
          onMouseEnter={() => onHover(index)}
          // mousedown, not click: the input's blur would close the list first.
          onMouseDown={(e) => { e.preventDefault(); onPick(entry) }}
          className={cn(
            'flex cursor-pointer items-center justify-between gap-3 px-3 py-1.5 text-sm',
            index === activeIndex ? 'bg-accent text-accent-foreground' : '',
          )}
        >
          <span>{entry.name}</span>
          <span className="shrink-0 text-xs text-muted-foreground">{entry.category}</span>
        </li>
      ))}
    </ul>
  )
}

/** Shared keyboard/open/highlight logic for both inputs below. */
function useSuggestions(draft: string, exclude: string[], limit = 8) {
  const [open, setOpen] = React.useState(false)
  const [activeIndex, setActiveIndex] = React.useState(0)

  // Derived during render rather than in an effect — no extra pass, never stale.
  const options = React.useMemo(
    () => searchSkills(draft, { exclude, limit }),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [draft, exclude.join('|'), limit],
  )

  const clamped = Math.min(activeIndex, Math.max(0, options.length - 1))

  return {
    open: open && options.length > 0,
    setOpen,
    options,
    activeIndex: clamped,
    setActiveIndex,
    move(delta: number) {
      setOpen(true)
      setActiveIndex((i) => {
        if (!options.length) return 0
        const next = Math.min(i, options.length - 1) + delta
        return (next + options.length) % options.length
      })
    },
  }
}

/* --------------------------------------------------------------- tag input */

/**
 * Multi-skill tag entry with autocomplete.
 *
 * Suggestions come from the catalogue, but typing something not in it and
 * pressing Enter still works — skills are free-text by design (spec §18). What
 * the catalogue buys us is consistent spelling: picking "PostgreSQL" from the
 * list rather than typing "postgres" is what makes the array-overlap match in
 * the suggestion engine fire.
 */
export function SkillInput({
  value, onChange, placeholder = 'Type a skill, e.g. React',
}: {
  value: string[]
  onChange: (next: string[]) => void
  placeholder?: string
}) {
  const [draft, setDraft] = React.useState('')
  const listId = React.useId()
  const { open, setOpen, options, activeIndex, setActiveIndex, move } =
    useSuggestions(draft, value)

  const add = React.useCallback(
    (raw: string) => {
      const parts = raw.split(',').map((part) => canonicalize(part)).filter(Boolean)
      if (!parts.length) return
      const seen = new Set(value.map(normalize))
      const next = [...value]
      for (const part of parts) {
        if (seen.has(normalize(part))) continue
        seen.add(normalize(part))
        next.push(part)
      }
      onChange(next)
      setDraft('')
      setActiveIndex(0)
    },
    [value, onChange, setActiveIndex],
  )

  function onKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault()
        move(1)
        break
      case 'ArrowUp':
        e.preventDefault()
        move(-1)
        break
      case 'Enter':
      case ',':
        e.preventDefault()
        if (open && options[activeIndex]) add(options[activeIndex].name)
        else add(draft)
        break
      case 'Escape':
        setOpen(false)
        break
      case 'Backspace':
        if (!draft && value.length) onChange(value.slice(0, -1))
        break
      default:
        break
    }
  }

  return (
    <div>
      {value.length > 0 ? (
        <div className="flex flex-wrap gap-1.5 pb-2">
          {value.map((skill) => (
            <Badge key={skill} tone="accent" className="gap-1">
              {skill}
              <button
                type="button"
                aria-label={`Remove ${skill}`}
                className="ml-0.5 rounded-full px-1 leading-none hover:bg-black/10"
                onClick={() => onChange(value.filter((s) => s !== skill))}
              >
                ×
              </button>
            </Badge>
          ))}
        </div>
      ) : null}

      <div className="relative">
        <Input
          role="combobox"
          aria-expanded={open}
          aria-controls={listId}
          aria-autocomplete="list"
          aria-activedescendant={open ? `${listId}-opt-${activeIndex}` : undefined}
          autoComplete="off"
          value={draft}
          placeholder={placeholder}
          onChange={(e) => { setDraft(e.target.value); setOpen(true); setActiveIndex(0) }}
          onFocus={() => setOpen(true)}
          onBlur={() => { setOpen(false); add(draft) }}
          onKeyDown={onKeyDown}
        />
        {open ? (
          <SuggestionList
            id={listId}
            options={options}
            activeIndex={activeIndex}
            onPick={(entry) => add(entry.name)}
            onHover={setActiveIndex}
          />
        ) : null}
      </div>

      <p className="mt-1 text-xs text-muted-foreground">
        Pick from the list, or type your own and press Enter.
      </p>
    </div>
  )
}

/* ----------------------------------------------------- single-value filter */

/** Same autocomplete, one value — used by the skill filter on the jobs page. */
export function SkillFilterInput({
  value, onChange, onSubmit, placeholder = 'Skill, e.g. React',
}: {
  value: string
  onChange: (next: string) => void
  onSubmit?: () => void
  placeholder?: string
}) {
  const listId = React.useId()
  const { open, setOpen, options, activeIndex, setActiveIndex, move } =
    useSuggestions(value, [])

  function pick(name: string) {
    onChange(name)
    setOpen(false)
  }

  function onKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === 'ArrowDown') { e.preventDefault(); move(1) }
    else if (e.key === 'ArrowUp') { e.preventDefault(); move(-1) }
    else if (e.key === 'Escape') setOpen(false)
    else if (e.key === 'Enter' && open && options[activeIndex]) {
      // Choose the highlighted suggestion instead of submitting the form.
      e.preventDefault()
      pick(options[activeIndex].name)
    } else if (e.key === 'Enter') {
      setOpen(false)
      onSubmit?.()
    }
  }

  return (
    <div className="relative">
      <Input
        role="combobox"
        aria-expanded={open}
        aria-controls={listId}
        aria-autocomplete="list"
        aria-activedescendant={open ? `${listId}-opt-${activeIndex}` : undefined}
        autoComplete="off"
        value={value}
        placeholder={placeholder}
        onChange={(e) => { onChange(e.target.value); setOpen(true); setActiveIndex(0) }}
        onFocus={() => setOpen(true)}
        onBlur={() => setOpen(false)}
        onKeyDown={onKeyDown}
      />
      {open ? (
        <SuggestionList
          id={listId}
          options={options}
          activeIndex={activeIndex}
          onPick={(entry) => pick(entry.name)}
          onHover={setActiveIndex}
        />
      ) : null}
    </div>
  )
}
