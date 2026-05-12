import { useState, useRef, useEffect, use } from 'react'
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';


import reactLogo from './assets/react.svg'
import viteLogo from './assets/vite.svg'
import heroImg from './assets/hero.png'
import './App.css'


interface Message {
  id: number;
  sender: 'user' | 'q';
  text: string;
}

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isThinking, setIsThinking] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // State for Vector Memory Topics
  const [memoryTopics, setMemoryTopics] = useState<string[]>([]);

  // Fetch Vector Memory Topics on load
  useEffect(() => {
    const fetchTopics = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/api/memory/topics');
        if (response.ok) {
          const data = await response.json();
          if (data.status === 'success') {
            setMemoryTopics(data.topics || []);
          }
        }
      } catch (error) {
        console.error("Failed to fetch memory topics:", error);
      }
    };
    
    fetchTopics();
  }, []);

  // Auto-scroll to the bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isThinking]);

  const handleSend = async (e?: React.SyntheticEvent) => {
    if (e) {
      e.preventDefault();
    }

    if (!input.trim()) {
      return;
    }

    const userText = input.trim();
    const newMsg: Message = { id: Date.now(), sender: 'user' as const, text: userText };
    setMessages((prev) => [...prev, newMsg]);
    setInput('');
    setIsThinking(true);

    try {
      // NOTE: Ensure this matches the exact route/schema in your api/rest_routes.py
      const response = await fetch('http://127.0.0.1:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({sender: 'user', message: userText }), 
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // Grab the exact key sent by FastAPI
      const qText = data.q_response || "**[SYSTEM]** Empty response received.";

      const qMsg: Message = { id: Date.now() + 1, sender: 'q' as const, text: qText };
      setMessages((prev) => [...prev, qMsg]);

    } catch (error) {
      console.error("Backend Connection Error:", error);
      const errorMsg: Message = { 
        id: Date.now() + 1, 
        sender: 'q' as const, 
        text: "**[SYSTEM FATAL]** Connection to the Daemon failed. Is `main.py` running on port 8000?" 
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsThinking(false);
    }
  };

  return (
    <>
      <header className="bg-slate-950 p-4 border-b border-slate-800 shadow-sm flex justify-between items-center z-10">
        <div>
          <h1 className="text-xl font-bold tracking-wider text-emerald-400">AXXANOID OS</h1>
          <p className="text-xs text-slate-500 uppercase tracking-widest">Project Q // Sovereign Daemon</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
          <span className="text-xs text-slate-400 font-mono">SYSTEM NOMINAL</span>
        </div>
      </header>
      <div className="flex h-[65vh] w-full bg-slate-900 text-slate-50 font-sans">
        {/* Vector Memory Topics (left column - top)*/}
        <div className="w-1/4 flex-none bg-slate-950 border-r border-slate-800 overflow-y-auto">
          <h2 className="text-xs font-bold text-slate-400 mb-2 uppercase tracking-wider mb-4 border-b border-slate-800 pb-2">
            Vector Memory Vault
          </h2>
          {memoryTopics.length === 0 ? (
            <p className=" text-sm text-slate-600 italic">No topics found.</p>
          ) : (
            <ul className="space-y-2">
              {memoryTopics.map((topic, idx) => (
                <li
                key={idx}
                className="text-sm text-emerald-400/800 bg-slate-900 px-3 py-2 rounded border border-slate-800 hover:border-emerald-500/50 transition-colors cursor-default">
                  {topic}
              </li>
              ))}
            </ul>
          )}
        </div>
        <div className="w-2/4 h-full flex-none">
          {/* Chat Log */}
          <main className="overflow-y-auto h-full  p-4 sm:p-6 space-y-6">
            {messages.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-slate-500 space-y-2">
                <p className="font-mono text-sm">System initialized.</p>
                <p className="font-mono text-sm">Awaiting input, Mon Capitaine.</p>
              </div>
            ) : (
              messages.map((msg) => (
                <div key={msg.id} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div 
                    className={`max-w-[85%] md:max-w-[70%] rounded-lg p-4 ${
                      msg.sender === 'user' 
                        ? 'bg-emerald-900/40 border border-emerald-800/50 text-emerald-100' 
                        : 'bg-slate-800 border border-slate-700 text-slate-200 shadow-md'
                    }`}
                  >
                    {msg.sender === 'q' && (
                      <div className="text-xs font-bold text-slate-400 mb-2 uppercase tracking-wider">Q-Daemon</div>
                    )}
                    {/* ReactMarkdown handles the bolding, lists, and code blocks from Q's output */}
                    <div className="prose prose-invert prose-sm max-w-none">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {msg.text}
                      </ReactMarkdown>
                    </div>
                  </div>
                </div>
              ))
            )}

            {/* Thinking Indicator */}
            {isThinking && (
              <div className="flex justify-start">
                <div className="bg-slate-800 border border-slate-700 rounded-lg p-4 shadow-md">
                    <div className="text-xs font-bold text-slate-400 mb-2 uppercase tracking-wider">Q-Daemon</div>
                    <div className="flex gap-1">
                      <span className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce"></span>
                      <span className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce delay-75"></span>
                      <span className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce delay-150"></span>
                    </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </main>
        </div>
        <div className="w-1/4 flex-none">
          <div className="hero">
            <img src={heroImg} className="base" width="170" height="179" alt="" />
            <img src={reactLogo} className="framework" alt="React logo" />
            <img src={viteLogo} className="vite" alt="Vite logo" />
          </div>
        </div>
      </div>
      <div className="flex h-[15vh] w-full bg-slate-900 text-slate-50 font-sans">
        <div className="w-1/4 flex-none border-r border-slate-800 bg-slate-950">
          {/* <div className="hero">
            <img src={heroImg} className="base" width="170" height="179" alt="" />
            <img src={reactLogo} className="framework" alt="React logo" />
            <img src={viteLogo} className="vite" alt="Vite logo" />
          </div> */}
        </div>
        <div className="w-2/4 h-full flex-none">
          {/* Input Area */}
          <div className="p-4 bg-slate-950 border-t border-slate-800">
            <form onSubmit={handleSend} className="max-w-5xl mx-auto flex gap-3">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                disabled={isThinking}
                placeholder={isThinking ? "Q is thinking..." : "Enter command..."}
                className="flex-1 bg-slate-900 border border-slate-700 rounded-md px-4 py-3 text-slate-100 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-colors disabled:opacity-50"
              />
              <button
                type="submit"
                disabled={isThinking || !input.trim()}
                className="bg-emerald-600 hover:bg-emerald-500 text-white px-6 py-3 rounded-md font-medium tracking-wide transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                EXECUTE
              </button>
            </form>
          </div>
        </div>
        <div className="w-1/4 flex-none">
          <div className="hero">
            <img src={heroImg} className="base" width="170" height="179" alt="" />
            <img src={reactLogo} className="framework" alt="React logo" />
            <img src={viteLogo} className="vite" alt="Vite logo" />
          </div>
        </div>
      </div>
      <div className="ticks"></div>
      <section id="next-steps">
        <div id="docs">
          <svg className="icon" role="presentation" aria-hidden="true">
            <use href="/icons.svg#documentation-icon"></use>
          </svg>
          <h2>Documentation</h2>
          <p>Your questions, answered</p>
          <ul>
            <li>
              <a href="https://vite.dev/" target="_blank">
                <img className="logo" src={viteLogo} alt="" />
                Explore Vite
              </a>
            </li>
            <li>
              <a href="https://react.dev/" target="_blank">
                <img className="button-icon" src={reactLogo} alt="" />
                Learn more
              </a>
            </li>
          </ul>
        </div>
        <div id="social">
          <svg className="icon" role="presentation" aria-hidden="true">
            <use href="/icons.svg#social-icon"></use>
          </svg>
          <h2>Connect with us</h2>
          <p>Join the Vite community</p>
          <ul>
            <li>
              <a href="https://github.com/vitejs/vite" target="_blank">
                <svg
                  className="button-icon"
                  role="presentation"
                  aria-hidden="true"
                >
                  <use href="/icons.svg#github-icon"></use>
                </svg>
                GitHub
              </a>
            </li>
            <li>
              <a href="https://chat.vite.dev/" target="_blank">
                <svg
                  className="button-icon"
                  role="presentation"
                  aria-hidden="true"
                >
                  <use href="/icons.svg#discord-icon"></use>
                </svg>
                Discord
              </a>
            </li>
            <li>
              <a href="https://x.com/vite_js" target="_blank">
                <svg
                  className="button-icon"
                  role="presentation"
                  aria-hidden="true"
                >
                  <use href="/icons.svg#x-icon"></use>
                </svg>
                X.com
              </a>
            </li>
            <li>
              <a href="https://bsky.app/profile/vite.dev" target="_blank">
                <svg
                  className="button-icon"
                  role="presentation"
                  aria-hidden="true"
                >
                  <use href="/icons.svg#bluesky-icon"></use>
                </svg>
                Bluesky
              </a>
            </li>
          </ul>
        </div>
      </section>
      <div className="ticks"></div>
      <section id="spacer"></section>
    </>
  )
}

export default App
