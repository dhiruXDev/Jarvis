import React, { useState, useEffect, useRef, useCallback } from 'react';
import AnalysingLoader from './Component/AnalysingLoader';
import { ComposableMap, Geographies, Geography, Marker } from 'react-simple-maps';

const geoUrl = "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json";

const getFlagEmoji = (countryCode) => {
  if (!countryCode) return '📍';
  const codePoints = countryCode
    .toUpperCase()
    .split('')
    .map(char => 127397 + char.charCodeAt(0));
  return String.fromCodePoint(...codePoints);
};

export default function App() {
  // --- STATE ---
  const [hologramMode, setHologramMode] = useState('core'); // 'core' | 'spectrum' | 'mapping' | 'matrix'
  const [coreSync, setCoreSync] = useState(99.42);
  const [isAnalyzing, setIsAnalyzing] = useState(true);
  const [time, setTime] = useState('12:00:00 AM');
  const [date, setDate] = useState('May 22, 2026');
  const [uptime, setUptime] = useState(0);
  const [backendStatus, setBackendStatus] = useState('Offline');

  const [cpu, setCpu] = useState(0);
  const [ram, setRam] = useState({ used: 0, total: 0, percent: 0 });
  const [disk, setDisk] = useState({ used: 0, total: 0, percent: 0 });
  const [netUpload, setNetUpload] = useState('0.0 Mbps');
  const [netDownload, setNetDownload] = useState('0.0 Mbps');

  const [location, setLocation] = useState({
    city: 'Detecting...',
    region: '',
    country: '',
    country_code: '',
    lat: 0.0,
    lng: 0.0
  });
  const [battery, setBattery] = useState({
    percent: 100,
    plugged: true
  });
  const [networkInfo, setNetworkInfo] = useState({
    status: 'ONLINE',
    type: 'WIFI'
  });
  const [bluetoothInfo, setBluetoothInfo] = useState({
    status: 'READY'
  });
  const [hardware, setHardware] = useState({
    cpu_temp: 45,
    gpu_temp: 40,
    fan_speed: 1000,
    power: 45
  });

  // Real-time network speed for canvas wave modulation
  const netUploadKb = useRef(0);
  const netDownloadKb = useRef(0);

  // Weather Info
  const [weather, setWeather] = useState({
    temp: 0.0,
    city: 'Detecting...',
    country: '',
    condition: 'Detecting...',
    humidity: 0,
    wind: 0.0,
    feels_like: 0.0
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
    { text: 'SYSTEM BOOT', type: 'info', time: '12:59:59' },
    { text: 'CORE SYSTEMS ONLINE', type: 'success', time: '13:00:01' },
    { text: 'SECURITY PROTOCOLS ACTIVE', type: 'info', time: '13:00:05' },
    { text: 'NETWORK CONNECTED', type: 'success', time: '13:00:07' },
    { text: 'ALL SYSTEMS NOMINAL', type: 'info', time: '13:00:10' }
  ]);
  const [autoscroll, setAutoscroll] = useState(true);

  // --- REFS ---
  const canvasRef = useRef(null);
  const chatEndRef = useRef(null);
  const logEndRef = useRef(null);
  const hologramTimer = useRef(null);
  const sseRef = useRef(null);
  const hologramModeRef = useRef('core');
  const mousePosRef = useRef({ x: 0, y: 0, cx: 0, cy: 0, isHovered: false, isDown: false, lastX: 0, lastY: 0 });
  const dragPhysicsRef = useRef({ velocityX: 0, velocityY: 0, angleX: 0, angleY: 0 });
  const ripplesRef = useRef([]);

  const handleAnalysisFinished = useCallback(() => {
    setIsAnalyzing(false);
    fetch('/api/ready', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    }).catch(err => {
      console.error("Failed to notify ready state:", err);
    });
  }, []);

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
    const canvas = hologramCanvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let animationFrameId;

    // 1. Generate Fibonacci sphere coordinates (normalized on unit sphere)
    const pointCount = 280;
    const points = [];
    for (let i = 0; i < pointCount; i++) {
      const phi = Math.acos(1 - 2 * (i + 0.5) / pointCount);
      const theta = Math.PI * (1 + Math.sqrt(5)) * i;
      points.push({
        x: Math.cos(theta) * Math.sin(phi),
        y: Math.sin(theta) * Math.sin(phi),
        z: Math.cos(phi),
        // rotated coordinates
        rx: 0,
        ry: 0,
        rz: 0,
        // projected coordinates
        px: 0,
        py: 0
      });
    }

    // 2. Precompute edges (connections) for the 3D wireframe mesh
    const edges = [];
    const maxDistance = 0.23; // normalized distance threshold
    for (let i = 0; i < pointCount; i++) {
      for (let j = i + 1; j < pointCount; j++) {
        const dx = points[i].x - points[j].x;
        const dy = points[i].y - points[j].y;
        const dz = points[i].z - points[j].z;
        const d = Math.sqrt(dx * dx + dy * dy + dz * dz);
        if (d < maxDistance) {
          edges.push([i, j]);
        }
      }
    }

    // 3. Pre-generate cyber matrix columns
    const matrixColsCount = 35;
    const matrixCols = [];
    for (let i = 0; i < matrixColsCount; i++) {
      matrixCols.push({
        x: (Math.random() - 0.5) * 600,
        y: (Math.random() - 0.5) * 600,
        z: Math.random() * 800,
        speed: 1.5 + Math.random() * 3,
        chars: Array.from({ length: 12 }, () => Math.random() > 0.5 ? '1' : '0')
      });
    }

    // 4. Precompute fixed nodes for radar mapping
    const radarNodes = [
      { label: 'SPEECH_CORE', angle: 0.5, dist: 130, active: true },
      { label: 'AI_BRAIN', angle: 2.1, dist: 80, active: true },
      { label: 'DISK_LOG', angle: -1.2, dist: 170, active: false },
      { label: 'WEATHER_API', angle: 3.8, dist: 200, active: true },
      { label: 'GEO_LOCATOR', angle: -2.7, dist: 110, active: true },
      { label: 'SSE_STREAM', angle: 1.4, dist: 220, active: true },
      { label: 'NET_SOCKET', angle: 5.3, dist: 150, active: false }
    ];

    // Animation states
    let wavePhase = 0;
    let speechAmp = 0; // modulated audio amplitude

    const resizeCanvas = () => {
      canvas.width = canvas.parentElement.clientWidth;
      canvas.height = canvas.parentElement.clientHeight;
    };
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Mouse Listeners
    const handleMouseMove = (e) => {
      const rect = canvas.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      const cx = x - canvas.width / 2;
      const cy = y - canvas.height / 2;

      const mPos = mousePosRef.current;
      if (mPos.isDown) {
        const dx = x - mPos.x;
        const dy = y - mPos.y;
        dragPhysicsRef.current.velocityX = dx * 0.003;
        dragPhysicsRef.current.velocityY = dy * 0.003;
      }

      mousePosRef.current = {
        ...mPos,
        x,
        y,
        cx,
        cy,
        lastX: mPos.x,
        lastY: mPos.y
      };
    };

    const handleMouseDown = (e) => {
      mousePosRef.current.isDown = true;
      const rect = canvas.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      // Spawn ripple
      ripplesRef.current.push({
        x,
        y,
        radius: 0,
        maxRadius: 80 + Math.random() * 40,
        speed: 3 + Math.random() * 2,
        alpha: 1
      });
    };

    const handleMouseUp = () => {
      mousePosRef.current.isDown = false;
    };

    const handleMouseEnter = () => {
      mousePosRef.current.isHovered = true;
    };

    const handleMouseLeave = () => {
      mousePosRef.current.isHovered = false;
      mousePosRef.current.isDown = false;
    };

    canvas.addEventListener('mousemove', handleMouseMove);
    canvas.addEventListener('mousedown', handleMouseDown);
    canvas.addEventListener('mouseup', handleMouseUp);
    canvas.addEventListener('mouseenter', handleMouseEnter);
    canvas.addEventListener('mouseleave', handleMouseLeave);

    const draw = () => {
      if (!canvas.width) return;
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      const state = hologramStateRef.current;
      const mode = hologramModeRef.current;
      const width = canvas.width;
      const height = canvas.height;
      const cx = width / 2;
      const cy = height / 2;

      // Dynamic speeds, sizes, and wave amplitudes depending on J.A.R.V.I.S. state
      let speedX = 0.002;
      let speedY = 0.003;
      let baseSphereRadius = 100;
      let waveAmp = 5;
      let scaleFreq = 1.0;

      if (state === 'listening') {
        speedX = 0.005;
        speedY = 0.007;
        baseSphereRadius = 105;
        waveAmp = 38; // High wavelength height when user is speaking
        scaleFreq = 2.4; // Dense frequency oscillations
      } else if (state === 'speaking') {
        speedX = 0.003;
        speedY = 0.005;
        baseSphereRadius = 102;
        const targetAmp = 26 + Math.sin(wavePhase * 0.15) * 20 + Math.cos(wavePhase * 0.06) * 14;
        speechAmp = speechAmp * 0.75 + targetAmp * 0.25;
        const isPausing = Math.sin(wavePhase * 0.05) < -0.85;
        waveAmp = isPausing ? 4 : speechAmp;
        scaleFreq = isPausing ? 0.8 : 1.2;
        baseSphereRadius += waveAmp * 0.12;
      } else if (state === 'processing' || state === 'recognizing') {
        speedX = 0.010;
        speedY = 0.012;
        baseSphereRadius = 98;
        waveAmp = 12;
        scaleFreq = 2.0;
      } else {
        speedX = 0.0015;
        speedY = 0.0022;
        baseSphereRadius = 96;
        waveAmp = 4;
        scaleFreq = 0.8;
      }

      // Update drag physics
      const physics = dragPhysicsRef.current;
      physics.angleX += physics.velocityX;
      physics.angleY += physics.velocityY;
      physics.velocityX *= 0.94;
      physics.velocityY *= 0.94;

      // Apply auto-rotation as a background drift
      physics.angleX += speedX;
      physics.angleY += speedY;

      // Keep angles clean
      physics.angleX %= Math.PI * 2;
      physics.angleY %= Math.PI * 2;

      wavePhase += 0.07;

      const getThemeRGB = (s) => {
        if (s === 'listening') return '57, 255, 20'; // cyber-green (user speaking)
        if (s === 'speaking') return '255, 0, 128'; // cyber-magenta/pink (Jarvis speaking)
        if (s === 'processing' || s === 'recognizing') return '255, 153, 0'; // cyber-orange
        return '0, 187, 255'; // cyber-blue
      };

      const rgb = getThemeRGB(state);

      // ==========================================
      // RENDER MODE: CORE (Fibonacci Sphere & Orbitals)
      // ==========================================
      if (mode === 'core') {
        // 1. Draw central radial glow
        const coreGlow = ctx.createRadialGradient(cx, cy, 0, cx, cy, 45 + Math.sin(wavePhase * 0.1) * 8);
        coreGlow.addColorStop(0, `rgba(${rgb}, 0.65)`);
        coreGlow.addColorStop(0.3, `rgba(${rgb}, 0.35)`);
        coreGlow.addColorStop(0.7, `rgba(${rgb}, 0.1)`);
        coreGlow.addColorStop(1, 'rgba(0,0,0,0)');
        ctx.fillStyle = coreGlow;
        ctx.beginPath();
        ctx.arc(cx, cy, 65, 0, Math.PI * 2);
        ctx.fill();

        // 2. Rotate & Project Sphere Points
        const cosX = Math.cos(physics.angleX);
        const sinX = Math.sin(physics.angleX);
        const cosY = Math.cos(physics.angleY);
        const sinY = Math.sin(physics.angleY);
        const fov = 160;

        points.forEach(p => {
          const y1 = p.y * cosX - p.z * sinX;
          const z1 = p.z * cosX + p.y * sinX;
          const x2 = p.x * cosY - z1 * sinY;
          const z2 = z1 * cosY + p.x * sinY;
          p.rx = x2;
          p.ry = y1;
          p.rz = z2;

          const scale = fov / (fov + z2 * baseSphereRadius * 0.7);
          p.px = cx + x2 * baseSphereRadius * scale;
          p.py = cy + y1 * baseSphereRadius * scale;
        });

        // 3. Draw 3D wireframe mesh
        ctx.lineWidth = 0.55;
        edges.forEach(([i, j]) => {
          const pi = points[i];
          const pj = points[j];
          const avgZ = (pi.rz + pj.rz) / 2;
          if (avgZ > 0.6) return;

          const opacity = Math.max(0, 1 - (avgZ + 0.8) / 1.6) * 0.16;
          ctx.strokeStyle = `rgba(${rgb}, ${opacity})`;
          ctx.beginPath();
          ctx.moveTo(pi.px, pi.py);
          ctx.lineTo(pj.px, pj.py);
          ctx.stroke();
        });

        // 4. Draw sphere particles
        points.forEach((p, idx) => {
          const opacity = Math.max(0.08, 1 - (p.rz + 0.8) / 1.8) * 0.75;
          const isHighlight = idx % 12 === 0;
          let size = (1.5 - p.rz) * 0.85;
          if (isHighlight) size *= 1.8;

          ctx.beginPath();
          ctx.arc(p.px, p.py, size, 0, Math.PI * 2);
          ctx.fillStyle = isHighlight ? `rgba(255, 255, 255, ${opacity * 0.95})` : `rgba(${rgb}, ${opacity})`;
          ctx.fill();

          if (isHighlight && p.rz < 0.2) {
            ctx.beginPath();
            ctx.arc(p.px, p.py, size * 2.2, 0, Math.PI * 2);
            ctx.strokeStyle = `rgba(${rgb}, ${opacity * 0.4})`;
            ctx.lineWidth = 0.6;
            ctx.stroke();
          }
        });

        // 5. Draw electrical synaptic jumps
        if (Math.random() < 0.08) {
          const i1 = Math.floor(Math.random() * pointCount);
          const i2 = Math.floor(Math.random() * pointCount);
          const p1 = points[i1];
          const p2 = points[i2];
          const dx = p1.px - p2.px;
          const dy = p1.py - p2.py;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist > 30 && dist < 120 && p1.rz < 0.3 && p2.rz < 0.3) {
            ctx.strokeStyle = `rgba(255, 255, 255, 0.75)`;
            ctx.lineWidth = 0.8;
            ctx.beginPath();
            ctx.moveTo(p1.px, p1.py);

            const mx = (p1.px + p2.px) / 2;
            const my = (p1.py + p2.py) / 2;
            const offsetAmt = 8;
            const ox = mx + (Math.random() - 0.5) * offsetAmt;
            const oy = my + (Math.random() - 0.5) * offsetAmt;

            ctx.lineTo(ox, oy);
            ctx.lineTo(p2.px, p2.py);
            ctx.stroke();
          }
        }

        // 6. Draw 3D orbital rings
        const drawOrbitalRing = (radius, tiltX, tiltY, rotateSpeed, dashPattern = []) => {
          ctx.beginPath();
          const ringAngle = wavePhase * rotateSpeed;
          const pointsCount = 72;
          ctx.lineWidth = 1.0;
          ctx.strokeStyle = `rgba(${rgb}, 0.28)`;
          if (dashPattern.length) ctx.setLineDash(dashPattern);

          for (let i = 0; i <= pointsCount; i++) {
            const theta = (i / pointsCount) * Math.PI * 2 + ringAngle;
            let rx = Math.cos(theta) * radius;
            let ry = Math.sin(theta) * radius;
            let rz = 0;

            const cosY = Math.cos(tiltY);
            const sinY = Math.sin(tiltY);
            const rx1 = rx * cosY - rz * sinY;
            const rz1 = rz * cosY + rx * sinY;

            const cosX = Math.cos(tiltX);
            const sinX = Math.sin(tiltX);
            const ry2 = ry * cosX - rz1 * sinX;
            const rz2 = rz1 * cosX + ry * sinX;

            const scale = fov / (fov + rz2 * radius * 0.003);
            const px = cx + rx1 * scale;
            const py = cy + ry2 * scale;

            if (i === 0) ctx.moveTo(px, py);
            else ctx.lineTo(px, py);
          }
          ctx.stroke();
          ctx.setLineDash([]);
        };

        drawOrbitalRing(145, 0.8, 0.4, 0.02, [5, 10]);
        drawOrbitalRing(185, -0.5, 0.7, -0.015, [15, 8]);

        // 7. Draw Orbiting Satellites
        const drawSatellite = (radius, tiltX, tiltY, speed, size) => {
          const theta = (wavePhase * speed) % (Math.PI * 2);
          let rx = Math.cos(theta) * radius;
          let ry = Math.sin(theta) * radius;
          let rz = 0;

          const cosY = Math.cos(tiltY);
          const sinY = Math.sin(tiltY);
          const rx1 = rx * cosY - rz * sinY;
          const rz1 = rz * cosY + rx * sinY;

          const cosX = Math.cos(tiltX);
          const sinX = Math.sin(tiltX);
          const ry2 = ry * cosX - rz1 * sinX;
          const rz2 = rz1 * cosX + ry * sinX;

          const scale = fov / (fov + rz2 * radius * 0.003);
          const px = cx + rx1 * scale;
          const py = cy + ry2 * scale;

          ctx.fillStyle = `rgba(${rgb}, ${rz2 > 0 ? 0.35 : 0.95})`;
          ctx.beginPath();
          ctx.arc(px, py, size, 0, Math.PI * 2);
          ctx.fill();

          for (let t = 1; t <= 5; t++) {
            const trailTheta = theta - t * 0.04 * (speed > 0 ? 1 : -1);
            let trx = Math.cos(trailTheta) * radius;
            let try_ = Math.sin(trailTheta) * radius;
            let trz = 0;

            const tr_rx1 = trx * cosY - trz * sinY;
            const tr_rz1 = trz * cosY + trx * sinY;
            const tr_ry2 = try_ * cosX - tr_rz1 * sinX;
            const tr_rz2 = tr_rz1 * cosX + try_ * sinX;

            const tr_scale = fov / (fov + tr_rz2 * radius * 0.003);
            const tr_px = cx + tr_rx1 * tr_scale;
            const tr_py = cy + tr_ry2 * tr_scale;

            ctx.fillStyle = `rgba(${rgb}, ${0.15 / t})`;
            ctx.beginPath();
            ctx.arc(tr_px, tr_py, size * 0.7, 0, Math.PI * 2);
            ctx.fill();
          }
        };

        drawSatellite(145, 0.8, 0.4, 0.4, 3);
        drawSatellite(185, -0.5, 0.7, -0.3, 3.5);

        // 8. Circular sound visualizer
        const ringRadius = 78;
        const barsCount = 64;
        ctx.lineWidth = 1.8;

        for (let i = 0; i < barsCount; i++) {
          const angle = (i / barsCount) * Math.PI * 2 + wavePhase * 0.15;
          let barHeight = 2;
          if (state === 'speaking') {
            barHeight = 2 + Math.abs(Math.sin(i * 0.3 + wavePhase * 1.5)) * waveAmp * 0.85;
          } else if (state === 'listening') {
            barHeight = 2 + Math.abs(Math.cos(i * 0.2 + wavePhase * 2.2)) * waveAmp * 0.75;
          } else if (state === 'processing' || state === 'recognizing') {
            barHeight = 2 + Math.abs(Math.sin(i * 0.5 + wavePhase * 3.0)) * 6;
          } else {
            barHeight = 2 + Math.abs(Math.sin(i * 0.1 + wavePhase * 0.5)) * 2;
          }

          const startX = cx + Math.cos(angle) * ringRadius;
          const startY = cy + Math.sin(angle) * ringRadius;
          const endX = cx + Math.cos(angle) * (ringRadius + barHeight);
          const endY = cy + Math.sin(angle) * (ringRadius + barHeight);

          ctx.strokeStyle = `rgba(${rgb}, ${0.3 + (barHeight / (waveAmp + 2)) * 0.7})`;
          ctx.beginPath();
          ctx.moveTo(startX, startY);
          ctx.lineTo(endX, endY);
          ctx.stroke();
        }
      }

      // ==========================================
      // RENDER MODE: SPECTRUM (Vertical Audio Waves & Grid)
      // ==========================================
      else if (mode === 'spectrum') {
        // 1. Draw background grid
        ctx.strokeStyle = "rgba(0, 187, 255, 0.05)";
        ctx.lineWidth = 0.8;
        const step = 40;
        for (let x = 0; x < width; x += step) {
          ctx.beginPath();
          ctx.moveTo(x, 0);
          ctx.lineTo(x, height);
          ctx.stroke();
        }
        for (let y = 0; y < height; y += step) {
          ctx.beginPath();
          ctx.moveTo(0, y);
          ctx.lineTo(width, y);
          ctx.stroke();
        }

        // 2. Draw horizontal multi-sine oscilloscope
        const waveLayers = [
          { freq: 0.008, amp: waveAmp * 2.2, speed: 0.05, opacity: 0.6, lineW: 2.2 },
          { freq: 0.015, amp: waveAmp * 1.3, speed: -0.08, opacity: 0.35, lineW: 1.2 },
          { freq: 0.025, amp: waveAmp * 0.8, speed: 0.12, opacity: 0.2, lineW: 1.0 },
          { freq: 0.004, amp: waveAmp * 3.2, speed: 0.02, opacity: 0.15, lineW: 0.8 }
        ];

        waveLayers.forEach((w) => {
          ctx.strokeStyle = `rgba(${rgb}, ${w.opacity})`;
          ctx.lineWidth = w.lineW;
          ctx.beginPath();

          for (let x = 0; x < width; x += 3) {
            const t = x / width;
            const env = Math.exp(-Math.pow((t - 0.5) / 0.38, 2));
            let y = cy + Math.sin(x * w.freq + wavePhase * w.speed) * w.amp * env;

            if (mousePosRef.current.isHovered) {
              const mx = mousePosRef.current.x;
              const dx = x - mx;
              const cursorDist = Math.abs(dx);
              if (cursorDist < 100) {
                const influence = (1 - cursorDist / 100) * env;
                y += Math.sin(x * 0.15 + wavePhase * 0.4) * 25 * influence;
              }
            }

            if (x === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
          }
          ctx.stroke();
        });

        // 3. Draw bottom frequency column bars
        const barW = 4;
        const gap = 2;
        const barCount = Math.floor(width / (barW + gap));
        ctx.fillStyle = `rgba(${rgb}, 0.22)`;

        for (let i = 0; i < barCount; i++) {
          const t = i / barCount;
          const env = Math.exp(-Math.pow((t - 0.5) / 0.45, 2));
          let barH = 5 + Math.sin(i * 0.15 + wavePhase) * 15 * env;
          barH += Math.cos(i * 0.4 - wavePhase * 1.5) * 8 * env;
          barH = Math.max(3, barH);

          if (state === 'speaking') barH *= 1.8;
          else if (state === 'listening') barH *= 2.2;
          else if (state === 'processing') barH *= 1.4;

          const bx = i * (barW + gap);
          const by = height - barH - 22;

          ctx.fillRect(bx, by, barW, barH);

          ctx.fillStyle = `rgba(${rgb}, 0.65)`;
          ctx.fillRect(bx, by - 3, barW, 1.5);
          ctx.fillStyle = `rgba(${rgb}, 0.22)`;
        }
      }

      // ==========================================
      // RENDER MODE: MAPPING (Scifi Radar Scanning Grid)
      // ==========================================
      else if (mode === 'mapping') {
        // 1. Draw radar coordinate rings
        ctx.strokeStyle = `rgba(${rgb}, 0.12)`;
        ctx.lineWidth = 1.0;
        const radarRadii = [60, 120, 180, 240];
        radarRadii.forEach(r => {
          ctx.beginPath();
          ctx.arc(cx, cy, r, 0, Math.PI * 2);
          ctx.stroke();

          ctx.strokeStyle = `rgba(${rgb}, 0.05)`;
          ctx.beginPath();
          ctx.moveTo(cx - r, cy); ctx.lineTo(cx + r, cy);
          ctx.moveTo(cx, cy - r); ctx.lineTo(cx, cy + r);
          ctx.stroke();
          ctx.strokeStyle = `rgba(${rgb}, 0.12)`;
        });

        // 2. Rotating radar sweep line
        const sweepAngle = (wavePhase * 0.06) % (Math.PI * 2);
        const sweepLen = 250;
        const sx = cx + Math.cos(sweepAngle) * sweepLen;
        const sy = cy + Math.sin(sweepAngle) * sweepLen;

        ctx.strokeStyle = `rgba(${rgb}, 0.85)`;
        ctx.lineWidth = 1.6;
        ctx.beginPath();
        ctx.moveTo(cx, cy);
        ctx.lineTo(sx, sy);
        ctx.stroke();

        // 3. Draw gradient tail sweep
        for (let s = 1; s <= 20; s++) {
          const tailAngle = sweepAngle - s * 0.018;
          const tsx = cx + Math.cos(tailAngle) * sweepLen;
          const tsy = cy + Math.sin(tailAngle) * sweepLen;
          ctx.strokeStyle = `rgba(${rgb}, ${0.45 / s})`;
          ctx.lineWidth = 1.0;
          ctx.beginPath();
          ctx.moveTo(cx, cy);
          ctx.lineTo(tsx, tsy);
          ctx.stroke();
        }

        // 4. Draw node maps
        radarNodes.forEach((node) => {
          const nx = cx + Math.cos(node.angle) * node.dist;
          const ny = cy + Math.sin(node.angle) * node.dist;

          // Radar proximity check
          const angleDiff = Math.abs((sweepAngle - node.angle + Math.PI * 4) % (Math.PI * 2) - Math.PI);
          const sweepProx = Math.exp(-Math.pow((angleDiff - Math.PI) / 0.15, 2));
          const alpha = Math.max(0.18, sweepProx * 0.95);

          ctx.strokeStyle = node.active ? `rgba(${rgb}, ${alpha})` : `rgba(239, 68, 68, ${alpha})`;
          ctx.fillStyle = node.active ? `rgba(${rgb}, ${alpha * 0.2})` : `rgba(239, 68, 68, ${alpha * 0.2})`;
          ctx.lineWidth = 1.0;

          const size = 5;
          ctx.beginPath();
          ctx.arc(nx, ny, size, 0, Math.PI * 2);
          ctx.fill();
          ctx.stroke();

          if (sweepProx > 0.6) {
            ctx.strokeStyle = `rgba(${rgb}, ${sweepProx * 0.15})`;
            ctx.beginPath();
            ctx.moveTo(cx, cy);
            ctx.lineTo(nx, ny);
            ctx.stroke();
          }

          ctx.font = "bold 8px Orbitron";
          ctx.fillStyle = node.active ? `rgba(${rgb}, ${alpha})` : `rgba(239, 68, 68, ${alpha})`;
          ctx.fillText(node.label, nx + 10, ny + 3);

          ctx.font = "500 7px Rajdhani";
          ctx.fillStyle = `rgba(156, 163, 175, ${alpha})`;
          ctx.fillText(`D:${node.dist}m // A:${node.angle.toFixed(2)}r`, nx + 10, ny + 11);
        });
      }

      // ==========================================
      // RENDER MODE: MATRIX (3D Perspective Code Rain)
      // ==========================================
      else if (mode === 'matrix') {
        ctx.font = "bold 10px Orbitron";
        matrixCols.forEach((col) => {
          col.z -= col.speed;
          if (col.z <= -100) {
            col.z = 800;
            col.x = (Math.random() - 0.5) * 600;
            col.y = (Math.random() - 0.5) * 600;
          }

          const fov = 200;
          const scale = fov / (fov + col.z);
          const px = cx + col.x * scale;
          const py = cy + col.y * scale;

          col.chars.forEach((char, idx) => {
            const charOffset = idx * 12 * scale;
            const cpy = py + charOffset;

            if (px < 0 || px > width || cpy < 0 || cpy > height) return;
            const depthOpacity = Math.max(0, Math.min(1.0, 1 - col.z / 800));

            let fillStyle;
            if (idx === 0) fillStyle = `rgba(255, 255, 255, ${depthOpacity * 0.95})`;
            else if (idx < 4) fillStyle = `rgba(${rgb}, ${depthOpacity * 0.85})`;
            else fillStyle = `rgba(0, 119, 255, ${depthOpacity * (0.6 - idx * 0.04)})`;

            ctx.fillStyle = fillStyle;
            ctx.font = `bold ${Math.max(6, 11 * scale)}px Orbitron`;

            if (Math.random() < 0.05) {
              col.chars[idx] = Math.random() > 0.6
                ? (Math.random() > 0.5 ? '1' : '0')
                : String.fromCharCode(33 + Math.floor(Math.random() * 40));
            }

            ctx.fillText(char, px, cpy);
          });
        });
      }

      // ==========================================
      // OVERLAY: INTERACTIVE MOUSE TARGET RETICLE
      // ==========================================
      const mPos = mousePosRef.current;
      if (mPos.isHovered) {
        ctx.strokeStyle = `rgba(${rgb}, 0.85)`;
        ctx.lineWidth = 1.0;

        const rx = mPos.x;
        const ry = mPos.y;
        const size = 8;
        const gap = 4;

        ctx.beginPath();
        ctx.moveTo(rx - size, ry - gap); ctx.lineTo(rx - gap, ry - gap); ctx.lineTo(rx - gap, ry - size);
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(rx + size, ry - gap); ctx.lineTo(rx + gap, ry - gap); ctx.lineTo(rx + gap, ry - size);
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(rx - size, ry + gap); ctx.lineTo(rx - gap, ry + gap); ctx.lineTo(rx - gap, ry + size);
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(rx + size, ry + gap); ctx.lineTo(rx + gap, ry + gap); ctx.lineTo(rx + gap, ry + size);
        ctx.stroke();

        ctx.fillStyle = `rgba(${rgb}, 0.9)`;
        ctx.beginPath();
        ctx.arc(rx, ry, 1.5, 0, Math.PI * 2);
        ctx.fill();

        ctx.font = "bold 8px Fira Code";
        ctx.fillStyle = `rgba(${rgb}, 0.8)`;
        const coordX = Math.round(mPos.cx);
        const coordY = Math.round(-mPos.cy);
        ctx.fillText(`X:${coordX} Y:${coordY}`, rx + 14, ry - 4);

        ctx.font = "500 7px Rajdhani";
        ctx.fillStyle = "rgba(156, 163, 175, 0.75)";
        ctx.fillText("GRID_LOCK // SEC:D", rx + 14, ry + 6);

        if (mode === 'core') {
          ctx.strokeStyle = `rgba(${rgb}, 0.18)`;
          ctx.setLineDash([2, 4]);
          ctx.beginPath();
          ctx.moveTo(cx, cy);
          ctx.lineTo(rx, ry);
          ctx.stroke();
          ctx.setLineDash([]);
        }
      }

      // ==========================================
      // OVERLAY: CLICK RIPPLES (Expanding shockwaves)
      // ==========================================
      const activeRipples = ripplesRef.current;
      ripplesRef.current = activeRipples.filter((ripple) => {
        ripple.radius += ripple.speed;
        ripple.alpha = 1 - ripple.radius / ripple.maxRadius;

        if (ripple.alpha <= 0) return false;

        ctx.strokeStyle = `rgba(${rgb}, ${ripple.alpha})`;
        ctx.lineWidth = 1.2;
        ctx.beginPath();
        ctx.arc(ripple.x, ripple.y, ripple.radius, 0, Math.PI * 2);
        ctx.stroke();

        ctx.strokeStyle = `rgba(${rgb}, ${ripple.alpha * 0.4})`;
        ctx.setLineDash([4, 8]);
        ctx.beginPath();
        ctx.arc(ripple.x, ripple.y, ripple.radius * 1.2, 0, Math.PI * 2);
        ctx.stroke();
        ctx.setLineDash([]);

        return true;
      });

      animationFrameId = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      window.removeEventListener('resize', resizeCanvas);
      canvas.removeEventListener('mousemove', handleMouseMove);
      canvas.removeEventListener('mousedown', handleMouseDown);
      canvas.removeEventListener('mouseup', handleMouseUp);
      canvas.removeEventListener('mouseenter', handleMouseEnter);
      canvas.removeEventListener('mouseleave', handleMouseLeave);
      cancelAnimationFrame(animationFrameId);
    };
  }, [isAnalyzing]);

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
      const now = new Date();
      const timestamp = now.toTimeString().split(' ')[0]; // "HH:MM:SS"
      return [...prev, { text: cleanText, type: finalType, time: timestamp }];
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

          if (stats.location) {
            setLocation(stats.location);
          }
          if (stats.battery) {
            setBattery(stats.battery);
          }
          if (stats.network) {
            setNetworkInfo({
              status: stats.network.status || 'ONLINE',
              type: stats.network.type || 'WIFI'
            });
          }
          if (stats.bluetooth) {
            setBluetoothInfo(stats.bluetooth);
          }
          if (stats.hardware) {
            setHardware(stats.hardware);
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

  // Store the current hologramState in a ref to keep animation loops fluid and continuous
  const hologramStateRef = useRef(hologramState);
  useEffect(() => {
    hologramStateRef.current = hologramState;
  }, [hologramState]);

  // Sync hologramMode to its ref
  useEffect(() => {
    hologramModeRef.current = hologramMode;
  }, [hologramMode]);

  // Animate the core sync metric
  useEffect(() => {
    const syncInterval = setInterval(() => {
      setCoreSync(prev => {
        const delta = (Math.random() - 0.5) * 0.08;
        const next = Math.max(98.30, Math.min(99.95, prev + delta));
        return parseFloat(next.toFixed(2));
      });
    }, 1500);
    return () => clearInterval(syncInterval);
  }, []);

  // Upgraded Hologram 3D Sphere & Voice Wave Canvas Effect
  const hologramCanvasRef = useRef(null);

  useEffect(() => {
    const canvas = hologramCanvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let animationFrameId;

    // 1. Generate Fibonacci sphere coordinates (normalized on unit sphere)
    const pointCount = 280;
    const points = [];
    for (let i = 0; i < pointCount; i++) {
      const phi = Math.acos(1 - 2 * (i + 0.5) / pointCount);
      const theta = Math.PI * (1 + Math.sqrt(5)) * i;
      points.push({
        x: Math.cos(theta) * Math.sin(phi),
        y: Math.sin(theta) * Math.sin(phi),
        z: Math.cos(phi),
        // rotated coordinates
        rx: 0,
        ry: 0,
        rz: 0,
        // projected coordinates
        px: 0,
        py: 0
      });
    }

    // 2. Precompute edges (connections) for the 3D wireframe mesh
    const edges = [];
    const maxDistance = 0.23; // normalized distance threshold
    for (let i = 0; i < pointCount; i++) {
      for (let j = i + 1; j < pointCount; j++) {
        const dx = points[i].x - points[j].x;
        const dy = points[i].y - points[j].y;
        const dz = points[i].z - points[j].z;
        const d = Math.sqrt(dx * dx + dy * dy + dz * dz);
        if (d < maxDistance) {
          edges.push([i, j]);
        }
      }
    }

    // Animation states
    let angleX = 0;
    let angleY = 0;
    let wavePhase = 0;
    let speechAmp = 0; // modulated audio amplitude

    const draw = () => {
      if (!canvas.width) return;
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      const state = hologramStateRef.current;
      const width = canvas.width;
      const height = canvas.height;
      const cx = width / 2;
      const cy = height / 2;

      // Dynamic speeds, sizes, and wave amplitudes depending on J.A.R.V.I.S. state
      let speedX = 0.002;
      let speedY = 0.003;
      let baseSphereRadius = 100;
      let waveAmp = 5;
      let scaleFreq = 1.0;

      if (state === 'listening') {
        speedX = 0.005;
        speedY = 0.007;
        baseSphereRadius = 105;
        waveAmp = 20;
        scaleFreq = 1.6;
      } else if (state === 'speaking') {
        speedX = 0.003;
        speedY = 0.005;
        baseSphereRadius = 102;
        // Modulated speech energy simulation (speech waveforms are dynamic)
        const targetAmp = 22 + Math.sin(wavePhase * 0.15) * 18 + Math.cos(wavePhase * 0.06) * 12;
        speechAmp = speechAmp * 0.75 + targetAmp * 0.25;

        // Let's add occasional speech pauses
        const isPausing = Math.sin(wavePhase * 0.05) < -0.85;
        waveAmp = isPausing ? 4 : speechAmp;
        scaleFreq = isPausing ? 0.8 : 1.2;
        baseSphereRadius += waveAmp * 0.12; // breathing effect reacting to speech energy!
      } else if (state === 'processing' || state === 'recognizing') {
        speedX = 0.010;
        speedY = 0.012;
        baseSphereRadius = 98;
        waveAmp = 12;
        scaleFreq = 2.0;
      } else {
        // Idle
        speedX = 0.0015;
        speedY = 0.0022;
        baseSphereRadius = 96;
        waveAmp = 4;
        scaleFreq = 0.8;
      }

      // Update rotation angles
      angleX += speedX;
      angleY += speedY;
      wavePhase += 0.07;

      // A dynamic color mapping function
      const getThemeRGB = (s) => {
        if (s === 'listening') return '0, 240, 255'; // cyber-cyan
        if (s === 'speaking') return '224, 163, 255'; // cyber-magenta (purple)
        if (s === 'processing' || s === 'recognizing') return '255, 153, 0'; // cyber-orange
        return '0, 187, 255'; // cyber-blue
      };

      const rgb = getThemeRGB(state);

      // --- 1. ROTATE & PROJECT SPHERE POINTS ---
      const cosX = Math.cos(angleX);
      const sinX = Math.sin(angleX);
      const cosY = Math.cos(angleY);
      const sinY = Math.sin(angleY);
      const fov = 160;

      points.forEach(p => {
        // X rotation
        const y1 = p.y * cosX - p.z * sinX;
        const z1 = p.z * cosX + p.y * sinX;
        // Y rotation
        const x2 = p.x * cosY - z1 * sinY;
        const z2 = z1 * cosY + p.x * sinY;

        p.rx = x2;
        p.ry = y1;
        p.rz = z2;

        // Perspective projection
        const scale = fov / (fov + z2 * baseSphereRadius * 0.7);
        p.px = cx + x2 * baseSphereRadius * scale;
        p.py = cy + y1 * baseSphereRadius * scale;
      });

      // --- 2. DRAW 3D MESH LINES (EDGES) ---
      ctx.lineWidth = 0.55;
      edges.forEach(([i, j]) => {
        const pi = points[i];
        const pj = points[j];

        // Depth test (fade out mesh connections at the back)
        const avgZ = (pi.rz + pj.rz) / 2;
        if (avgZ > 0.6) return; // clip very back connections for visual clarity

        const opacity = Math.max(0, 1 - (avgZ + 0.8) / 1.6) * 0.16;
        ctx.strokeStyle = `rgba(${rgb}, ${opacity})`;
        ctx.beginPath();
        ctx.moveTo(pi.px, pi.py);
        ctx.lineTo(pj.px, pj.py);
        ctx.stroke();
      });

      // --- 3. DRAW SPHERE PARTICLES ---
      points.forEach((p, idx) => {
        // Opacity based on depth Z: front is bright, back is dim
        const opacity = Math.max(0.08, 1 - (p.rz + 0.8) / 1.8) * 0.75;

        // Highlight about 8% of the nodes with extra glow & size
        const isHighlight = idx % 12 === 0;
        let size = (1.5 - p.rz) * 0.85;
        if (isHighlight) size *= 1.8;

        ctx.beginPath();
        ctx.arc(p.px, p.py, size, 0, 2 * Math.PI);
        ctx.fillStyle = isHighlight ? `rgba(255, 255, 255, ${opacity * 0.95})` : `rgba(${rgb}, ${opacity})`;
        ctx.fill();

        // Extra glowing ring for highlight nodes
        if (isHighlight && p.rz < 0.2) {
          ctx.beginPath();
          ctx.arc(p.px, p.py, size * 2.2, 0, 2 * Math.PI);
          ctx.strokeStyle = `rgba(${rgb}, ${opacity * 0.4})`;
          ctx.lineWidth = 0.6;
          ctx.stroke();
        }
      });

      // --- 4. DRAW HORIZONTAL GLOWING AUDIO VOICE WAVE ---
      // A) Vertical bar fill
      ctx.lineWidth = 1.6;
      for (let x = width * 0.08; x < width * 0.92; x += 3.5) {
        const t = x / width;
        // Gaussian bell curve envelope to taper wave at left/right boundaries
        const env = Math.exp(-Math.pow((t - 0.5) / 0.28, 2));

        // Combined multi-frequency wave formula
        const waveVal = Math.sin(x * 0.024 * scaleFreq + wavePhase) * 0.55 +
          Math.cos(x * 0.012 * scaleFreq - wavePhase * 0.7) * 0.30 +
          Math.sin(x * 0.048 * scaleFreq + wavePhase * 1.4) * 0.15;

        // Calculate symmetrical wave height
        const h = Math.max(1.5, Math.abs(waveVal) * waveAmp * env);

        // Alpha glows stronger at the center
        const alpha = (0.2 + env * 0.65) * 0.45;
        ctx.strokeStyle = `rgba(${rgb}, ${alpha})`;

        ctx.beginPath();
        ctx.moveTo(x, cy - h);
        ctx.lineTo(x, cy + h);
        ctx.stroke();
      }

      // B) Continuous boundary curves (top/bottom)
      ctx.lineWidth = 1.5;
      ctx.strokeStyle = `rgba(${rgb}, 0.85)`;

      // Top boundary path
      ctx.beginPath();
      for (let x = width * 0.05; x <= width * 0.95; x += 2) {
        const t = x / width;
        const env = Math.exp(-Math.pow((t - 0.5) / 0.28, 2));
        const waveVal = Math.sin(x * 0.024 * scaleFreq + wavePhase) * 0.55 +
          Math.cos(x * 0.012 * scaleFreq - wavePhase * 0.7) * 0.30 +
          Math.sin(x * 0.048 * scaleFreq + wavePhase * 1.4) * 0.15;
        const h = Math.abs(waveVal) * waveAmp * env;

        if (x === width * 0.05) ctx.moveTo(x, cy - h);
        else ctx.lineTo(x, cy - h);
      }
      ctx.stroke();

      // Bottom boundary path
      ctx.beginPath();
      for (let x = width * 0.05; x <= width * 0.95; x += 2) {
        const t = x / width;
        const env = Math.exp(-Math.pow((t - 0.5) / 0.28, 2));
        const waveVal = Math.sin(x * 0.024 * scaleFreq + wavePhase) * 0.55 +
          Math.cos(x * 0.012 * scaleFreq - wavePhase * 0.7) * 0.30 +
          Math.sin(x * 0.048 * scaleFreq + wavePhase * 1.4) * 0.15;
        const h = Math.abs(waveVal) * waveAmp * env;

        if (x === width * 0.05) ctx.moveTo(x, cy + h);
        else ctx.lineTo(x, cy + h);
      }
      ctx.stroke();

      // C) Secondary intersecting sine line (asymmetrical, scrolling)
      ctx.lineWidth = 1.0;
      const secColor = state === 'speaking' ? '0, 240, 255' : '224, 163, 255';
      ctx.strokeStyle = `rgba(${secColor}, 0.65)`;
      ctx.beginPath();
      for (let x = width * 0.05; x <= width * 0.95; x += 3) {
        const t = x / width;
        const env = Math.exp(-Math.pow((t - 0.5) / 0.28, 2));
        // Cross weave math
        const waveVal2 = Math.sin(x * 0.035 * scaleFreq - wavePhase * 1.3) * 0.7 +
          Math.cos(x * 0.018 * scaleFreq + wavePhase * 0.9) * 0.3;
        const yOffset = waveVal2 * waveAmp * 0.75 * env;

        if (x === width * 0.05) ctx.moveTo(x, cy + yOffset);
        else ctx.lineTo(x, cy + yOffset);
      }
      ctx.stroke();

      animationFrameId = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      cancelAnimationFrame(animationFrameId);
    };
  }, [isAnalyzing]);

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
    if (hologramState === 'listening') return 'text-cyber-green bg-cyber-green/10 border-cyber-green/35';
    if (hologramState === 'speaking') return 'text-cyber-magenta bg-cyber-magenta/10 border-cyber-magenta/35';
    if (hologramState === 'processing' || hologramState === 'recognizing') return 'text-cyber-orange bg-cyber-orange/10 border-cyber-orange/35';
    return 'text-cyber-muted bg-cyber-muted/5 border-cyber-blue/15';
  };

  const getPulseColor = () => {
    if (hologramState === 'listening') return 'bg-cyber-green shadow-[0_0_10px_#39ff14]';
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
    if (hologramState === 'listening') return '#39ff14';
    if (hologramState === 'speaking') return '#e0a3ff';
    if (hologramState === 'processing' || hologramState === 'recognizing') return '#ff9900';
    return '#00bbff';
  };

  if (isAnalyzing) {
    return <AnalysingLoader onFinished={handleAnalysisFinished} />;
  }

  return (
    <div className="flex flex-col h-screen p-[15px] relative overflow-hidden select-none">

      {/* --- TOP HEADER BAR --- */}
      <header className="flex justify-between items-start w-full px-6 py-0 mb-3 relative z-10 select-none">
        {/* Left Logo Section */}
        <div className="flex items-center gap-3 pt-3">
          <span className="font-hud text-xl font-black tracking-[4px] bg-gradient-to-r from-white via-cyber-blue to-cyber-cyan bg-clip-text text-transparent filter drop-shadow-[0_0_5px_rgba(0,187,255,0.4)]">
            J.A.R.V.I.S.
          </span>
          <div className="flex items-center gap-[5px] px-[8px] py-[2px] rounded-full border border-green-500/30 bg-green-500/10 font-hud text-[9px] tracking-wider text-green-400">
            <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse shadow-[0_0_6px_#22c55e]"></span>
            <span>ONLINE</span>
          </div>
        </div>

        {/* Middle Angled Bevel Box */}
        <div className="hud-header-bevel flex justify-center items-center px-12 py-[8px] min-w-[320px]">
          <span className="font-hud text-[13px] tracking-[3px] text-white [text-shadow:0_0_8px_rgba(0,240,255,0.4)]">
            {time} <span className="mx-2 text-cyber-blue">|</span> {date.toUpperCase()}
          </span>
        </div>

        {/* Right Weather/Settings Section */}
        <div className="flex items-center gap-4 pt-2">
          <div className="flex flex-col items-end text-right font-hud text-[11px] tracking-wider text-cyber-muted">
            <div className="flex items-center gap-2">
              <span className="text-white font-bold text-sm [text-shadow:0_0_6px_rgba(0,240,255,0.3)]">{weather.temp.toFixed(1)}°C</span>
              <span className="text-[10px] uppercase font-semibold">{weather.city || 'PATNA'}</span>
            </div>
            <div className="flex items-center gap-1 text-[9px] text-cyber-dim mt-0.5 uppercase">
              <span className="text-cyber-cyan">💧</span>
              <span>{weather.humidity}% HUMIDITY</span>
            </div>
          </div>
          <button className="bg-cyber-deep/40 border border-cyber-blue/20 rounded-md w-[32px] h-[32px] flex justify-center items-center cursor-pointer transition-all duration-300 hover:border-cyber-cyan hover:shadow-[0_0_8px_rgba(0,240,255,0.3)] hover:rotate-45 group">
            <svg viewBox="0 0 24 24" className="w-[16px] h-[16px] fill-cyber-muted transition-colors duration-300 group-hover:fill-cyber-cyan">
              <path d="M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54c-.04-.24-.24-.41-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.05.3-.09.63-.09.94s.02.64.07.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z" />
            </svg>
          </button>
        </div>
      </header>

      {/* --- MAIN HUD INTERFACE GRID --- */}
      <main className={`grid grid-cols-[28%_44%_28%] gap-[12px] flex-1 min-h-0 transition-[padding-bottom] duration-300 select-none ${terminalOpen ? 'pb-[230px]' : 'pb-[48px]'}`}>

        {/* LEFT COLUMN: SYSTEM INFO, SPEED, STATUS, HARDWARE MONITOR */}
        <section className="flex flex-col gap-[10px] min-h-0">

          {/* SYSTEM OVERVIEW */}
          <div className="hud-panel relative flex flex-col p-3 rounded-lg transition-colors duration-300">
            <div className="scifi-corner scifi-corner-tl"></div>
            <div className="scifi-corner scifi-corner-tr"></div>
            <div className="scifi-corner scifi-corner-bl"></div>
            <div className="scifi-corner scifi-corner-br"></div>

            <div className="flex items-center gap-[8px] pb-1.5 border-b border-cyber-blue/10 mb-2.5 relative after:content-[''] after:absolute after:bottom-[-1px] after:left-0 after:w-8 after:height-[1px] after:bg-cyber-blue after:[box-shadow:0_0_5px_#00bbff]">
              <svg viewBox="0 0 24 24" className="w-3.5 h-3.5 fill-cyber-blue filter drop-shadow-[0_0_3px_#00bbff]"><path d="M21 2H3c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h7l-2 3v1h8v-1l-2-3h7c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H3V4h18v12z" /></svg>
              <h2 className="font-hud text-[11px] font-bold tracking-wider text-white">SYSTEM OVERVIEW</h2>
            </div>

            <div className="flex flex-col gap-2 justify-center">
              {[
                { label: 'CPU', val: `${cpu}%`, percent: cpu },
                { label: 'RAM', val: `${(ram.used / (1024 * 1024 * 1024)).toFixed(1)} GB / ${(ram.total / (1024 * 1024 * 1024)).toFixed(1)} GB`, percent: ram.percent },
                { label: 'DISK', val: `${(disk.used / (1024 * 1024 * 1024)).toFixed(0)} GB / ${(disk.total / (1024 * 1024 * 1024)).toFixed(0)} GB`, percent: disk.percent }
              ].map(bar => (
                <div key={bar.label} className="flex flex-col gap-0.5">
                  <div className="flex justify-between font-hud text-[10px] tracking-wider">
                    <span className="text-cyber-muted font-semibold">{bar.label}</span>
                    <span className="text-cyber-cyan font-bold [text-shadow:0_0_5px_rgba(0,240,255,0.4)]">{bar.val}</span>
                  </div>
                  <div className="h-[4px] bg-cyber-deep/60 border border-cyber-blue/10 rounded-full overflow-hidden relative">
                    <div
                      className="h-full bg-gradient-to-r from-cyber-blue to-cyber-cyan shadow-[0_0_8px_#00f0ff] rounded-full transition-all duration-700"
                      style={{ width: `${bar.percent}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* NETWORK (SPEEDS & VISUALIZERS) */}
          <div className="hud-panel relative flex flex-col p-3 transition-colors duration-300 rounded-lg">
            <div className="scifi-corner scifi-corner-tl"></div>
            <div className="scifi-corner scifi-corner-tr"></div>
            <div className="scifi-corner scifi-corner-bl"></div>
            <div className="scifi-corner scifi-corner-br"></div>

            <div className="flex items-center gap-[8px] pb-1.5 border-b border-cyber-blue/10 mb-2.5 relative after:content-[''] after:absolute after:bottom-[-1px] after:left-0 after:w-8 after:height-[1px] after:bg-cyber-blue after:[box-shadow:0_0_5px_#00bbff]">
              <svg viewBox="0 0 24 24" className="w-3.5 h-3.5 fill-cyber-blue filter drop-shadow-[0_0_3px_#00bbff]"><path d="M19 13H5c-1.1 0-2 .9-2 2v4c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2v-4c0-1.1-.9-2-2-2zM9 17H7v-2h2v2zm4 0h-2v-2h2v2zm4 0h-2v-2h2v2zM12 3L2 12h3v2h14v-2h3L12 3z" /></svg>
              <h2 className="font-hud text-[11px] font-bold tracking-wider text-white">NETWORK</h2>
            </div>

            <div className="grid grid-cols-2 gap-2.5">
              {/* UPLOAD */}
              <div className="bg-cyber-deep/35 border border-cyber-blue/10 rounded p-2 flex flex-col justify-between h-[85px] relative overflow-hidden">
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 rounded-full bg-cyber-cyan/10 border border-cyber-cyan/35 flex justify-center items-center shrink-0">
                    <svg viewBox="0 0 24 24" className="w-3.5 h-3.5 fill-cyber-cyan"><path d="M4 12l1.41 1.41L11 7.83V20h2V7.83l5.58 5.59L20 12l-8-8-8 8z" /></svg>
                  </div>
                  <div>
                    <span className="text-[8px] uppercase text-cyber-muted tracking-wider font-bold block leading-none mb-0.5">UPLOAD</span>
                    <span className="font-hud text-[11px] font-bold text-white [text-shadow:0_0_5px_rgba(0,240,255,0.3)]">{netUpload}</span>
                  </div>
                </div>
                {/* Visualizer bars */}
                <div className="flex items-end justify-between h-4 px-0.5 mt-1">
                  {Array.from({ length: 18 }).map((_, idx) => {
                    const h = Math.max(2, Math.min(10, 3 + Math.sin(idx * 0.5) * 4 + Math.cos(idx * 0.3) * 2));
                    const dur = 0.4 + Math.random() * 0.4;
                    return (
                      <div
                        key={idx}
                        className="w-[1.5px] bg-cyber-cyan rounded-full animate-vis-bar"
                        style={{
                          height: `${h}px`,
                          animationDuration: `${dur}s`,
                          animationDelay: `${idx * 0.02}s`
                        }}
                      />
                    );
                  })}
                </div>
              </div>

              {/* DOWNLOAD */}
              <div className="bg-cyber-deep/35 border border-cyber-blue/10 rounded p-2 flex flex-col justify-between h-[85px] relative overflow-hidden">
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 rounded-full bg-cyber-blue/15 border border-cyber-blue/35 flex justify-center items-center shrink-0">
                    <svg viewBox="0 0 24 24" className="w-3.5 h-3.5 fill-cyber-blue"><path d="M20 12l-1.41-1.41L13 16.17V4h-2v12.17L5.42 10.58 4 12l8 8 8-8z" /></svg>
                  </div>
                  <div>
                    <span className="text-[8px] uppercase text-cyber-muted tracking-wider font-bold block leading-none mb-0.5">DOWNLOAD</span>
                    <span className="font-hud text-[11px] font-bold text-white [text-shadow:0_0_5px_rgba(0,187,255,0.3)]">{netDownload}</span>
                  </div>
                </div>
                {/* Visualizer bars */}
                <div className="flex items-end justify-between h-4 px-0.5 mt-1">
                  {Array.from({ length: 18 }).map((_, idx) => {
                    const h = Math.max(2, Math.min(10, 3 + Math.cos(idx * 0.5) * 4 + Math.sin(idx * 0.3) * 2));
                    const dur = 0.4 + Math.random() * 0.4;
                    return (
                      <div
                        key={idx}
                        className="w-[1.5px] bg-cyber-blue rounded-full animate-vis-bar"
                        style={{
                          height: `${h}px`,
                          animationDuration: `${dur}s`,
                          animationDelay: `${idx * 0.02}s`
                        }}
                      />
                    );
                  })}
                </div>
              </div>
            </div>
          </div>

          {/* SYSTEM STATUS */}
          <div className="hud-panel relative flex flex-col p-3 transition-colors duration-300 rounded-lg">
            <div className="scifi-corner scifi-corner-tl"></div>
            <div className="scifi-corner scifi-corner-tr"></div>
            <div className="scifi-corner scifi-corner-bl"></div>
            <div className="scifi-corner scifi-corner-br"></div>

            <div className="flex items-center gap-[8px] pb-1.5 border-b border-cyber-blue/10 mb-2.5 relative after:content-[''] after:absolute after:bottom-[-1px] after:left-0 after:w-8 after:height-[1px] after:bg-cyber-blue after:[box-shadow:0_0_5px_#00bbff]">
              <svg viewBox="0 0 24 24" className="w-3.5 h-3.5 fill-cyber-blue filter drop-shadow-[0_0_3px_#00bbff]"><path d="M21 3H3c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h5v2h8v-2h5c1.1 0 1.99-.9 1.99-2L23 5c0-1.1-.9-2-2-2zm0 14H3V5h18v12zm-9-2l3-8 3 8h-6zm-3.5-3L6.5 9.5 4 12h5.5z" /></svg>
              <h2 className="font-hud text-[11px] font-bold tracking-wider text-white">SYSTEM STATUS</h2>
            </div>

            <div className="grid grid-cols-4 gap-1 py-0.5">
              {/* BATTERY */}
              <div className="flex flex-col items-center text-center">
                <div className="w-9 h-9 rounded-full border border-cyber-blue/25 bg-cyber-deep/30 flex justify-center items-center mb-1 shadow-[0_0_5px_rgba(0,187,255,0.05)] hover:border-cyber-cyan hover:shadow-[0_0_10px_rgba(0,240,255,0.2)] transition-all duration-300">
                  <svg viewBox="0 0 24 24" className="w-3.5 h-3.5 fill-cyber-cyan"><path d="M15.67 4H14V2h-4v2H8.33C7.6 4 7 4.6 7 5.33v15.33C7 21.4 7.6 22 8.33 22h7.33c.74 0 1.34-.6 1.34-1.33V5.33C17 4.6 16.4 4 15.67 4z" /></svg>
                </div>
                <span className="text-[7.5px] uppercase tracking-wider text-cyber-muted font-bold leading-none">BATTERY</span>
                <span className={`font-hud text-[10px] font-bold mt-0.5 ${battery.percent <= 20 ? 'text-red-500 animate-pulse' : 'text-green-400'}`}>{battery.percent}%</span>
              </div>

              {/* NETWORK */}
              <div className="flex flex-col items-center text-center">
                <div className="w-9 h-9 rounded-full border border-cyber-blue/25 bg-cyber-deep/30 flex justify-center items-center mb-1 shadow-[0_0_5px_rgba(0,187,255,0.05)] hover:border-cyber-cyan hover:shadow-[0_0_10px_rgba(0,240,255,0.2)] transition-all duration-300">
                  <svg viewBox="0 0 24 24" className="w-3.5 h-3.5 fill-cyber-blue"><path d="M2 22h20V2zM20 20h-2V10h2v10zm-4 0h-2V13h2v7zm-4 0h-2v-4h2v4z" /></svg>
                </div>
                <span className="text-[7.5px] uppercase tracking-wider text-cyber-muted font-bold leading-none">NETWORK</span>
                <span className="font-hud text-[10px] font-bold text-green-400 mt-0.5">{networkInfo.status}</span>
              </div>

              {/* CONNECTION */}
              <div className="flex flex-col items-center text-center">
                <div className="w-9 h-9 rounded-full border border-cyber-blue/25 bg-cyber-deep/30 flex justify-center items-center mb-1 shadow-[0_0_5px_rgba(0,187,255,0.05)] hover:border-cyber-cyan hover:shadow-[0_0_10px_rgba(0,240,255,0.2)] transition-all duration-300">
                  <svg viewBox="0 0 24 24" className="w-3.5 h-3.5 fill-cyber-blue"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.53c-.26-.81-1-1.4-1.9-1.4h-1v-3c0-.55-.45-1-1-1h-6v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.4z" /></svg>
                </div>
                <span className="text-[7.5px] uppercase tracking-wider text-cyber-muted font-bold leading-none">CONNECTION</span>
                <span className="font-hud text-[10px] font-bold text-cyber-cyan mt-0.5">{networkInfo.type}</span>
              </div>

              {/* BLUETOOTH */}
              <div className="flex flex-col items-center text-center">
                <div className="w-9 h-9 rounded-full border border-cyber-blue/25 bg-cyber-deep/30 flex justify-center items-center mb-1 shadow-[0_0_5px_rgba(0,187,255,0.05)] hover:border-cyber-cyan hover:shadow-[0_0_10px_rgba(0,240,255,0.2)] transition-all duration-300">
                  <svg viewBox="0 0 24 24" className="w-3.5 h-3.5 fill-cyber-blue"><path d="M17.71 7.71L12 2h-1v7.59L6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 11 14.41V22h1l5.71-5.71-4.3-4.29 4.3-4.29zM13 5.83l1.88 1.88L13 9.59V5.83zm0 12.34v-3.76l1.88 1.88L13 18.17z" /></svg>
                </div>
                <span className="text-[7.5px] uppercase tracking-wider text-cyber-muted font-bold leading-none">BLUETOOTH</span>
                <span className={`font-hud text-[10px] font-bold mt-0.5 ${bluetoothInfo.status === 'READY' ? 'text-green-400' : 'text-cyber-muted'}`}>{bluetoothInfo.status}</span>
              </div>
            </div>
          </div>

          {/* WEATHER CARD */}
          <div className="hud-panel relative flex flex-col p-3.5 transition-colors duration-300 rounded-lg">
            <div className="scifi-corner scifi-corner-tl"></div>
            <div className="scifi-corner scifi-corner-tr"></div>
            <div className="scifi-corner scifi-corner-bl"></div>
            <div className="scifi-corner scifi-corner-br"></div>

            <div className="flex items-center gap-[8px] pb-1.5 border-b border-cyber-blue/10 mb-2 relative after:content-[''] after:absolute after:bottom-[-1px] after:left-0 after:w-8 after:height-[1px] after:bg-cyber-blue after:[box-shadow:0_0_5px_#00bbff]">
              <svg viewBox="0 0 24 24" className="w-3.5 h-3.5 fill-cyber-blue filter drop-shadow-[0_0_3px_#00bbff]">
                <path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96z" />
              </svg>
              <h2 className="font-hud text-[11px] font-bold tracking-wider text-white">WEATHER</h2>
            </div>

            <div className="grid grid-cols-[60%_40%] items-center mb-2.5">
              <div>
                <div className="font-hud text-3xl font-extrabold text-white leading-none tracking-tight">
                  {weather.temp.toFixed(1)}°C
                </div>
                <div className="font-hud text-[11px] text-cyber-muted font-bold mt-1.5 uppercase">
                  {weather.city || 'PATNA'}, {weather.country || 'IN'}
                </div>
                <div className="font-hud text-[9px] text-cyber-cyan font-bold tracking-wider mt-0.5 uppercase">
                  {weather.condition || 'MAINLY CLEAR'}
                </div>
              </div>
              <div className="flex justify-center items-center relative">
                {/* Glowing Sun & Cloud SVG */}
                <svg className="w-[90px] h-[90px] overflow-visible drop-shadow-[0_0_6px_rgba(0,187,255,0.35)]" viewBox="0 0 64 64">
                  <circle cx="38" cy="24" r="10" className="fill-[#ffb703] stroke-[#ff8f00] stroke-[1px] animate-spin-sun" style={{ transformOrigin: '38px 24px' }} />
                  <path d="M 38,8 L 38,11 M 38,37 L 38,40 M 22,24 L 25,24 M 51,24 L 54,24" stroke="#ffb703" strokeWidth="1.5" strokeLinecap="round" />
                  <path d="M46 38c0 3.3-2.7 6-6 6H22c-4.4 0-8-3.6-8-8 0-3.9 2.8-7.1 6.6-7.8C22 23.3 26.2 20 31 20c5.3 0 9.7 3.9 10.4 9 2.6.4 4.6 2.7 4.6 5.3z" className="fill-black/90 stroke-[#00bbff] stroke-[1.5px]" />
                </svg>
              </div>
            </div>

            {/* Weather detail values */}
            <div className="grid grid-cols-3 gap-1.5 pt-2 border-t border-cyber-blue/10 text-center font-hud text-[8.5px]">
              <div className="bg-black/40 border border-cyber-blue/10 rounded py-1 flex flex-col justify-center">
                <span className="text-cyber-muted text-[7.5px] uppercase font-bold tracking-wider">Humid</span>
                <span className="text-white font-bold text-[9.5px] mt-0.5">💧 {weather.humidity}%</span>
              </div>
              <div className="bg-black/40 border border-cyber-blue/10 rounded py-1 flex flex-col justify-center">
                <span className="text-cyber-muted text-[7.5px] uppercase font-bold tracking-wider">Wind</span>
                <span className="text-white font-bold text-[9.5px] mt-0.5">💨 {weather.wind.toFixed(1)} km/h</span>
              </div>
              <div className="bg-black/40 border border-cyber-blue/10 rounded py-1 flex flex-col justify-center">
                <span className="text-cyber-muted text-[7.5px] uppercase font-bold tracking-wider">Feels</span>
                <span className="text-white font-bold text-[9.5px] mt-0.5">🌡️ {weather.feels_like.toFixed(1)}°</span>
              </div>
            </div>
          </div>

          {/* JARVIS SYSTEM UPTIME */}
          <div className="hud-panel relative flex justify-between items-center p-2.5 rounded transition-colors duration-300">
            <div className="scifi-corner scifi-corner-tl"></div>
            <div className="scifi-corner scifi-corner-tr"></div>
            <div className="scifi-corner scifi-corner-bl"></div>
            <div className="scifi-corner scifi-corner-br"></div>
            <div className="flex items-center gap-1.5 select-none">
              <span className="w-1.5 h-1.5 rounded-full bg-cyber-cyan animate-pulse"></span>
              <span className="font-hud text-[9px] font-bold tracking-widest text-cyber-muted uppercase">SYSTEM UPTIME</span>
            </div>
            <span className="font-mono text-xs font-bold text-cyber-cyan [text-shadow:0_0_5px_rgba(0,240,255,0.4)]">{formatUptime(uptime)}</span>
          </div>
        </section>

        {/* CENTER COLUMN: HOLOGRAM VIEWPORT & CONTROL CONTROLS */}
        <section className="flex flex-col h-full min-h-0">

          {/* Hologram screen viewport */}
          <div className="flex-1 bg-black/85 border-2 border-cyber-blue/30 rounded-lg relative overflow-hidden flex flex-col justify-center items-center shadow-[inset_0_0_40px_rgba(0,187,255,0.18)]">

            {/* Corner brackets */}
            <div className="scifi-corner scifi-corner-tl border-l-4 border-t-4 w-5 h-5"></div>
            <div className="scifi-corner scifi-corner-tr border-r-4 border-t-4 w-5 h-5"></div>
            <div className="scifi-corner scifi-corner-bl border-l-4 border-b-4 w-5 h-5"></div>
            <div className="scifi-corner scifi-corner-br border-r-4 border-b-4 w-5 h-5"></div>

            {/* Grid Pattern Backdrop */}
            <div className="absolute inset-0 bg-[linear-gradient(rgba(0,187,255,0.035)_1px,transparent_1px),linear-gradient(90deg,rgba(0,187,255,0.035)_1px,transparent_1px)] bg-[size:16px_16px] pointer-events-none z-[1]" />
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(0,187,255,0.08)_0%,transparent_70%)] pointer-events-none z-[1]" />

            {/* Scanlines overlay */}
            <div className="absolute inset-0 hud-scanline pointer-events-none z-[2]" />

            {/* Hologram Mode Tabs */}
            <div className="absolute top-3.5 left-1/2 transform -translate-x-1/2 flex gap-1.5 z-10">
              {[
                { id: 'core', label: 'NEURAL CORE' },
                { id: 'spectrum', label: 'SPECTRUM' },
                { id: 'mapping', label: 'NEURAL MAPPING' },
                { id: 'matrix', label: 'CYBER MATRIX' }
              ].map(tab => (
                <button
                  key={tab.id}
                  type="button"
                  onClick={() => setHologramMode(tab.id)}
                  className={`hud-tab px-3 py-1 rounded text-[9px] font-hud tracking-widest transition-all duration-200 cursor-pointer font-bold ${hologramMode === tab.id ? 'active' : 'text-cyber-muted'
                    }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Floating Hologram SVG */}
            {hologramMode === 'core' && (
              <div className="absolute w-[300px] h-[300px] pointer-events-none z-[1] flex justify-center items-center">
                {/* Circular HUD Rings Backdrop */}
                <svg className={`absolute w-full h-full block overflow-visible pointer-events-none z-[1] transition-all duration-300 ${getAvatarClasses()}`} viewBox="0 0 400 400">
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
                  <circle cx="200" cy="200" r="175" className="fill-none stroke-cyber-blue stroke-[1.5px] opacity-40 animate-rotate-cw [transform-origin:200px_200px]" style={{ strokeDasharray: '120, 160' }} />
                  <circle cx="200" cy="200" r="155" className="fill-none stroke-cyber-blue stroke-[1px] opacity-30 animate-rotate-ccw [transform-origin:200px_200px]" style={{ strokeDasharray: '30, 15, 10, 15' }} />
                  <circle cx="200" cy="200" r="135" className="fill-none stroke-cyber-cyan stroke-[1px] opacity-20 animate-rotate-cw-fast [transform-origin:200px_200px]" style={{ strokeDasharray: '6, 12' }} />

                  {/* Crosshair target lines */}
                  <line x1="20" y1="200" x2="50" y2="200" className="stroke-cyber-blue/50 stroke-[1px]" />
                  <line x1="350" y1="200" x2="380" y2="200" className="stroke-cyber-blue/50 stroke-[1px]" />
                  <line x1="200" y1="20" x2="200" y2="50" className="stroke-cyber-blue/50 stroke-[1px]" />
                  <line x1="200" y1="350" x2="200" y2="380" className="stroke-cyber-blue/50 stroke-[1px]" />
                </svg>
              </div>
            )}

            {/* 3D Holographic Sphere and Symmetrical Voice Waves Canvas */}
            <canvas
              ref={hologramCanvasRef}
              className="w-full h-full relative z-[2] cursor-crosshair drop-shadow-[0_0_15px_rgba(0,187,255,0.2)]"
            />

            {/* Viewport bottom stats and details overlay */}
            <div className="absolute bottom-3 left-4 right-4 flex justify-between items-end pointer-events-none z-[3] font-hud text-[8.5px] tracking-wider select-none text-cyber-dim">
              <div className="flex flex-col gap-0.5 text-left">
                <div>SYS_MODE: <span className="text-white font-bold">{hologramMode.toUpperCase()}</span></div>
                <div>ACTIVE_PORT: <span className="text-cyber-cyan font-bold">SSE_STREAM_8000</span></div>
              </div>

              {/* Center Label */}
              <div className="flex flex-col items-center">
                <div className="font-hud text-lg font-black tracking-[6px] text-white [text-shadow:0_0_8px_rgba(0,187,255,0.5)] leading-none mb-0.5">
                  J.A.R.V.I.S.
                </div>
                <div className="font-hud text-[8.5px] tracking-[3px] text-cyber-cyan/85 flex items-center gap-1.5 uppercase font-medium">
                  <span>◇</span>
                  <span>{getStatusText()}</span>
                  <span>◇</span>
                </div>
              </div>

              <div className="flex flex-col items-end gap-0.5 text-right">
                <div className="flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-cyber-cyan animate-pulse shadow-[0_0_5px_#00f0ff]"></span>
                  <span>CORE SYNC: <span className="text-cyber-cyan font-bold [text-shadow:0_0_5px_rgba(0,240,255,0.4)]">{coreSync}%</span></span>
                </div>
                <div>STABILITY: <span className="text-green-400 font-bold">NOMINAL</span></div>
              </div>
            </div>

          </div>

          {/* VIEWPORT CONTROLS */}
          <div className="flex justify-center items-end gap-3 py-[10px] pb-1 z-[3]">
            {/* CAMERA BUTTON (LEFT) */}
            <button
              onClick={() => setCameraActive(p => !p)}
              className={`hud-btn-left w-[105px] h-[45px] flex flex-col justify-center items-center gap-[3px] cursor-pointer transition-all duration-300 border-l border-b border-cyber-blue/30 hover:border-cyber-cyan/60 ${cameraActive ? 'border-cyber-cyan filter brightness-125 shadow-[0_0_10px_rgba(0,240,255,0.2)] text-white' : 'text-cyber-muted'}`}
            >
              {/* Shutter Icon */}
              <svg viewBox="0 0 24 24" className={`w-[15px] h-[15px] ${cameraActive ? 'fill-cyber-cyan filter drop-shadow-[0_0_3px_#00f0ff]' : 'fill-cyber-muted'}`}>
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm-1-12.87v4.71l-4.08-2.36 4.08-2.35zM6.16 11h4.71l-2.36 4.08L6.16 11zm5.71 7.15l-4.08-2.36 4.08-2.35v4.71zm5.97-4.27l-4.71.01 2.36-4.08 2.35 4.07zm-1.89-6.02l2.36 4.08h-4.72l2.36-4.08z" />
              </svg>
              <span className="text-[9px] tracking-widest uppercase font-semibold">CAMERA</span>
            </button>

            {/* VOICE COMMAND BUTTON (CENTER - WIDE) */}
            <button
              onClick={toggleMic}
              className={`hud-btn-center w-[170px] h-[52px] flex flex-col justify-center items-center gap-[4px] cursor-pointer transition-all duration-300 border-b border-cyber-blue/40 hover:border-cyber-cyan/70 ${micActive ? 'border-cyber-cyan filter brightness-125 shadow-[0_0_15px_rgba(0,240,255,0.25)] text-white' : 'text-cyber-muted'}`}
            >
              {/* Mic Icon */}
              <svg viewBox="0 0 24 24" className={`w-[17px] h-[17px] ${micActive ? 'fill-cyber-cyan filter drop-shadow-[0_0_4px_#00f0ff] animate-pulse' : 'fill-cyber-muted'}`}>
                <path d="M12 14c1.66 0 2.99-1.34 2.99-3L15 5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm5.3-3c0 3-2.54 5.1-5.3 5.1S6.7 14 6.7 11H5c0 3.41 2.72 6.23 6 6.72V21h2v-3.28c3.28-.48 6-3.3 6-6.72h-1.7z" />
              </svg>
              <span className="text-[9px] tracking-widest uppercase font-bold">VOICE COMMAND</span>
            </button>

            {/* KEYBOARD BUTTON (RIGHT) */}
            <button
              onClick={() => setKeyboardActive(p => !p)}
              className={`hud-btn-right w-[105px] h-[45px] flex flex-col justify-center items-center gap-[3px] cursor-pointer transition-all duration-300 border-r border-b border-cyber-blue/30 hover:border-cyber-cyan/60 ${keyboardActive ? 'border-cyber-cyan filter brightness-125 shadow-[0_0_10px_rgba(0,240,255,0.2)] text-white' : 'text-cyber-muted'}`}
            >
              {/* Keyboard Icon */}
              <svg viewBox="0 0 24 24" className={`w-[15px] h-[15px] ${keyboardActive ? 'fill-cyber-cyan filter drop-shadow-[0_0_3px_#00f0ff]' : 'fill-cyber-muted'}`}>
                <path d="M20 5H4c-1.1 0-1.99.9-1.99 2L2 17c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm-9 3h2v2h-2V8zm0 3h2v2h-2v-2zM8 8h2v2H8V8zm0 3h2v2H8v-2zm-1 2H5v-2h2v2zm0-3H5V8h2v2zm9 7H8v-2h8v2zm0-4h-2v-2h2v2zm0-3h-2V8h2v2zm3 4h-2v-2h2v2zm0-3h-2V8h2v2z" />
              </svg>
              <span className="text-[9px] tracking-widest uppercase font-semibold">KEYBOARD</span>
            </button>
          </div>
        </section>

        {/* RIGHT COLUMN: CONVERSATION PANEL & LOCATION CARD */}
        <section className="flex flex-col gap-[12px] h-full min-h-0">

          {/* LOCATION CARD */}
          <div className="hud-panel relative flex flex-col p-3.5 rounded-lg transition-colors duration-300 overflow-hidden">
            <div className="scifi-corner scifi-corner-tl"></div>
            <div className="scifi-corner scifi-corner-tr"></div>
            <div className="scifi-corner scifi-corner-bl"></div>
            <div className="scifi-corner scifi-corner-br"></div>

            {/* Scifi Radar Background Map using react-simple-maps */}
            <div className="absolute inset-0 pointer-events-none opacity-20 overflow-hidden select-none flex justify-center items-center">
              <div className="w-full h-full scale-[1.1] transform translate-y-1.5">
                <ComposableMap
                  projection="geoMercator"
                  projectionConfig={{
                    scale: 45,
                    center: [0, 20]
                  }}
                  width={320}
                  height={120}
                  style={{ width: "100%", height: "100%" }}
                >
                  <Geographies geography={geoUrl}>
                    {({ geographies }) =>
                      geographies.map((geo) => (
                        <Geography
                          key={geo.rsmKey}
                          geography={geo}
                          fill="rgba(0, 187, 255, 0.08)"
                          stroke="rgba(13, 160, 213, 0.76)"
                          strokeWidth={0.5}
                          style={{
                            default: { outline: "none" },
                            hover: { outline: "none" },
                            pressed: { outline: "none" },
                          }}
                        />
                      ))
                    }
                  </Geographies>
                  {location.lat && location.lng && (
                    <Marker coordinates={[location.lng, location.lat]}>
                      <g className="overflow-visible">
                        {/* Outer pulsing radar wave */}
                        <circle r={12} stroke="#00f0ff" fill="none" className="opacity-90 animate-radar-pulse" strokeWidth={1} style={{ transformOrigin: "0px 0px" }} />

                        {/* Outer dotted target ring */}
                        <circle r={9} stroke="#00f0ff" fill="none" className="opacity-90" strokeWidth={0.8} strokeDasharray="1.5, 1.5" />

                        {/* Inner solid ring */}
                        <circle r={5} stroke="#00f0ff" fill="none" className="opacity-100" strokeWidth={0.8} />

                        {/* Center active coordinate indicator */}
                        <circle r={2.2} fill="#00f0ff" className="animate-pulse" />

                        {/* Crosshair lines */}
                        <line x1={-13} y1={0} x2={13} y2={0} stroke="#00f0ff" className="opacity-80" strokeWidth={0.8} />
                        <line x1={0} y1={-13} x2={0} y2={13} stroke="#00f0ff" className="opacity-80" strokeWidth={0.8} />
                      </g>
                    </Marker>
                  )}
                </ComposableMap>
              </div>
            </div>

            <div className="flex items-center gap-[8px] pb-2 border-b border-cyber-blue/10 mb-3 relative after:content-[''] after:absolute after:bottom-[-1px] after:left-0 after:w-8 after:height-[1px] after:bg-cyber-blue after:[box-shadow:0_0_5px_#00bbff] z-10">
              <svg viewBox="0 0 24 24" className="w-3.5 h-3.5 fill-cyber-blue filter drop-shadow-[0_0_3px_#00bbff]"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z" /></svg>
              <h2 className="font-hud text-[11px] font-bold tracking-wider text-white">LOCATION</h2>
            </div>

            <div className="flex flex-col gap-2.5 z-10">
              <div className="flex items-center gap-3">
                {location.country_code ? (
                  <img
                    src={`https://flagcdn.com/w40/${location.country_code.toLowerCase()}.png`}
                    alt={location.country}
                    className="w-[34px] h-[22px] object-cover rounded shadow-[0_0_6px_rgba(0,187,255,0.25)] border border-cyber-blue/30"
                  />
                ) : (
                  <span className="text-xl">📍</span>
                )}
                <div>
                  <div className="font-hud text-[15px] font-black text-cyber-cyan leading-tight">{location.city || 'Patna'}</div>
                  <div className="text-[10px] text-cyber-muted font-bold uppercase">{location.region ? `${location.region}, ` : ''}{location.country || 'Bihar, India'}</div>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-cyber-muted tracking-widest mt-1 bg-cyber-deep/60 rounded p-1.5 border border-cyber-blue/10">
                <div>LAT: <span className="text-cyber-cyan font-bold">{location.lat ? location.lat.toFixed(4) : '25.5943'}°</span></div>
                <div>LNG: <span className="text-cyber-cyan font-bold">{location.lng ? location.lng.toFixed(4) : '85.1352'}°</span></div>
              </div>
              <div className="flex justify-between items-center pt-1 mt-1 font-hud text-[9px]">
                <span className="text-cyber-dim uppercase tracking-wider">locator.active</span>
                <a
                  href={`https://www.google.com/maps?q=${location.lat},${location.lng}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-cyber-blue hover:text-cyber-cyan transition-colors duration-200 tracking-wider font-semibold uppercase hover:underline"
                >
                  VIEW MAP &gt;
                </a>
              </div>
            </div>
          </div>

          {/* CONVERSATION PANEL */}
          <div className="hud-panel relative flex flex-col flex-1 rounded-lg transition-colors duration-300 overflow-hidden min-h-0">
            <div className="scifi-corner scifi-corner-tl"></div>
            <div className="scifi-corner scifi-corner-tr"></div>
            <div className="scifi-corner scifi-corner-bl"></div>
            <div className="scifi-corner scifi-corner-br"></div>

            <div className="flex justify-between items-center px-4 py-2.5 border-b border-cyber-blue/10 bg-cyber-deep/20 relative after:content-[''] after:absolute after:bottom-[-1px] after:left-0 after:w-10 after:height-[1px] after:bg-cyber-blue after:[box-shadow:0_0_5px_#00bbff]">
              <div className="flex items-center gap-[8px]">
                <svg viewBox="0 0 24 24" className="w-3.5 h-3.5 fill-cyber-blue filter drop-shadow-[0_0_3px_#00bbff]"><path d="M20 2H4c-1.1 0-1.99.9-1.99 2L2 22l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zM6 9h12v2H6V9zm8 5H6v-2h8v2zm4-6H6V6h12v2z" /></svg>
                <h2 className="font-hud text-[11px] font-bold tracking-wider text-white">CONVERSATION</h2>
              </div>
              <div className="flex gap-2">
                <button onClick={() => setMessages([])} className="bg-transparent border border-cyber-blue/20 hover:border-cyber-cyan rounded text-cyber-muted font-hud text-[9px] uppercase tracking-wider px-2 py-[2px] cursor-pointer hover:bg-cyber-cyan/10 hover:text-white transition-all duration-200">CLEAR</button>
                <button onClick={exportChat} className="bg-transparent border border-cyber-blue/20 hover:border-cyber-cyan rounded text-cyber-muted font-hud text-[9px] uppercase tracking-wider px-2 py-[2px] cursor-pointer hover:bg-cyber-cyan/10 hover:text-white transition-all duration-200">EXPORT</button>
              </div>
            </div>

            {/* Conversation Messages */}
            <div className="flex-1 overflow-y-auto p-3.5 bg-black/40 flex flex-col gap-2.5">
              <div className="flex flex-col gap-3">
                {messages.map((m, i) => (
                  <div key={i} className={`flex gap-2.5 max-w-[88%] animate-msg-slide ${m.sender === 'Jarvis' ? 'self-start' : 'self-end flex-row-reverse'}`}>
                    {/* Avatar circle */}
                    <div className={`w-6 h-6 rounded-full flex justify-center items-center font-hud text-[10px] font-black border shrink-0 ${m.sender === 'Jarvis'
                      ? 'bg-cyber-deep/80 border-cyber-blue/60 text-cyber-blue shadow-[0_0_4px_rgba(0,187,255,0.25)]'
                      : 'bg-cyber-deep/80 border-cyber-cyan/60 text-cyber-cyan shadow-[0_0_4px_rgba(0,240,255,0.25)]'
                      }`}>
                      {m.sender === 'Jarvis' ? 'J' : 'U'}
                    </div>
                    {/* Message body */}
                    <div className="flex flex-col gap-0.5">
                      <div className={`text-[12.5px] leading-relaxed p-[8px_12px] rounded-lg break-words font-labels font-medium ${m.sender === 'Jarvis'
                        ? 'bg-cyber-deep/75 border border-cyber-blue/15 text-[#e2f1ff] rounded-tl-none'
                        : 'bg-cyber-blue/10 border border-cyber-cyan/30 text-white rounded-tr-none shadow-[inset_0_0_10px_rgba(0,240,255,0.05)]'
                        }`}>{m.text}</div>
                      <span className={`text-[8px] text-cyber-dim font-hud ${m.sender === 'Jarvis' ? 'self-start' : 'self-end'}`}>{m.time}</span>
                    </div>
                  </div>
                ))}
                <div ref={chatEndRef} />
              </div>
            </div>

            {/* Conversation Inputs */}
            <div className="p-2.5 border-t border-cyber-blue/10 bg-cyber-deep/30">
              <form onSubmit={sendCommand} className="flex gap-2 bg-black/70 border border-cyber-blue/20 rounded p-0.5 focus-within:border-cyber-cyan/50 focus-within:shadow-[0_0_8px_rgba(0,240,255,0.15)] transition-all duration-300">
                <input
                  type="text"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  placeholder="Type a command or ask..."
                  className="flex-1 bg-transparent border-none outline-none text-white font-labels text-[13px] px-2.5 py-1.5"
                />
                <button type="submit" className="bg-black border border-cyber-blue/30 hover:border-cyber-cyan rounded w-[30px] h-[30px] flex justify-center items-center cursor-pointer transition-all duration-300 hover:shadow-[0_0_6px_#00f0ff] hover:scale-105 group">
                  <svg viewBox="0 0 24 24" className="w-[12px] h-[12px] fill-cyber-muted transition-colors duration-300 group-hover:fill-cyber-cyan">
                    <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
                  </svg>
                </button>
              </form>
            </div>

          </div>

        </section>

      </main>

      {/* --- COLLAPSIBLE LOG DRAWER TERMINAL --- */}
      <footer className={`fixed bottom-0 left-[15px] right-[15px] h-[220px] bg-black/95 border border-cyber-blue/25 border-b-0 rounded-t-lg shadow-[0_-4px_20px_rgba(0,187,255,0.12)] flex flex-col transition-transform duration-350 z-50 backdrop-blur-md ${terminalOpen ? 'translate-y-0' : 'translate-y-[182px]'}`}>
        <div
          onClick={() => setTerminalOpen(!terminalOpen)}
          className="flex justify-between items-center px-[18px] py-[8px] border-b border-cyber-blue/15 cursor-pointer h-[38px] select-none"
        >
          {/* Left Title */}
          <div className="flex items-center gap-[8px] font-hud text-[10.5px] font-bold tracking-wider text-cyber-cyan shrink-0">
            <span className="w-1.5 h-1.5 rounded-full bg-cyber-cyan shadow-[0_0_6px_#00f0ff] animate-blink-dot"></span>
            <span>SYSTEM LOG STREAM</span>
          </div>

          {/* Center Scrolling Ticker (Visible only when collapsed) */}
          {!terminalOpen ? (
            <div className="flex-1 overflow-hidden mx-6 h-5 flex items-center relative select-none">
              <div className="flex gap-8 whitespace-nowrap animate-log-ticker text-[10px] text-cyber-muted font-mono uppercase tracking-[2px]">
                {logs.slice(-8).map((log, idx) => (
                  <span key={idx} className="flex items-center gap-1.5">
                    <span className="text-cyber-cyan font-bold">{log.time}</span>
                    <span className={log.type === 'error' ? 'text-red-400' : log.type === 'success' ? 'text-green-400' : 'text-white'}>
                      {log.text.replace(/\[.*?\]\s*/g, '')}
                    </span>
                    <span className="text-cyber-dim mx-2">|</span>
                  </span>
                ))}
                {/* Duplicate the array to make the scrolling continuous */}
                {logs.slice(-8).map((log, idx) => (
                  <span key={`dup-${idx}`} className="flex items-center gap-1.5">
                    <span className="text-cyber-cyan font-bold">{log.time}</span>
                    <span className={log.type === 'error' ? 'text-red-400' : log.type === 'success' ? 'text-green-400' : 'text-white'}>
                      {log.text.replace(/\[.*?\]\s*/g, '')}
                    </span>
                    <span className="text-cyber-dim mx-2">|</span>
                  </span>
                ))}
              </div>
            </div>
          ) : (
            <div className="flex-1 text-center font-hud text-[10px] text-cyber-dim uppercase tracking-wider select-none">
              Active Terminal Log Drawer // Real-Time Events Streams
            </div>
          )}

          {/* Right Controls */}
          <div className="flex items-center gap-3 shrink-0">
            {terminalOpen && (
              <>
                <button
                  onClick={(e) => { e.stopPropagation(); setLogs([{ text: 'SYSTEM BUFFER INITIALIZED', type: 'info', time: new Date().toTimeString().split(' ')[0] }]); }}
                  className="bg-transparent border border-cyber-blue/20 rounded text-cyber-muted font-hud text-[9px] px-2 py-[2px] cursor-pointer hover:border-cyber-cyan hover:text-white hover:bg-cyber-cyan/10 transition-colors"
                >
                  CLEAR LOGS
                </button>
                <label className="text-[9.5px] font-hud text-cyber-muted flex items-center gap-1 cursor-pointer" onClick={e => e.stopPropagation()}>
                  <input
                    type="checkbox"
                    checked={autoscroll}
                    onChange={() => setAutoscroll(!autoscroll)}
                    className="cursor-pointer accent-cyber-blue"
                  />
                  AUTO-SCROLL
                </label>
              </>
            )}
            <button className="bg-transparent border border-cyber-blue/30 rounded px-2.5 py-[3px] text-cyber-blue font-hud text-[9px] uppercase tracking-wider hover:bg-cyber-blue/10 hover:border-cyber-cyan hover:text-white transition-all duration-200 cursor-pointer">
              {terminalOpen ? 'CLOSE DRAWER' : 'VIEW FULL LOGS >'}
            </button>
          </div>
        </div>

        {/* Expanded terminal scroll block */}
        <div className="flex-1 overflow-y-auto px-[18px] py-2.5 bg-black/60">
          <pre className="font-mono text-[10.5px] leading-relaxed text-cyber-muted whitespace-pre-wrap break-all">
            {logs.map((log, index) => {
              let classColor = "text-[#e2f1ff]";
              if (log.type === 'error') classColor = "text-red-400";
              else if (log.type === 'success') classColor = "text-green-400";
              else if (log.type === 'info') classColor = "text-cyber-cyan";
              return (
                <span key={index} className={classColor}>
                  <span className="text-cyber-dim">[{log.time}]</span> {log.text}{"\n"}
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
