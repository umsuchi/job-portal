import * as React from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { errorMessage } from '@/api/client'
import { messages } from '@/api/endpoints'
import { Avatar } from '@/components/Avatar'
import { Alert, Button, Card, EmptyState, Skeleton, Textarea } from '@/components/ui'
import { cn } from '@/lib/cn'
import { formatTime } from '@/lib/format'

export function ThreadPage() {
  const { applicationId = '' } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [draft, setDraft] = React.useState('')
  const bottomRef = React.useRef<HTMLDivElement>(null)

  const { data, isPending, error } = useQuery({
    queryKey: ['thread', applicationId],
    queryFn: () => messages.thread(applicationId),
    // US-4.3: polling stands in for WebSockets.
    refetchInterval: 15_000,
    refetchOnWindowFocus: true,
  })

  const count = data?.messages.length ?? 0
  React.useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [count])

  const send = useMutation({
    mutationFn: (body: string) => messages.send(applicationId, body),
    onSuccess: () => {
      setDraft('')
      queryClient.invalidateQueries({ queryKey: ['thread', applicationId] })
      queryClient.invalidateQueries({ queryKey: ['unread'] })
    },
  })

  // Reading the thread clears the badge server-side; refresh the counter too.
  React.useEffect(() => {
    if (data) queryClient.invalidateQueries({ queryKey: ['unread'] })
  }, [data, queryClient])

  function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    const body = draft.trim()
    if (body) send.mutate(body)
  }

  if (isPending) return <Skeleton className="mx-auto h-96 max-w-2xl" />
  if (error || !data) {
    return (
      <EmptyState
        title="Conversation unavailable"
        description={errorMessage(error, 'You may not be a party to this application.')}
        action={<Button variant="outline" onClick={() => navigate(-1)}>Go back</Button>}
      />
    )
  }

  return (
    <div className="mx-auto max-w-2xl">
      <button onClick={() => navigate(-1)} className="text-sm text-muted-foreground hover:underline">
        ← Back
      </button>

      <div className="mt-4 flex items-center gap-3">
        <Avatar
          src={data.counterpart_avatar_url} name={data.counterpart_name} size="lg"
        />
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">{data.counterpart_name}</h1>
          <p className="mt-0.5 text-sm text-muted-foreground">About: {data.job_title}</p>
        </div>
      </div>
      <div className="mb-6" />

      <Card className="flex max-h-[60vh] flex-col overflow-y-auto p-5">
        {data.messages.length === 0 ? (
          <p className="py-8 text-center text-sm text-muted-foreground">
            No messages yet. Say hello.
          </p>
        ) : (
          <div className="space-y-3">
            {data.messages.map((m) => (
              <div key={m.id} className={cn('flex items-end gap-2', m.is_mine ? 'justify-end' : 'justify-start')}>
                {m.is_mine ? null : (
                  <Avatar size="sm" src={m.sender_avatar_url} name={m.sender_name} />
                )}
                <div
                  className={cn(
                    'max-w-[80%] rounded-lg px-3 py-2 text-sm',
                    m.is_mine
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-muted text-foreground',
                  )}
                >
                  <p className="whitespace-pre-wrap">{m.body}</p>
                  <p className={cn('mt-1 text-[11px]', m.is_mine ? 'text-primary-foreground/70' : 'text-muted-foreground')}>
                    {m.is_mine ? 'You' : m.sender_name} · {formatTime(m.sent_at)}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
        <div ref={bottomRef} />
      </Card>

      <form onSubmit={onSubmit} className="mt-4 space-y-2">
        {send.isError ? <Alert>{errorMessage(send.error, 'Could not send.')}</Alert> : null}
        <Textarea
          value={draft}
          maxLength={4000}
          placeholder="Write a message…"
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) onSubmit(e)
          }}
        />
        <div className="flex items-center justify-between">
          <span className="text-xs text-muted-foreground">⌘/Ctrl + Enter to send</span>
          <Button type="submit" loading={send.isPending} disabled={!draft.trim()}>Send</Button>
        </div>
      </form>
    </div>
  )
}
