import React, { useState, useEffect, useRef, useCallback } from 'react';
import { chatService, speechService } from '../services/api';
import { useFarmer } from '../context/FarmerContext';
import toast from 'react-hot-toast';
import './ChatPage.css';

const QUICK_PROMPTS = [
  '🌾 What crop should I grow this monsoon?',
  '🍅 Today\'s tomato mandi price?',
  '🐛 Yellow spots on my cotton leaves',
  '💧 How much water does paddy need?',
  '🧪 Which fertilizer for wheat at sowing?',
  '🌤️ Will it rain tomorrow?',
  '📈 Which crop is most profitable this season?',
  '🌱 My soil pH is 5.5 — what to grow?',
];

function formatTime(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function TypingIndicator() {
  return (
    <div className="message-row ai">
      <div className="msg-avatar ai-avatar">🌿</div>
      <div className="msg-bubble-wrap">
        <div className="typing-indicator">
          <div className="typing-dot" />
          <div className="typing-dot" />
          <div className="typing-dot" />
        </div>
      </div>
    </div>
  );
}

export default function ChatPage() {
  const { profile, language } = useFarmer();
  const [sessions, setSessions]   = useState([]);
  const [activeSession, setActiveSession] = useState(null);
  const [messages, setMessages]   = useState([]);
  const [input, setInput]         = useState('');
  const [loading, setLoading]     = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const messagesEndRef = useRef(null);
  const textareaRef    = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef   = useRef([]);

  // ── Load sessions ────────────────────────────────
  const loadSessions = useCallback(async () => {
    try {
      const res = await chatService.getSessions();
      setSessions(res.data);
    } catch { /* no sessions yet */ }
  }, []);

  useEffect(() => { loadSessions(); }, [loadSessions]);

  // ── Load messages for active session ─────────────
  useEffect(() => {
    if (!activeSession) { setMessages([]); return; }
    chatService.getMessages(activeSession.id)
      .then(res => setMessages(res.data))
      .catch(() => setMessages([]));
  }, [activeSession]);

  // ── Auto-scroll ───────────────────────────────────
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  // ── Auto-resize textarea ─────────────────────────
  useEffect(() => {
    const ta = textareaRef.current;
    if (!ta) return;
    ta.style.height = 'auto';
    ta.style.height = Math.min(ta.scrollHeight, 140) + 'px';
  }, [input]);

  // ── Build farmer context from profile ─────────────
  const buildContext = () => ({
    location:        profile?.district ? `${profile.district}, ${profile.state}` : undefined,
    state:           profile?.state,
    soil_type:       profile?.soil_type,
    farm_size_acres: profile?.farm_size_acres,
    primary_crops:   profile?.primary_crops,
    irrigation_type: profile?.irrigation_type,
  });

  // ── Send message ──────────────────────────────────
  const sendMessage = async (text) => {
    const msg = (text || input).trim();
    if (!msg || loading) return;

    // Optimistically add user message
    const optimisticUser = { id: Date.now(), role: 'user', content: msg, created_at: new Date().toISOString() };
    setMessages(prev => [...prev, optimisticUser]);
    setInput('');
    setLoading(true);

    try {
      const payload = {
        message: msg,
        session_id: activeSession?.id || null,
        language,
        farmer_context: buildContext(),
      };
      const res = await chatService.send(payload);

      // If new session created, update active and reload list
      if (!activeSession) {
        setActiveSession({ id: res.data.session_id, title: msg.slice(0, 50) });
        loadSessions();
      }

      const aiMsg = {
        id: res.data.message_id,
        role: 'assistant',
        content: res.data.response,
        intent: res.data.intent,
        sources: res.data.sources || [],
        created_at: new Date().toISOString(),
      };
      setMessages(prev => [...prev, aiMsg]);
    } catch (err) {
      setMessages(prev => prev.filter(m => m.id !== optimisticUser.id));
      toast.error(err.response?.data?.detail || 'Failed to get AI response');
    } finally { setLoading(false); }
  };

  // ── Voice recording ───────────────────────────────
  const toggleRecording = async () => {
    if (isRecording) {
      mediaRecorderRef.current?.stop();
      setIsRecording(false);
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mr = new MediaRecorder(stream);
      audioChunksRef.current = [];
      mr.ondataavailable = e => audioChunksRef.current.push(e.data);
      mr.onstop = async () => {
        stream.getTracks().forEach(t => t.stop());
        const blob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        const form = new FormData();
        form.append('audio', blob, 'voice.webm');
        form.append('language', language);
        try {
          const res = await speechService.stt(form);
          if (res.data.transcript) { setInput(res.data.transcript); toast.success('Voice captured!'); }
          else toast.error('Could not understand audio');
        } catch { toast.error('Voice transcription failed'); }
      };
      mr.start();
      mediaRecorderRef.current = mr;
      setIsRecording(true);
      toast('🎙️ Recording… tap mic to stop', { icon: '🔴', duration: 60000 });
    } catch { toast.error('Microphone access denied'); }
  };

  // ── Text-to-speech for AI messages ───────────────
  const speakMessage = async (text) => {
    try {
      const res = await speechService.tts(text, language);
      if (res.data.audio_base64) {
        const audio = new Audio(`data:audio/mp3;base64,${res.data.audio_base64}`);
        audio.play();
      }
    } catch { toast.error('TTS unavailable'); }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  };

  const startNewChat = () => { setActiveSession(null); setMessages([]); };

  return (
    <div className="chat-page">
      {/* ── Sessions panel ── */}
      <aside className="chat-sessions">
        <div className="sessions-header">
          <span className="sessions-title">💬 Conversations</span>
          <button className="new-chat-btn" onClick={startNewChat} title="New chat">＋</button>
        </div>

        <div className="sessions-list">
          {sessions.length === 0 && (
            <p style={{ padding: '1rem', fontSize: '0.82rem', color: 'var(--color-text-muted)', textAlign: 'center' }}>
              No conversations yet.<br/>Start asking below!
            </p>
          )}
          {sessions.map(s => (
            <div
              key={s.id}
              className={`session-item${activeSession?.id === s.id ? ' active' : ''}`}
              onClick={() => setActiveSession(s)}
            >
              <p className="session-title">💬 {s.title || 'Conversation'}</p>
              <p className="session-date">{new Date(s.created_at).toLocaleDateString()}</p>
            </div>
          ))}
        </div>

        <div className="quick-prompts">
          <p className="quick-prompts-title">Try asking</p>
          {QUICK_PROMPTS.slice(0, 5).map(q => (
            <button key={q} className="quick-prompt-chip" onClick={() => sendMessage(q)}>
              {q}
            </button>
          ))}
        </div>
      </aside>

      {/* ── Main chat ── */}
      <div className="chat-main">
        {/* Header */}
        <div className="chat-header">
          <div className="chat-header-avatar">🌿</div>
          <div className="chat-header-info">
            <p className="chat-header-name">Smart Farming AI — IBM Granite</p>
            <p className="chat-header-status">
              <span className="status-dot" /> Online · RAG-powered
            </p>
          </div>
        </div>

        {/* Messages */}
        <div className="chat-messages">
          {messages.length === 0 && !loading && (
            <div className="chat-welcome">
              <div className="chat-welcome-icon">🌾</div>
              <h2>Hi {profile ? (profile.state ? `from ${profile.state}` : '') : ''}, I'm your Farming AI!</h2>
              <p>Ask me anything about crops, soil, pests, market prices, or irrigation — in any Indian language.</p>
              <div className="chat-welcome-chips">
                {QUICK_PROMPTS.map(q => (
                  <button key={q} className="welcome-chip" onClick={() => sendMessage(q)}>{q}</button>
                ))}
              </div>
            </div>
          )}

          {messages.map(msg => (
            <div key={msg.id} className={`message-row ${msg.role === 'user' ? 'user' : 'ai'}`}>
              <div className={`msg-avatar ${msg.role === 'user' ? 'user-avatar' : 'ai-avatar'}`}>
                {msg.role === 'user' ? '👤' : '🌿'}
              </div>
              <div className="msg-bubble-wrap">
                <div className="msg-bubble">{msg.content}</div>
                <div className="msg-meta">
                  <span>{formatTime(msg.created_at)}</span>
                  {msg.intent && <span className="msg-intent-badge">{msg.intent}</span>}
                  {msg.role === 'assistant' && (
                    <button
                      style={{ background:'none', border:'none', cursor:'pointer', fontSize:'0.85rem', padding:0 }}
                      onClick={() => speakMessage(msg.content)}
                      title="Speak aloud"
                    >🔊</button>
                  )}
                </div>
                {msg.sources?.length > 0 && (
                  <div className="msg-sources">
                    {msg.sources.map((s, i) => (
                      <span key={i} className="source-chip">📚 {s.source}</span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}

          {loading && <TypingIndicator />}
          <div ref={messagesEndRef} />
        </div>

        {/* Input bar */}
        <div className="chat-input-bar">
          <div className="chat-input-row">
            <textarea
              ref={textareaRef}
              className="chat-textarea"
              placeholder="Ask anything about farming… (Enter to send, Shift+Enter for new line)"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              rows={1}
              disabled={loading}
            />
            <div className="chat-input-actions">
              <button
                className={`input-action-btn${isRecording ? ' recording' : ''}`}
                onClick={toggleRecording}
                title={isRecording ? 'Stop recording' : 'Voice input'}
              >🎤</button>
              <button className="send-btn" onClick={() => sendMessage()} disabled={!input.trim() || loading}>
                {loading ? <span className="spinner" style={{borderTopColor:'#fff'}} /> : '➤'}
              </button>
            </div>
          </div>
          <div className="chat-input-hints">
            {['🌾 Crop advice', '📊 Market price', '🐛 Pest help', '💧 Irrigation', '🧪 Fertilizer'].map(h => (
              <button key={h} className="hint-chip" onClick={() => setInput(h.slice(3))}>{h}</button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
