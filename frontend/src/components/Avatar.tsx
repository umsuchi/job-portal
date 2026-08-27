import * as React from 'react'
import { cn } from '@/lib/cn'

const SIZES = { sm: 'h-8 w-8 text-xs', md: 'h-10 w-10 text-sm', lg: 'h-14 w-14 text-base' }

function initials(name?: string | null): string {
  if (!name) return '?'
  const words = name.trim().split(/\s+/).slice(0, 2)
  return words.map((w) => w[0]?.toUpperCase() ?? '').join('') || '?'
}

/**
 * Avatar from a URL, falling back to initials.
 *
 * The URL is user-supplied and unvalidated, so a broken or hostile link must
 * degrade to the initials rather than showing a broken-image icon — hence the
 * onError swap. `referrerPolicy` keeps the app's URLs out of the image host's
 * logs.
 */
export function Avatar({
  src, name, size = 'md', className,
}: {
  src?: string | null
  name?: string | null
  size?: keyof typeof SIZES
  className?: string
}) {
  const [failed, setFailed] = React.useState(false)
  React.useEffect(() => setFailed(false), [src])

  const shell = cn(
    'inline-flex shrink-0 items-center justify-center overflow-hidden rounded-full',
    'bg-muted font-medium text-muted-foreground',
    SIZES[size], className,
  )

  if (!src || failed) {
    return <span className={shell} aria-hidden>{initials(name)}</span>
  }
  return (
    <span className={shell}>
      <img
        src={src}
        alt={name ? `${name}` : ''}
        loading="lazy"
        referrerPolicy="no-referrer"
        className="h-full w-full object-cover"
        onError={() => setFailed(true)}
      />
    </span>
  )
}
