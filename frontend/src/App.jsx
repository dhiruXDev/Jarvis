import React, { useState, useEffect, useRef } from 'react';

export default function App() {
  // --- STATE ---
  const [time, setTime] = useState('12:00:00 AM');
  const [date, setDate] = useState('May 22, 2026');
  const [uptime, setUptime] = useState(0);
  const [backendStatus, setBackendStatus] = useState('Offline');
  
  const [cpu, setCpu] = useState(0);
  const [ram, setRam] = useState({ used: 0, total: 0, percent: 0 });
  const [disk, setDisk] = useState({ used: 0, total: 0, percent: 0 });
  const [netUpload, setNetUpload] = useState('0.0 Mbps');
  const [netDownload, setNetDownload] = useState('0.0 Mbps');
  
  // Real-time network speed for canvas wave modulation
  const netUploadKb = useRef(0);
  const netDownloadKb = useRef(0);
  
  // Weather Info
  const [weather, setWeather] = useState({
    temp: 25.2,
    city: 'Queen City',
    country: 'PH',
    condition: 'Overcast Clouds',
    humidity: 38,
    wind: 5.4,
    feels_like: 26.1
  });
  
  const [hologramState, setHologramState] = useState('idle');
  const [micActive, setMicActive] = useState(true);
  const [keyboardActive, setKeyboardActive] = useState(false);
  const [cameraActive, setCameraActive] = useState(false);
  
  const [messages, setMessages] = useState([
    { sender: 'Jarvis', text: 'Hello, I am JARVIS.', time: '02:51 PM' },
    { sender: 'Jarvis', text: 'JARVIS backend is online. Ready for command, sir.', time: '02:51 PM' }
  ]);
  const [chatInput, setChatInput] = useState('');
  
  const [terminalOpen, setTerminalOpen] = useState(false);
  const [logs, setLogs] = useState([
    { text: '[JARVIS HUD React Core Initializing...]', type: 'info' },
    { text: '[Server-Sent Events listener offline]', type: '' },
    { text: '[Listening for backend stream...]', type: 'info' }
  ]);
  const [autoscroll, setAutoscroll] = useState(true);
  
  // --- REFS ---
  const canvasRef = useRef(null);
  const chatEndRef = useRef(null);
  const logEndRef = useRef(null);
  const hologramTimer = useRef(null);
  const sseRef = useRef(null);

  // ==========================================
  // CLOCK, DATE & UPTIME INTERVALLER
  // ==========================================
  useEffect(() => {
    // Clock & Date updater
    const updateTime = () => {
      const now = new Date();
      
      let hours = now.getHours();
      const minutes = String(now.getMinutes()).padStart(2, '0');
      const seconds = String(now.getSeconds()).padStart(2, '0');
      const ampm = hours >= 12 ? 'PM' : 'AM';
      hours = hours % 12;
      hours = hours ? hours : 12;
      const hoursStr = String(hours).padStart(2, '0');
      
      setTime(`${hoursStr}:${minutes}:${seconds} ${ampm}`);
      
      const months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
      setDate(`${months[now.getMonth()]} ${now.getDate()}, ${now.getFullYear()}`);
    };
    
    updateTime();
    const clockInterval = setInterval(updateTime, 1000);
    
    // Uptime updater
    const uptimeInterval = setInterval(() => {
      setUptime(prev => prev + 1);
    }, 1000);
    
    return () => {
      clearInterval(clockInterval);
      clearInterval(uptimeInterval);
    };
  }, []);

  const formatUptime = (sec) => {
    const h = String(Math.floor(sec / 3600)).padStart(2, '0');
    const m = String(Math.floor((sec % 3600) / 60)).padStart(2, '0');
    const s = String(sec % 60).padStart(2, '0');
    return `${h}:${m}:${s}`;
  };

  // ==========================================
  // REAL-TIME CANVAS OSCILLOSCOPE (NET SPEED)
  // ==========================================
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    let animationFrameId;
    let phase = 0;
    
    const resizeCanvas = () => {
      canvas.width = canvas.parentElement.clientWidth;
      canvas.height = canvas.parentElement.clientHeight;
    };
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    
    const draw = () => {
      if (!canvas.width) return;
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      const totalKb = netUploadKb.current + netDownloadKb.current;
      const baseAmplitude = 8;
      const maxAdditionalAmplitude = 18;
      const normSpeed = Math.min(totalKb / 12500, 1.0); 
      
      const amplitude = baseAmplitude + (normSpeed * maxAdditionalAmplitude);
      const frequency = 0.015 + (normSpeed * 0.03);
      const speed = 0.04 + (normSpeed * 0.1);
      
      phase += speed;
      
      // Draw grid lines
      ctx.strokeStyle = "rgba(0, 187, 255, 0.04)";
      ctx.lineWidth = 1;
      for (let i = 0; i < canvas.width; i += 20) {
        ctx.beginPath();
        ctx.moveTo(i, 0);
        ctx.lineTo(i, canvas.height);
        ctx.stroke();
      }
      for (let i = 0; i < canvas.height; i += 15) {
        ctx.beginPath();
        ctx.moveTo(0, i);
        ctx.lineTo(canvas.width, i);
        ctx.stroke();
      }
      
      // Multi-layer sine waves
      const waves = [
        { color: "rgba(0, 240, 255, 0.45)", amp: amplitude, freq: frequency, offset: 0 },
        { color: "rgba(0, 119, 255, 0.3)", amp: amplitude * 0.6, freq: frequency * 1.5, offset: Math.PI / 2 },
        { color: "rgba(0, 187, 255, 0.15)", amp: amplitude * 0.4, freq: frequency * 0.8, offset: Math.PI }
      ];
      
      waves.forEach((w, index) => {
        ctx.strokeStyle = w.color;
        ctx.lineWidth = index === 0 ? 2 : 1;
        ctx.beginPath();
        
        for (let x = 0; x < canvas.width; x++) {
          const y = (canvas.height / 2) + Math.sin(x * w.freq + phase + w.offset) * w.amp;
          if (x === 0) {
            ctx.moveTo(x, y);
          } else {
            ctx.lineTo(x, y);
          }
        }
        ctx.stroke();
      });
      
      animationFrameId = requestAnimationFrame(draw);
    };
    
    draw();
    
    return () => {
      window.removeEventListener('resize', resizeCanvas);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  // ==========================================
  // SYSTEM LOG PUSHING
  // ==========================================
  const addLog = (text, type = '') => {
    setLogs(prev => {
      const cleanText = text.trim();
      if (!cleanText) return prev;
      
      let finalType = type;
      if (!type) {
        if (cleanText.includes("[ERROR]") || cleanText.includes("Error:") || cleanText.includes("Exception:")) finalType = 'error';
        else if (cleanText.includes("[SUCCESS]") || cleanText.includes("ready") || cleanText.includes("complete")) finalType = 'success';
        else if (cleanText.includes("[SYSTEM]") || cleanText.includes("[EXECUTOR]") || cleanText.includes("[LOCAL PARSER")) finalType = 'info';
      }
      return [...prev, { text: cleanText, type: finalType }];
    });
  };

  // ==========================================
  // SSE EVENT SUBSCRIPTION
  // ==========================================
  useEffect(() => {
    const connectSSE = () => {
      addLog("[SSE] Connecting to Jarvis Event Stream...", "info");
      
      const sse = new EventSource('/events');
      sseRef.current = sse;
      
      sse.onopen = () => {
        setBackendStatus('Online');
        addLog("[SSE] Connection established successfully.", "success");
      };
      
      sse.onerror = () => {
        setBackendStatus('Offline');
        addLog("[SSE ERROR] Disconnected. Reconnecting in 3s...", "error");
        sse.close();
        setTimeout(connectSSE, 3000);
      };
      
      // Stats handler
      sse.addEventListener("system_stats", (e) => {
        try {
          const stats = JSON.parse(e.data);
          
          setCpu(stats.cpu);
          setRam(stats.ram);
          setDisk(stats.disk);
          setNetUpload(`${stats.network.upload.toFixed(1)} Mbps`);
          setNetDownload(`${stats.network.download.toFixed(1)} Mbps`);
          
          // Cache values for canvas modulation
          netUploadKb.current = stats.network.upload * 125;
          netDownloadKb.current = stats.network.download * 125;
          
          if (stats.weather) {
            setWeather(stats.weather);
          }
        } catch (err) {
          console.error("Stats parse fail:", err);
        }
      });
      
      // Console redirector prints
      sse.addEventListener("console_log", (e) => {
        addLog(e.data);
      });
      
      // Conversation messages
      sse.addEventListener("chat_message", (e) => {
        try {
          const msg = JSON.parse(e.data);
          setMessages(prev => [...prev, { sender: msg.sender, text: msg.text, time: msg.timestamp }]);
          
          if (msg.sender.toLowerCase() === 'jarvis') {
            triggerHologram('speaking', 3000);
          }
        } catch (err) {
          console.error("Chat message parse fail:", err);
        }
      });
      
      // State updater
      sse.addEventListener("status", (e) => {
        try {
          const data = JSON.parse(e.data);
          triggerHologram(data.state, data.duration || 0);
        } catch (err) {
          console.error("Status parse fail:", err);
        }
      });
    };
    
    connectSSE();
    
    return () => {
      if (sseRef.current) sseRef.current.close();
    };
  }, []);

  // Hologram State machine
  const triggerHologram = (state, duration = 0) => {
    if (hologramTimer.current) {
      clearTimeout(hologramTimer.current);
      hologramTimer.current = null;
    }
    
    setHologramState(state);
    
    if (state === 'listening') {
      setMicActive(true);
    }
    
    if (duration > 0) {
      hologramTimer.current = setTimeout(() => {
        setHologramState('idle');
      }, duration);
    }
  };

  // --- ACTIONS ---
  const sendCommand = (e) => {
    if (e) e.preventDefault();
    const command = chatInput.trim();
    if (!command) return;
    
    setChatInput('');
    
    // Append user chat locally
    const now = new Date();
    const timestamp = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    setMessages(prev => [...prev, { sender: 'You', text: command, time: timestamp }]);
    
    fetch('/api/command', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ command: command })
    })
    .then(res => res.json())
    .then(data => {
      if (data.status === 'error') {
        addLog(`[ERROR] Command Dispatch: ${data.message}`, 'error');
      }
    })
    .catch(err => {
      addLog(`[CONNECTION FAILURE] Failed to post command: ${err}`, 'error');
    });
  };

  const toggleMic = () => {
    fetch('/api/toggle-mic', { method: 'POST' })
      .then(res => res.json())
      .then(data => {
        setMicActive(data.active);
        addLog(`[SYSTEM] Microphone ${data.active ? "activated." : "deactivated."}`, 'info');
      })
      .catch(err => {
        addLog(`[ERROR] Failed to toggle mic: ${err}`, 'error');
      });
  };

  const exportChat = () => {
    let text = "=== JARVIS CONVERSATION EXPORT ===\n\n";
    messages.forEach(m => {
      text += `[${m.time}] ${m.sender}: ${m.text}\n`;
    });
    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'jarvis_conversation.txt';
    link.click();
    addLog("[CONVERSATION] Chat logs exported successfully.", "success");
  };

  // Autoscrollers
  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  useEffect(() => {
    if (autoscroll && logEndRef.current) {
      logEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, autoscroll]);

  // Determine core avatar active state styles
  const getAvatarClasses = () => {
    if (hologramState === 'listening') return 'animate-core-listening scale-105';
    if (hologramState === 'speaking') return 'animate-core-speaking scale-102';
    if (hologramState === 'processing') return 'processing';
    return 'animate-pulse duration-5000';
  };

  const getStatusText = () => {
    if (hologramState === 'listening') return 'Listening for voice command...';
    if (hologramState === 'speaking') return 'Speaking...';
    if (hologramState === 'processing' || hologramState === 'recognizing') return 'Processing command...';
    return 'System Idle';
  };

  const getStatusColor = () => {
    if (hologramState === 'listening') return 'text-cyber-cyan bg-cyber-cyan/10 border-cyber-cyan/35';
    if (hologramState === 'speaking') return 'text-cyber-magenta bg-cyber-magenta/10 border-cyber-magenta/35';
    if (hologramState === 'processing' || hologramState === 'recognizing') return 'text-cyber-orange bg-cyber-orange/10 border-cyber-orange/35';
    return 'text-cyber-muted bg-cyber-muted/5 border-cyber-blue/15';
  };

  const getPulseColor = () => {
    if (hologramState === 'listening') return 'bg-cyber-cyan shadow-[0_0_10px_#00f0ff]';
    if (hologramState === 'speaking') return 'bg-cyber-magenta shadow-[0_0_10px_#e0a3ff]';
    if (hologramState === 'processing' || hologramState === 'recognizing') return 'bg-cyber-orange shadow-[0_0_10px_#ff9900]';
    return 'bg-cyber-dim shadow-none';
  };

  const getMouthD = () => {
    if (hologramState === 'listening') return 'M170,250 Q200,235 230,250';
    if (hologramState === 'speaking') return 'M170,250 Q200,225 230,250';
    return 'M170,250 Q200,250 230,250';
  };

  const getMeshColor = () => {
    if (hologramState === 'listening') return '#00f0ff';
    if (hologramState === 'speaking') return '#e0a3ff';
    if (hologramState === 'processing' || hologramState === 'recognizing') return '#ff9900';
    return '#00bbff';
  };

  return (
    <div className="flex flex-col h-screen p-[15px] relative overflow-hidden select-none">
      
      {/* --- TOP HEADER BAR --- */}
      <header className="flex justify-between items-center px-5 py-[10px] mb-[15px] bg-cyber-card border border-cyber-blue/20 rounded-lg backdrop-blur-xl shadow-glow relative overflow-hidden before:content-[''] before:absolute before:top-0 before:left-0 before:w-full before:height-[1px] before:bg-gradient-to-r before:from-transparent before:via-cyber-blue before:to-transparent">
        <div className="flex items-center gap-[15px]">
          <span className="font-hud text-[28px] font-black text-white [text-shadow:0_0_10px_#00bbff] tracking-wider">06</span>
          <span className="font-hud text-[22px] font-bold tracking-[4px] bg-gradient-to-r from-white to-cyber-blue bg-clip-text text-transparent filter drop-shadow-[0_0_5px_rgba(0,187,255,0.5)]">JARVIS</span>
          <div className={`flex items-center gap-[6px] px-[10px] py-[3px] rounded-full font-hud text-[10px] tracking-wider border bg-cyber-cyan/5 border-cyber-cyan/20 text-cyber-cyan`}>
            <span className={`w-[6px] height-[6px] rounded-full bg-cyber-cyan shadow-[0_0_8px_#00f0ff] ${backendStatus === 'Online' ? 'animate-ping' : ''}`}></span>
            <span>{backendStatus}</span>
          </div>
        </div>
        
        <div className="font-hud text-[16px] tracking-[2px] text-white [text-shadow:0_0_8px_rgba(0,187,255,0.4)] flex items-center gap-3">
          <span>{time}</span>
          <span className="text-cyber-dim">|</span>
          <span>{date}</span>
        </div>
        
        <div className="flex items-center gap-5">
          <div className="flex items-center gap-[10px] border-r border-cyber-blue/20 pr-5">
            <span className="font-hud text-[16px] font-semibold text-white [text-shadow:0_0_5px_#00bbff]">{weather.temp.toFixed(1)}°C</span>
            <div className="flex flex-col text-[12px] text-cyber-muted">
              <span>{weather.city}</span>
              <span>💧 {weather.humidity}%</span>
            </div>
          </div>
          <button className="bg-none border border-cyber-blue/20 rounded-md w-8 h-8 flex justify-center items-center cursor-pointer transition-all duration-300 hover:border-cyber-cyan hover:shadow-[0_0_10px_rgba(0,240,255,0.3)] hover:rotate-45 group">
            <svg viewBox="0 0 24 24" className="w-[18px] h-[18px] fill-cyber-muted transition-colors duration-300 group-hover:fill-cyber-cyan">
              <path d="M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54c-.04-.24-.24-.41-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.05.3-.09.63-.09.94s.02.64.07.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/>
            </svg>
          </button>
        </div>
      </header>

      {/* --- MAIN HUD INTERFACE GRID --- */}
      <main className={`grid grid-cols-[28%_44%_28%] gap-[15px] flex-1 min-h-0 transition-[padding-bottom] duration-300 ${terminalOpen ? 'pb-[220px]' : 'pb-[50px]'}`}>
        
        {/* LEFT COLUMN: SYSTEM INFO, SPEED, WEATHER, UPTIME */}
        <section className="flex flex-col gap-[15px] min-h-0">
          
          {/* SYSTEM OVERVIEW */}
          <div className="bg-cyber-card border border-cyber-blue/15 rounded-lg flex flex-col p-4 shadow-glow hover:border-cyber-blue/30 transition-colors duration-300 flex-[1.1]">
            <div className="flex items-center gap-[10px] pb-3 border-b border-cyber-blue/10 mb-4 relative after:content-[''] after:absolute after:bottom-[-1px] after:left-0 after:w-10 after:height-[1px] after:bg-cyber-blue after:[box-shadow:0_0_5px_#00bbff]">
              <svg viewBox="0 0 24 24" className="w-4 h-4 fill-cyber-blue filter drop-shadow-[0_0_3px_#00bbff]"><path d="M21 2H3c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h7l-2 3v1h8v-1l-2-3h7c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H3V4h18v12z"/></svg>
              <h2 className="font-hud text-[13px] font-semibold tracking-wider text-white">SYSTEM OVERVIEW</h2>
            </div>
            
            <div className="flex flex-col gap-[15px] justify-center flex-1">
              {[
                { label: 'CPU', val: `${cpu}%`, percent: cpu },
                { label: 'RAM', val: `${(ram.used/(1024*1024*1024)).toFixed(1)} GB / ${(ram.total/(1024*1024*1024)).toFixed(1)} GB`, percent: ram.percent },
                { label: 'DISK', val: `${(disk.used/(1024*1024*1024)).toFixed(0)} GB / ${(disk.total/(1024*1024*1024)).toFixed(0)} GB`, percent: disk.percent }
              ].map(bar => (
                <div key={bar.label} className="flex flex-col gap-1">
                  <div className="flex justify-between font-hud text-[11px] tracking-wider">
                    <span className="text-cyber-muted">{bar.label}</span>
                    <span className="text-cyber-blue [text-shadow:0_0_5px_rgba(0,187,255,0.3)]">{bar.val}</span>
                  </div>
                  <div className="h-[6px] bg-cyber-deep/40 border border-cyber-blue/10 rounded-full overflow-hidden relative">
                    <div 
                      className="h-full bg-gradient-to-r from-cyber-blue to-cyber-cyan shadow-[0_0_8px_#00bbff] rounded-full transition-all duration-700 relative after:content-[''] after:absolute after:top-0 after:right-0 after:bottom-0 after:w-1 after:bg-white after:shadow-[0_0_6px_#fff]" 
                      style={{ width: `${bar.percent}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          {/* NETWORK */}
          <div className="bg-cyber-card border border-cyber-blue/15 rounded-lg flex flex-col p-4 shadow-glow hover:border-cyber-blue/30 transition-colors duration-300 flex-[1.1]">
            <div className="flex items-center gap-[10px] pb-3 border-b border-cyber-blue/10 mb-4 relative after:content-[''] after:absolute after:bottom-[-1px] after:left-0 after:w-10 after:height-[1px] after:bg-cyber-blue after:[box-shadow:0_0_5px_#00bbff]">
              <svg viewBox="0 0 24 24" className="w-4 h-4 fill-cyber-blue filter drop-shadow-[0_0_3px_#00bbff]"><path d="M15.9 5c-.17 0-.32.09-.41.23l-3.32 5.54a.8.8 0 0 0 0 .86l3.32 5.54c.09.14.24.23.41.23H22V5h-6.1zM2 12c0 4.41 3.59 8 8 8a7.93 7.93 0 0 0 4.9-1.72l-1.39-2.32A5.22 5.22 0 0 1 10 17c-2.76 0-5-2.24-5-5s2.24-5 5-5c1.47 0 2.78.64 3.71 1.66l1.39-2.32A7.93 7.93 0 0 0 10 4c-4.41 0-8 3.59-8 8z"/></svg>
              <h2 className="font-hud text-[13px] font-semibold tracking-wider text-white">NETWORK</h2>
            </div>
            
            <div className="flex flex-col gap-4 flex-1 justify-center">
              <div className="grid grid-cols-2 gap-3">
                {[
                  { lbl: 'Upload', val: netUpload },
                  { lbl: 'Download', val: netDownload }
                ].map(n => (
                  <div key={n.lbl} className="flex flex-col bg-cyber-deep/35 border border-cyber-blue/5 rounded p-[8px_10px] relative before:content-[''] before:absolute before:top-0 before:left-0 before:w-[2px] before:h-full before:bg-cyber-blue">
                    <span className="text-[11px] uppercase text-cyber-muted tracking-wider">{n.lbl}</span>
                    <span className="font-hud text-[15px] font-semibold text-white [text-shadow:0_0_6px_rgba(0,187,255,0.35)] mt-[2px]">{n.val}</span>
                  </div>
                ))}
              </div>
              <div className="h-[55px] border border-cyber-blue/5 bg-cyber-deep/30 rounded overflow-hidden">
                <canvas ref={canvasRef} className="w-full h-full block" />
              </div>
            </div>
          </div>

          {/* WEATHER */}
          <div className="bg-cyber-card border border-cyber-blue/15 rounded-lg flex flex-col p-4 shadow-glow hover:border-cyber-blue/30 transition-colors duration-300 flex-[1.3]">
            <div className="flex items-center gap-[10px] pb-3 border-b border-cyber-blue/10 mb-4 relative after:content-[''] after:absolute after:bottom-[-1px] after:left-0 after:w-10 after:height-[1px] after:bg-cyber-blue after:[box-shadow:0_0_5px_#00bbff]">
              <svg viewBox="0 0 24 24" className="w-4 h-4 fill-cyber-blue filter drop-shadow-[0_0_3px_#00bbff]"><path d="M6.75 20.25h10.5a4.5 4.5 0 0 0 2.94-7.91A6 6 0 0 0 9 6.22 6.75 6.75 0 0 0 6.75 20.25z"/></svg>
              <h2 className="font-hud text-[13px] font-semibold tracking-wider text-white">WEATHER</h2>
            </div>
            
            <div className="grid grid-cols-[1.2fr_0.8fr] gap-x-[10px] flex-1 justify-center">
              <div>
                <div className="font-hud text-[32px] font-extrabold text-white [text-shadow:0_0_8px_rgba(0,187,255,0.4)] leading-[1.1]">{weather.temp.toFixed(1)}°C</div>
                <div className="text-[13px] text-cyber-muted font-semibold mt-[2px] tracking-[0.5px]">{weather.city}, {weather.country}</div>
                <div className="text-[12px] text-cyber-cyan uppercase tracking-wider mt-[2px]">{weather.condition}</div>
              </div>
              <div className="flex justify-center items-center">
                <div className="relative w-[50px] h-[40px]">
                  <div className="w-[40px] h-[15px] bg-cyber-text/70 rounded-full absolute bottom-0 left-0 shadow-[0_0_10px_rgba(226,241,255,0.3)] z-[2] before:content-[''] before:bg-cyber-text/70 before:absolute before:rounded-full before:w-[20px] before:h-[20px] before:top-[-10px] before:left-[6px] after:content-[''] after:bg-cyber-text/70 after:absolute after:rounded-full after:w-[24px] after:h-[24px] after:top-[-13px] after:right-[6px]" />
                  <div className="w-[22px] h-[22px] bg-gradient-to-br from-[#ffe359] to-[#ff9000] rounded-full absolute top-[-6px] right-[2px] z-[1] shadow-[0_0_15px_#ff9000] animate-spin-sun" />
                </div>
              </div>
              <div className="col-span-2 grid grid-cols-3 gap-[5px] border-t border-cyber-blue/10 pt-2 mt-2">
                {[
                  { lbl: '💧 Humid', val: `${weather.humidity}%` },
                  { lbl: '💨 Wind', val: `${weather.wind.toFixed(1)} k/h` },
                  { lbl: '🌡️ Feels', val: `${weather.feels_like.toFixed(1)}°` }
                ].map(detail => (
                  <div key={detail.lbl} className="flex flex-col items-center bg-cyber-deep/20 rounded py-1">
                    <span className="text-[10px] text-cyber-muted">{detail.lbl}</span>
                    <span className="font-hud text-[11px] text-white mt-[2px]">{detail.val}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* UPTIME */}
          <div className="bg-cyber-card border border-cyber-blue/15 rounded-lg flex flex-col p-4 shadow-glow hover:border-cyber-blue/30 transition-colors duration-300 flex-[0.8]">
            <div className="flex items-center gap-[10px] pb-3 border-b border-cyber-blue/10 mb-2 relative after:content-[''] after:absolute after:bottom-[-1px] after:left-0 after:w-10 after:height-[1px] after:bg-cyber-blue after:[box-shadow:0_0_5px_#00bbff]">
              <svg viewBox="0 0 24 24" className="w-4 h-4 fill-cyber-blue filter drop-shadow-[0_0_3px_#00bbff]"><path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/></svg>
              <h2 className="font-hud text-[13px] font-semibold tracking-wider text-white">UPTIME</h2>
            </div>
            
            <div className="flex flex-col items-center justify-center flex-1 text-center">
              <div className="font-hud text-[28px] font-extrabold text-cyber-cyan [text-shadow:0_0_10px_rgba(0,240,255,0.4)] tracking-[2px]">{formatUptime(uptime)}</div>
              <div className="text-[10px] text-cyber-muted tracking-[0.5px] uppercase mt-1">System operations secure</div>
            </div>
          </div>
          
        </section>
        
        {/* CENTER COLUMN: HOLOGRAM VIEWPORT & CONTROL CONTROLS */}
        <section className="flex flex-col h-full min-h-0">
          
          <div className="flex-1 bg-gradient-to-b from-cyber-deep/50 to-[rgba(1,6,18,0.9)] border border-cyber-blue/20 rounded-lg relative overflow-hidden flex flex-col justify-center items-center shadow-[inset_0_0_30px_rgba(0,187,255,0.15),0_0_15px_rgba(0,187,255,0.25)]">
            
            {/* HUD Backdrops */}
            <div className="absolute inset-0 bg-[linear-gradient(rgba(0,187,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(0,187,255,0.03)_1px,transparent_1px)] bg-[size:20px_20px] bg-center pointer-events-none z-[1]" />
            <div className="absolute inset-0 bg-radial-gradient pointer-events-none z-[1] bg-[radial-gradient(circle_at_50%_50%,rgba(0,187,255,0.08)_0%,transparent_60%)]" />
            
            {/* Floating Hologram SVG */}
            <div className="w-[320px] h-[320px] relative z-[2] flex justify-center items-center">
              <svg className={`w-full h-full block overflow-visible transition-all duration-300 ${getAvatarClasses()}`} viewBox="0 0 400 400">
                <defs>
                  <filter id="glow-filter" x="-20%" y="-20%" width="140%" height="140%">
                    <feGaussianBlur stdDeviation="6" result="blur" />
                    <feMerge>
                      <feMergeNode in="blur" />
                      <feMergeNode in="SourceGraphic" />
                    </feMerge>
                  </filter>
                </defs>
                
                {/* HUD RINGS */}
                <circle cx="200" cy="200" r="170" className="fill-none stroke-cyber-blue stroke-[1.5px] opacity-40 animate-rotate-cw [transform-origin:200px_200px]" style={{ strokeDasharray: '100, 150' }} />
                <circle cx="200" cy="200" r="150" className="fill-none stroke-cyber-blue stroke-[1px] opacity-30 animate-rotate-ccw [transform-origin:200px_200px]" style={{ strokeDasharray: '20, 10, 5, 10' }} />
                <circle cx="200" cy="200" r="130" className="fill-none stroke-cyber-blue stroke-[1px] opacity-20 animate-rotate-cw-fast [transform-origin:200px_200px]" style={{ strokeDasharray: '4, 8' }} />
                
                {/* Horizontal Scan Bar */}
                <line x1="50" y1="200" x2="350" y2="200" className="stroke-cyber-cyan/40 stroke-[1.5px] filter drop-shadow-[0_0_3px_#00f0ff] animate-scan-vertical" />
                
                {/* Face Mesh Contour */}
                <g filter="url(#glow-filter)" className="transition-all duration-500">
                  <path 
                    d="M130,120 Q120,60 200,60 Q280,60 270,120 Q280,240 230,290 L220,320 L180,320 L170,290 Q120,240 130,120 Z" 
                    className="fill-none stroke-[1.8px] transition-colors duration-500"
                    style={{ stroke: getMeshColor(), opacity: 0.65 }}
                  />
                  
                  {/* Eyes */}
                  <circle cx="165" cy="140" r="16" className="fill-none stroke-[1px] opacity-50" style={{ stroke: getMeshColor() }} />
                  <circle cx="165" cy="140" r="4" className="animate-eye-blink" style={{ fill: getMeshColor(), filter: `drop-shadow(0 0 4px ${getMeshColor()})` }} />
                  <circle cx="235" cy="140" r="16" className="fill-none stroke-[1px] opacity-50" style={{ stroke: getMeshColor() }} />
                  <circle cx="235" cy="140" r="4" className="animate-eye-blink" style={{ fill: getMeshColor(), filter: `drop-shadow(0 0 4px ${getMeshColor()})` }} />
                  
                  {/* Grid mappings */}
                  <line x1="200" y1="60" x2="200" y2="110" className="fill-none stroke-[1.2px] opacity-45" style={{ stroke: getMeshColor() }} />
                  <path d="M160,90 L200,110 L240,90" className="fill-none stroke-[1.2px] opacity-45" style={{ stroke: getMeshColor() }} />
                  
                  {/* Nose */}
                  <path d="M200,110 L200,210 L185,225 L215,225 Z" className="fill-none stroke-[1.2px] opacity-45" style={{ stroke: getMeshColor() }} />
                  
                  {/* Cheek mappings */}
                  <path d="M135,160 Q160,200 170,230" className="fill-none stroke-[1.2px] opacity-45" style={{ stroke: getMeshColor() }} />
                  <path d="M265,160 Q240,200 230,230" className="fill-none stroke-[1.2px] opacity-45" style={{ stroke: getMeshColor() }} />
                  
                  {/* Jaw */}
                  <path d="M150,250 L180,290 L220,290 L250,250" className="fill-none stroke-[1.2px] opacity-45" style={{ stroke: getMeshColor() }} />
                  
                  {/* Mouth Speech Wave */}
                  <path 
                    d={getMouthD()} 
                    className={`fill-none stroke-2 stroke-linecap-round opacity-80 ${hologramState === 'listening' ? 'animate-mouth-listening' : hologramState === 'speaking' ? 'animate-mouth-speaking' : ''}`}
                    style={{ stroke: getMeshColor() }}
                  />
                  
                  {/* Nodes */}
                  {[
                    { cx: 200, cy: 60 }, { cx: 165, cy: 140 }, { cx: 235, cy: 140 },
                    { cx: 200, cy: 110 }, { cx: 200, cy: 210 }, { cx: 180, cy: 290 }, { cx: 220, cy: 290 }
                  ].map((node, i) => (
                    <circle key={i} cx={node.cx} cy={node.cy} r={i === 0 || i === 3 || i === 4 ? 3 : 2} className="opacity-80" style={{ fill: getMeshColor(), filter: `drop-shadow(0 0 2px ${getMeshColor()})` }} />
                  ))}
                </g>
              </svg>
            </div>
            
            {/* Hologram labels */}
            <div className="absolute bottom-[25px] flex flex-col items-center gap-[5px] pointer-events-none z-[3]">
              <h1 className="font-hud text-[26px] font-extrabold tracking-[8px] text-white [text-shadow:0_0_10px_rgba(0,187,255,0.6)] text-center">JARVIS</h1>
              <div className={`flex items-center gap-[8px] bg-cyber-deep/60 border rounded px-[15px] py-1 transition-all duration-300 ${getStatusColor()}`}>
                <span className={`w-[6px] h-[6px] rounded-full ${getPulseColor()} ${hologramState !== 'idle' ? 'animate-pulse-dot' : ''}`}></span>
                <span className="font-hud text-[11px] tracking-wider uppercase">{getStatusText()}</span>
              </div>
            </div>
            
          </div>
          
          {/* CONTROL SWITCH PANEL */}
          <div className="flex justify-center gap-[18px] py-[15px] pb-1 z-[3]">
            {[
              { id: 'btn-camera', lbl: 'Camera', active: cameraActive, set: setCameraActive, path: "M9 2L7.17 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2h-3.17L15 2H9zm3 15c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5z" },
              { id: 'btn-voice', lbl: 'Voice', active: micActive, toggle: toggleMic, path: "M12 14c1.66 0 2.99-1.34 2.99-3L15 5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm5.3-3c0 3-2.54 5.1-5.3 5.1S6.7 14 6.7 11H5c0 3.41 2.72 6.23 6 6.72V21h2v-3.28c3.28-.48 6-3.3 6-6.72h-1.7z" },
              { id: 'btn-keyboard', lbl: 'Keyboard', active: keyboardActive, set: setKeyboardActive, path: "M20 5H4c-1.1 0-1.99.9-1.99 2L2 17c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm-9 3h2v2h-2V8zm0 3h2v2h-2v-2zM8 8h2v2H8V8zm0 3h2v2H8v-2zm-1 2H5v-2h2v2zm0-3H5V8h2v2zm9 7H8v-2h8v2zm0-4h-2v-2h2v2zm0-3h-2V8h2v2zm3 4h-2v-2h2v2zm0-3h-2V8h2v2z" }
            ].map(btn => (
              <button 
                key={btn.id}
                onClick={() => {
                  if (btn.toggle) btn.toggle();
                  else btn.set(p => !p);
                }}
                className={`bg-cyber-deep/40 border rounded-lg w-[75px] h-[75px] flex flex-col justify-center items-center gap-[8px] cursor-pointer relative overflow-hidden transition-all duration-300 hover:border-cyber-cyan/40 hover:-translate-y-1 hover:shadow-[0_5px_15px_rgba(0,240,255,0.15)] ${btn.active ? 'border-cyber-cyan bg-cyber-cyan/10 shadow-[0_0_15px_rgba(0,240,255,0.2)]' : 'border-cyber-blue/15'} group`}
              >
                <div className="absolute inset-0 bg-radial-gradient opacity-0 transition-opacity duration-300 group-hover:opacity-100 bg-[radial-gradient(circle,rgba(0,187,255,0.15)_0%,transparent_70%)]" />
                <svg viewBox="0 0 24 24" className={`w-[22px] h-[22px] transition-all duration-300 z-10 ${btn.active ? 'fill-cyber-cyan filter drop-shadow-[0_0_4px_#00f0ff]' : 'fill-cyber-muted group-hover:fill-cyber-cyan group-hover:scale-110'}`}>
                  <path d={btn.path} />
                </svg>
                <span className={`text-[10px] tracking-wider uppercase z-10 transition-colors duration-300 ${btn.active ? 'text-white font-semibold' : 'text-cyber-muted group-hover:text-cyber-text'}`}>{btn.lbl}</span>
              </button>
            ))}
          </div>
          
        </section>
        
        {/* RIGHT COLUMN: CONVERSATION PANEL */}
        <section className="flex flex-col h-full min-h-0">
          
          <div className="bg-cyber-card border border-cyber-blue/15 rounded-lg flex flex-col h-full shadow-glow hover:border-cyber-blue/30 transition-colors duration-300 overflow-hidden">
            <div className="flex justify-between items-center px-4 py-3 border-b border-cyber-blue/10 bg-cyber-deep/20 relative after:content-[''] after:absolute after:bottom-[-1px] after:left-0 after:w-10 after:height-[1px] after:bg-cyber-blue after:[box-shadow:0_0_5px_#00bbff]">
              <div className="flex items-center gap-[10px]">
                <svg viewBox="0 0 24 24" className="w-4 h-4 fill-cyber-blue filter drop-shadow-[0_0_3px_#00bbff]"><path d="M20 2H4c-1.1 0-1.99.9-1.99 2L2 22l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zM6 9h12v2H6V9zm8 5H6v-2h8v2zm4-6H6V6h12v2z"/></svg>
                <h2 className="font-hud text-[13px] font-semibold tracking-wider text-white">CONVERSATION</h2>
              </div>
              <div className="flex gap-2">
                <button onClick={() => setMessages([])} className="bg-cyber-blue/5 border border-cyber-blue/20 rounded text-cyber-muted font-labels text-[11px] font-semibold px-2 py-[2px] cursor-pointer hover:bg-cyber-cyan/12 hover:border-cyber-cyan hover:text-white hover:shadow-[0_0_6px_rgba(0,240,255,0.25)] transition-all duration-200">🗑️ Clear</button>
                <button onClick={exportChat} className="bg-cyber-blue/5 border border-cyber-blue/20 rounded text-cyber-muted font-labels text-[11px] font-semibold px-2 py-[2px] cursor-pointer hover:bg-cyber-cyan/12 hover:border-cyber-cyan hover:text-white hover:shadow-[0_0_6px_rgba(0,240,255,0.25)] transition-all duration-200">💾 Export</button>
              </div>
            </div>
            
            {/* Conversation Messages */}
            <div className="flex-1 overflow-y-auto p-4 bg-cyber-deep/40 flex flex-col gap-3">
              <div className="flex flex-col gap-[14px]">
                {messages.map((m, i) => (
                  <div key={i} className={`flex gap-3 max-w-[85%] animate-msg-slide ${m.sender === 'Jarvis' ? 'self-start' : 'self-end flex-row-reverse'}`}>
                    <div className={`w-7 h-7 rounded-full flex justify-center items-center font-hud text-[12px] font-bold border ${
                      m.sender === 'Jarvis' 
                        ? 'bg-cyber-blue/10 border-cyber-blue text-cyber-blue shadow-[0_0_5px_rgba(0,187,255,0.3)]' 
                        : 'bg-cyber-cyan/15 border-cyber-cyan text-cyber-cyan shadow-[0_0_5px_rgba(0,240,255,0.3)]'
                    }`}>{m.sender === 'Jarvis' ? 'J' : 'U'}</div>
                    <div className="flex flex-col gap-1">
                      <div className={`text-[13px] leading-relaxed p-[10px_14px] rounded-xl break-words ${
                        m.sender === 'Jarvis'
                          ? 'bg-cyber-deep/60 border border-cyber-blue/10 text-cyber-text rounded-tl-sm'
                          : 'bg-cyber-blue/10 border border-cyber-cyan/20 text-white rounded-tr-sm shadow-[0_0_10px_rgba(0,187,255,0.05)]'
                      }`}>{m.text}</div>
                      <span className={`text-[9px] text-cyber-dim ${m.sender === 'Jarvis' ? 'self-start' : 'self-end'}`}>{m.time}</span>
                    </div>
                  </div>
                ))}
                <div ref={chatEndRef} />
              </div>
            </div>
            
            {/* Conversation Inputs */}
            <div className="p-3 border-t border-cyber-blue/10 bg-cyber-deep/30">
              <form onSubmit={sendCommand} className="flex gap-2 bg-cyber-deep/60 border border-cyber-blue/15 rounded-md p-1 focus-within:border-cyber-cyan focus-within:shadow-[0_0_10px_rgba(0,240,255,0.2)] transition-all duration-300">
                <input 
                  type="text" 
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  placeholder="Type a command or ask a question..." 
                  className="flex-1 bg-transparent border-none outline-none text-white font-labels text-[13px] px-[10px] py-2"
                />
                <button type="submit" className="bg-gradient-to-br from-cyber-blue to-[#0077ff] border-none rounded w-8 h-8 flex justify-center items-center cursor-pointer transition-all duration-300 hover:brightness-[1.2] hover:shadow-[0_0_8px_#00bbff] hover:scale-105">
                  <svg viewBox="0 0 24 24" className="w-[14px] h-[14px] fill-white">
                    <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                  </svg>
                </button>
              </form>
            </div>
            
          </div>
          
        </section>
        
      </main>
      
      {/* --- COLLAPSIBLE LOG DRAWER TERMINAL --- */}
      <footer className={`fixed bottom-0 left-[15px] right-[15px] h-[220px] bg-cyber-deep/95 border border-cyber-blue/20 border-b-0 rounded-t-lg shadow-[0_-5px_25px_rgba(0,187,255,0.15)] flex flex-col transition-transform duration-350 z-50 backdrop-blur-md ${terminalOpen ? 'translate-y-0' : 'translate-y-[182px]'}`}>
        <div 
          onClick={() => setTerminalOpen(!terminalOpen)}
          className="flex justify-between items-center px-[18px] py-[10px] border-b border-cyber-blue/15 cursor-pointer"
        >
          <div className="flex items-center gap-[10px] font-hud text-[11px] tracking-wider text-cyber-cyan">
            <span className="w-[6px] h-[6px] rounded-full bg-cyber-cyan shadow-[0_0_6px_#00f0ff] animate-blink-dot"></span>
            <span>SYSTEM LOG STREAM</span>
          </div>
          <div className="flex items-center gap-[15px]">
            <button 
              onClick={(e) => { e.stopPropagation(); setLogs([{ text: '[Logs Cleared by Administrator]', type: 'info' }]); }}
              className="bg-cyber-blue/5 border border-cyber-blue/20 rounded text-cyber-muted font-labels text-[10px] px-[6px] py-[1px] cursor-pointer hover:bg-cyber-cyan/10 hover:border-cyber-cyan hover:text-white"
            >
              Clear Logs
            </button>
            <label className="text-[10px] text-cyber-muted flex items-center gap-1 cursor-pointer" onClick={e => e.stopPropagation()}>
              <input 
                type="checkbox" 
                checked={autoscroll}
                onChange={() => setAutoscroll(!autoscroll)}
                className="cursor-pointer accent-cyber-blue" 
              />
              Auto-Scroll
            </label>
            <button className="bg-none border-none cursor-pointer flex justify-center items-center w-5 h-5">
              <svg viewBox="0 0 24 24" className={`w-4 h-4 fill-cyber-muted transition-transform duration-350 ${terminalOpen ? 'rotate-180' : 'rotate-0'}`}>
                <path d="M7 14l5-5 5 5z"/>
              </svg>
            </button>
          </div>
        </div>
        
        <div className="flex-1 overflow-y-auto px-[18px] py-3 bg-[#000206]/50">
          <pre className="font-mono text-[11px] leading-relaxed text-cyber-muted whitespace-pre-wrap break-all">
            {logs.map((log, index) => {
              let classColor = "";
              if (log.type === 'error') classColor = "text-red-500";
              else if (log.type === 'success') classColor = "text-cyber-green";
              else if (log.type === 'info') classColor = "text-cyber-cyan";
              return (
                <span key={index} className={classColor}>
                  {log.text}{"\n"}
                </span>
              );
            })}
            <div ref={logEndRef} />
          </pre>
        </div>
      </footer>
      
    </div>
  );
}
