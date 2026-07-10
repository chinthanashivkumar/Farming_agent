import React, { useState, useEffect, useRef, useCallback } from 'react';
import { chatService } from '../services/api';
import { useFarmer } from '../context/FarmerContext';
import toast from 'react-hot-toast';
import './ChatPage.css';

// ── Quick prompts per language ────────────────────────────────────────────────
const QUICK_PROMPTS = {
  en: [
    '🌾 What crop should I grow this monsoon?',
    '🍅 Today\'s tomato mandi price?',
    '🐛 Yellow spots on my cotton leaves',
    '💧 How much water does paddy need?',
    '🧪 Which fertilizer for wheat at sowing?',
    '📈 Which crop is most profitable this season?',
    '🌱 My soil pH is 5.5 — what to grow?',
    '🌤️ Signs of nitrogen deficiency?',
  ],
  hi: [
    '🌾 इस मानसून में कौन सी फसल उगाऊं?',
    '🍅 आज टमाटर का मंडी भाव क्या है?',
    '🐛 मेरी कपास की पत्तियों पर पीले धब्बे हैं',
    '💧 धान को कितना पानी चाहिए?',
    '🧪 गेहूं बोते समय कौन सी खाद दें?',
    '📈 इस सीजन में कौन सी फसल सबसे फायदेमंद है?',
    '🌱 मेरी मिट्टी का pH 5.5 है — क्या उगाएं?',
    '🌤️ नाइट्रोजन की कमी के क्या लक्षण हैं?',
  ],
  kn: [
    '🌾 ಈ ಮಳೆಗಾಲದಲ್ಲಿ ಯಾವ ಬೆಳೆ ಬೆಳೆಯಬೇಕು?',
    '🍅 ಇಂದಿನ ಟೊಮಾಟೊ ಮಂಡಿ ಬೆಲೆ ಏನು?',
    '🐛 ನನ್ನ ಹತ್ತಿ ಎಲೆಗಳಲ್ಲಿ ಹಳದಿ ಚುಕ್ಕೆಗಳಿವೆ',
    '💧 ಭತ್ತಕ್ಕೆ ಎಷ್ಟು ನೀರು ಬೇಕು?',
    '🧪 ಗೋಧಿ ಬಿತ್ತನೆ ಸಮಯದಲ್ಲಿ ಯಾವ ರಸಗೊಬ್ಬರ?',
    '📈 ಈ ಋತುವಿನಲ್ಲಿ ಯಾವ ಬೆಳೆ ಹೆಚ್ಚು ಲಾಭದಾಯಕ?',
    '🌱 ನನ್ನ ಮಣ್ಣಿನ pH 5.5 — ಏನು ಬೆಳೆಯಬಹುದು?',
    '🌤️ ಸಾರಜನಕ ಕೊರತೆಯ ಲಕ್ಷಣಗಳೇನು?',
  ],
};

// ── Chrome Web Speech API language codes ─────────────────────────────────────
// NOTE: Chrome requires exact BCP-47 tags. 'kn-IN' is NOT recognised — use 'kn'.
// 'hi-IN' and 'en-IN' work fine.
const SPEECH_LANG_MAP = {
  en: 'en-IN',
  hi: 'hi-IN',
  kn: 'kn',     // Kannada — Chrome only accepts 'kn' (no region suffix)
};

// ── Hint chips per language ───────────────────────────────────────────────────
const HINT_CHIPS = {
  en: ['🌾 Crop advice', '📊 Market price', '🐛 Pest help', '💧 Irrigation', '🧪 Fertilizer'],
  hi: ['🌾 फसल सलाह', '📊 मंडी भाव', '🐛 कीट सहायता', '💧 सिंचाई', '🧪 खाद'],
  kn: ['🌾 ಬೆಳೆ ಸಲಹೆ', '📊 ಮಂಡಿ ಬೆಲೆ', '🐛 ಕೀಟ ಸಹಾಯ', '💧 ನೀರಾವರಿ', '🧪 ಗೊಬ್ಬರ'],
};

