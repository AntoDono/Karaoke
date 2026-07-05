import type { WsIn, WsOut } from '~/types'

export interface LiveSocketOptions {
  onPitch?: (m: Extract<WsIn, { type: 'pitch' }>) => void
  onGrade?: (m: Extract<WsIn, { type: 'grade' }>) => void
  onRange?: (m: Extract<WsIn, { type: 'range' }>) => void
  onReady?: (sessionId: string) => void
  onError?: (msg: string) => void
  onClose?: () => void
}

/**
 * WebSocket client for /api/live/ws. Buffers messages sent before the socket
 * opens so callers can `send()` freely at mount time.
 */
export function useLiveSocket(opts: LiveSocketOptions = {}) {
  const config = useRuntimeConfig()
  const wsBase = config.public.wsBase as string

  const isOpen = ref(false)
  const sessionId = ref<string | null>(null)
  const lastError = ref<string | null>(null)

  let socket: WebSocket | null = null
  let pendingText: string[] = []
  let pendingBinary: ArrayBuffer[] = []

  function connect() {
    if (socket) return
    socket = new WebSocket(`${wsBase}/api/live/ws`)
    socket.binaryType = 'arraybuffer'

    socket.onopen = () => {
      isOpen.value = true
      for (const t of pendingText) socket!.send(t)
      for (const b of pendingBinary) socket!.send(b)
      pendingText = []
      pendingBinary = []
    }

    socket.onmessage = (ev) => {
      let msg: WsIn
      try { msg = JSON.parse(ev.data as string) as WsIn }
      catch { return }

      switch (msg.type) {
        case 'ready':
          sessionId.value = msg.session_id
          opts.onReady?.(msg.session_id)
          break
        case 'pitch': opts.onPitch?.(msg); break
        case 'grade': opts.onGrade?.(msg); break
        case 'range': opts.onRange?.(msg); break
        case 'error':
          lastError.value = msg.message
          opts.onError?.(msg.message)
          break
      }
    }

    socket.onclose = () => {
      isOpen.value = false
      socket = null
      sessionId.value = null
      opts.onClose?.()
    }

    socket.onerror = () => {
      lastError.value = 'websocket error'
    }
  }

  function send(msg: WsOut) {
    const text = JSON.stringify(msg)
    if (socket && socket.readyState === WebSocket.OPEN) socket.send(text)
    else pendingText.push(text)
  }

  function sendBinary(buf: ArrayBuffer) {
    if (socket && socket.readyState === WebSocket.OPEN) socket.send(buf)
    else if (pendingBinary.length < 20) pendingBinary.push(buf)
  }

  function close() {
    socket?.close()
    socket = null
    isOpen.value = false
    sessionId.value = null
  }

  onUnmounted(close)

  return { connect, close, send, sendBinary, isOpen, sessionId, lastError }
}