function formatTime(iso) {
  if (!iso) return '';
  return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

// ── Render AI message: support **bold**, bullet lines, newlines ───────────────
function MessageContent({ text }) {
  if (!text) return null;
  return (
    <div className="msg-content">
      {text.split('\n').map((line, i) => {
        const trimmed = line.trim();
        if (!trimmed) return <br key={i} />;

        // Bullet points: lines starting with -, *, •, numbers like "1."
        const isBullet = /^(\*|-|•|\d+\.)\s/.test(trimmed);
        // Bold: **text**
        const parts = trimmed.split(/\*\*(.+?)\*\*/g).map((part, j) =>
          j % 2 === 1 ? <strong key={j}>{part}</strong> : part
        );

        if (isBullet) {
          return (
            <div key={i} className="msg-bullet">
              <span className="bullet-dot">•</span>
              <span>{parts}</span>
            </div>
          );
        }
        return <p key={i} className="msg-line">{parts}</p>;
      })}
    </div>
  );
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
  const [sessions, setSessions]       = useState([]);
  const [activeSession, setActiveSession] = useState(null);
  const [messages, setMessages]       = useState([]);
  const [input, setInput]             = useState('');
  const [loading, setLoading]         = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [micStatus, setMicStatus]     = useState('');   // live feedback text
  const messagesEndRef = useRef(null);
  const textareaRef    = useRef(null);
  const recognitionRef = useRef(null);

  const prompts   = QUICK_PROMPTS[language] || QUICK_PROMPTS.en;
  const hintChips = HINT_CHIPS[language]    || HINT_CHIPS.en;

  // ── Load sessions ─────────────────────────────────────────────────────────
  const loadSessions = useCallback(async () => {
    try {
      const res = await chatService.getSessions();
      setSessions(res.data);
    } catch { /* no sessions yet */ }
  }, []);

  useEffect(() => { loadSessions(); }, [loadSessions]);

  // ── Load messages for active session ─────────────────────────────────────
  useEffect(() => {
    if (!activeSession) { setMessages([]); return; }
    chatService.getMessages(activeSession.id)
      .then(res => setMessages(res.data))
      .catch(() => setMessages([]));
  }, [activeSession]);

  // ── Auto-scroll ───────────────────────────────────────────────────────────
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  // ── Auto-resize textarea ──────────────────────────────────────────────────
  useEffect(() => {
    const ta = textareaRef.current;
    if (!ta) return;
    ta.style.height = 'auto';
    ta.style.height = Math.min(ta.scrollHeight, 140) + 'px';
  }, [input]);

  // ── Stop recognition when language changes ────────────────────────────────
  useEffect(() => {
    if (recognitionRef.current) {
      recognitionRef.current.abort();
      recognitionRef.current = null;
      setIsRecording(false);
      setMicStatus('');
    }
  }, [language]);

  // ── Cleanup on unmount ────────────────────────────────────────────────────
  useEffect(() => {
    return () => {
      recognitionRef.current?.abort();
      recognitionRef.current = null;
    };
  }, []);

  // ── Farmer context ────────────────────────────────────────────────────────
  const buildContext = () => ({
    location:        profile?.district ? `${profile.district}, ${profile.state}` : undefined,
    state:           profile?.state,
    soil_type:       profile?.soil_type,
    farm_size_acres: profile?.farm_size_acres,
    primary_crops:   profile?.primary_crops,
    irrigation_type: profile?.irrigation_type,
  });

  // ── Send message ──────────────────────────────────────────────────────────
  const sendMessage = async (text) => {
    const msg = (text || input).trim();
    if (!msg || loading) return;

    const optimisticUser = {
      id: Date.now(), role: 'user', content: msg,
      created_at: new Date().toISOString(),
    };
    setMessages(prev => [...prev, optimisticUser]);
    setInput('');
    setLoading(true);

    try {
      const res = await chatService.send({
        message: msg,
        session_id: activeSession?.id || null,
        language,
        farmer_context: buildContext(),
      });

      if (!activeSession) {
        setActiveSession({ id: res.data.session_id, title: msg.slice(0, 50) });
        loadSessions();
      }

      setMessages(prev => [...prev, {
        id: res.data.message_id,
        role: 'assistant',
        content: res.data.response,
        intent: res.data.intent,
        sources: res.data.sources || [],
        created_at: new Date().toISOString(),
      }]);
    } catch (err) {
      setMessages(prev => prev.filter(m => m.id !== optimisticUser.id));
      toast.error(err.response?.data?.detail || 'Failed to get AI response');
    } finally { setLoading(false); }
  };

  // ── Mic — Web Speech API ──────────────────────────────────────────────────
  const toggleRecording = () => {
    // Stop if already recording
    if (isRecording) {
      recognitionRef.current?.stop();
      setIsRecording(false);
      setMicStatus('');
      return;
    }

    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      toast.error(
        'Speech recognition not supported. Please use Google Chrome or Microsoft Edge.',
        { duration: 5000 }
      );
      return;
    }

    // Abort any leftover instance
    if (recognitionRef.current) {
      recognitionRef.current.abort();
      recognitionRef.current = null;
    }

    const rec = new SpeechRecognition();

    // ⚠️  Critical: Chrome needs 'kn' not 'kn-IN' for Kannada
    rec.lang              = SPEECH_LANG_MAP[language] || 'en-IN';
    rec.interimResults    = true;   // show live transcript as you speak
    rec.maxAlternatives   = 1;
    rec.continuous        = true;   // keep listening until user taps stop

    let finalTranscript = '';

    rec.onstart = () => {
      setIsRecording(true);
      setMicStatus('🎙️ Listening…');
    };

    rec.onresult = (event) => {
      let interim = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const t = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalTranscript += t + ' ';
        } else {
          interim = t;
        }
      }
      // Show live interim text in mic status bar
      setMicStatus('🎙️ ' + (finalTranscript + interim).trim());
    };

    rec.onerror = (event) => {
      setIsRecording(false);
      setMicStatus('');
      recognitionRef.current = null;
      const msgs = {
        'not-allowed':      'Microphone access denied — allow mic in browser settings.',
        'no-speech':        'No speech detected. Please speak closer to the mic.',
        'network':          'Network error during speech recognition.',
        'language-not-supported': `Language not supported by your browser for speech input.`,
        'aborted':          null,
      };
      const m = msgs[event.error] ?? `Mic error: ${event.error}`;
      if (m) toast.error(m, { duration: 5000 });
    };

    rec.onend = () => {
      setIsRecording(false);
      setMicStatus('');
      // If we got final text, put it in the input box
      if (finalTranscript.trim()) {
        setInput(prev => prev ? prev + ' ' + finalTranscript.trim() : finalTranscript.trim());
        toast.success('✅ Voice captured — press ➤ to send');
      }
      recognitionRef.current = null;
    };

    recognitionRef.current = rec;
    rec.start();
  };

  // ── TTS — browser-native ──────────────────────────────────────────────────
  const speakMessage = (text) => {
    if (!window.speechSynthesis) { toast.error('TTS not supported in this browser'); return; }
    window.speechSynthesis.cancel();
    const utter = new SpeechSynthesisUtterance(text);
    utter.lang = SPEECH_LANG_MAP[language] || 'en-IN';
    window.speechSynthesis.speak(utter);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  };

  return (
    <div className="chat-page">
      {/* ── Sessions panel ── */}
      <aside className="chat-sessions">
        <div className="sessions-header">
          <span className="sessions-title">💬 Conversations</span>
          <button className="new-chat-btn"
            onClick={() => { setActiveSession(null); setMessages([]); }}
            title="New chat">＋</button>
        </div>

        <div className="sessions-list">
          {sessions.length === 0 && (
            <p className="sessions-empty">No conversations yet.<br/>Start asking below!</p>
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
          <p className="quick-prompts-title">
            {language === 'kn' ? 'ಕೇಳಲು ಪ್ರಯತ್ನಿಸಿ' : language === 'hi' ? 'पूछें' : 'Try asking'}
          </p>
          {prompts.slice(0, 5).map(q => (
            <button key={q} className="quick-prompt-chip" onClick={() => sendMessage(q)}>
              {q}
            </button>
          ))}
        </div>
      </aside>

      {/* ── Main chat ── */}
      <div className="chat-main">
        <div className="chat-header">
          <div className="chat-header-avatar">🌿</div>
          <div className="chat-header-info">
            <p className="chat-header-name">
              {language === 'kn' ? '🌿 ಕೃಷಿ AI — IBM Granite'
                : language === 'hi' ? '🌿 कृषि AI — IBM Granite'
                : '🌿 Smart Farming AI — IBM Granite'}
            </p>
            <p className="chat-header-status">
              <span className="status-dot" /> Online · RAG-powered
            </p>
          </div>
        </div>

        <div className="chat-messages">
          {messages.length === 0 && !loading && (
            <div className="chat-welcome">
              <div className="chat-welcome-icon">🌾</div>
              <h2>
                {language === 'kn'
                  ? `ನಮಸ್ಕಾರ${profile?.state ? ` — ${profile.state}` : ''}! ನಾನು ನಿಮ್ಮ ಕೃಷಿ AI ಸಹಾಯಕ 🌿`
                  : language === 'hi'
                  ? `नमस्ते${profile?.state ? ` — ${profile.state}` : ''}! मैं आपका कृषि AI सहायक हूं 🌿`
                  : `Hi${profile?.state ? ` from ${profile.state}` : ''}! I'm your Farming AI 🌿`}
              </h2>
              <p>
                {language === 'kn'
                  ? 'ಬೆಳೆ, ಮಣ್ಣು, ಕೀಟ, ಮಂಡಿ ಬೆಲೆ ಅಥವಾ ನೀರಾವರಿ ಬಗ್ಗೆ ಕನ್ನಡದಲ್ಲಿ ಕೇಳಿ.'
                  : language === 'hi'
                  ? 'फसल, मिट्टी, कीट, मंडी भाव या सिंचाई के बारे में हिंदी में पूछें।'
                  : 'Ask me anything about crops, soil, pests, market prices, or irrigation.'}
              </p>
              <div className="chat-welcome-chips">
                {prompts.map(q => (
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
                <div className="msg-bubble">
                  <MessageContent text={msg.content} />
                </div>
                <div className="msg-meta">
                  <span>{formatTime(msg.created_at)}</span>
                  {msg.intent && (
                    <span className="msg-intent-badge">🏷️ {msg.intent}</span>
                  )}
                  {msg.role === 'assistant' && (
                    <button
                      className="tts-btn"
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
          {/* Live mic status strip */}
          {micStatus && (
            <div className="mic-status-bar">
              <span className="mic-status-dot" />
              <span className="mic-status-text">{micStatus}</span>
              <button className="mic-stop-btn" onClick={toggleRecording}>■ Stop</button>
            </div>
          )}

          <div className="chat-input-row">
            <textarea
              ref={textareaRef}
              className="chat-textarea"
              placeholder={
                language === 'kn' ? 'ಕನ್ನಡದಲ್ಲಿ ಕೇಳಿ… (Enter ಕಳುಹಿಸಲು)'
                : language === 'hi' ? 'हिंदी में पूछें… (Enter से भेजें)'
                : 'Ask anything about farming… (Enter to send)'
              }
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
                title={isRecording ? 'Stop recording' : `Voice input (${language === 'kn' ? 'ಕನ್ನಡ' : language === 'hi' ? 'हिंदी' : 'English'})`}
              >🎤</button>
              <button
                className="send-btn"
                onClick={() => sendMessage()}
                disabled={!input.trim() || loading}
              >
                {loading ? <span className="spinner" style={{ borderTopColor: '#fff' }} /> : '➤'}
              </button>
            </div>
          </div>

          <div className="chat-input-hints">
            {hintChips.map(h => (
              <button
                key={h}
                className="hint-chip"
                onClick={() => setInput(h.replace(/^.\s/, ''))}
              >{h}</button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
