# Jarvish 🤖

> Your Personal AI Desktop Assistant

Jarvish is an AI-powered desktop assistant designed to simplify everyday tasks through voice commands, intelligent automation, and natural conversations. It combines local AI models, web capabilities, system controls, and multilingual communication into a single desktop experience.

---
## 🖥️ Jarvish UI

![Jarvish UI](./JarvisUI.png)

## 🚀 Overview

Jarvish is more than a chatbot. It acts as a personal desktop companion capable of understanding natural language, performing system-level actions, searching the web, managing tasks, and interacting through voice in real time.

Whether you want to open applications, search information, control your computer, or simply have a conversation, Jarvish is built to assist.

---

## ✨ Features

### 🎙️ Voice Assistant
- Real-time voice interaction
- Speech-to-Text (STT)
- Text-to-Speech (TTS)
- Hands-free operation

### 🧠 AI-Powered Conversations
- Natural language understanding
- Context-aware responses
- Local LLM integration using Ollama
- Fast and intelligent task execution

### 🌐 Web Search Integration
- Search the internet instantly
- Retrieve relevant information
- Answer knowledge-based queries

### 🌍 Multilingual Support
- English
- Hindi
- Punjabi
- Extensible to additional languages

### ⚡ Desktop Automation
- Open applications
- Launch websites
- System controls
  - Volume Control
  - Brightness Control
  - Bluetooth Management
  - Hotspot Control
- Execute custom commands

### 🎵 Smart Utilities
- Play music
- Check internet speed
- Perform quick calculations
- Productivity assistance

### 💬 Modern Chat Interface
- Real-time streaming responses
- Interactive UI
- Voice + Text communication

### 🔒 Local First
- Supports local AI models through Ollama
- Privacy-friendly architecture
- Reduced dependency on cloud services

---

## 🏗️ Architecture

```text
┌────────────────────┐
│   React Frontend   │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│   Python Backend   │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│      Ollama        │
│   Local LLMs       │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ System Automation  │
│ Web Search Engine  │
│ Voice Services     │
└────────────────────┘
```

---

## 🛠️ Tech Stack

### Backend
- Python
- Ollama
- SpeechRecognition
- pyttsx3
- FastAPI / HTTP Server
- psutil

### Frontend
- React.js
- JavaScript
- HTML5
- CSS3
- Vite

### AI & Voice
- Qwen Models
- Ollama
- Speech-to-Text
- Text-to-Speech

---

## 📂 Project Structure

```text
Jarvish/
│
├── backend/
│   ├── core/
│   ├── automation/
│   ├── voice/
│   ├── web/
│   └── main.py
│
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
├── assets/
├── requirements.txt
├── README.md
└── .env
```

---

## ⚙️ Installation

### 1. Clone Repository

```bash
git clone https://github.com/dhiruXDev/Jarvis.git
cd Jarvis
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
```

### Activate Environment

#### Windows

```bash
.venv\Scripts\activate
```

#### Linux / macOS

```bash
source .venv/bin/activate
```

---

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Install Frontend Dependencies

```bash
cd frontend
npm install
```

---

### 5. Install Ollama

Download and install Ollama:

https://ollama.com

Pull your preferred model:

```bash
ollama pull qwen2.5:3b
```

---

## ▶️ Running Jarvish

### Start Backend

```bash
python main.py
```

### Start Frontend

```bash
cd frontend
npm run dev
```

Open:

```text
http://localhost:5173
```

---

## 🎯 Example Commands

```text
Open Chrome
Search latest AI news
Increase volume
Turn on Bluetooth
What's the weather today?
Play a song
Open LeetCode
Tell me a joke
```

---

## 🔮 Future Roadmap

- Multi-Agent Architecture
- Long-Term Memory System
- Vector Database Integration
- Personalized User Profiles
- Workflow Automation Engine
- Smart Scheduling
- Mobile Companion App
- Electron Desktop Packaging
- Agentic AI Capabilities

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome.

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to your branch
5. Open a Pull Request

---

## 📜 License

This project is licensed under the MIT License.

---
 
## 👨‍💻 Developer

**Dhiraj Kumar**

- MERN Stack Developer
- AI Enthusiast
- Exploring Agentic AI

GitHub: https://github.com/dhiruXDev
 

---
## 👥 Contributors

| Name | Role |
|------|------|
| **Dhiraj Kumar** | MERN Stack Developer • AI Enthusiast • Exploring Agentic AI |
| **Urshitaa** | AI/ML Developer • Web Developer |

GitHub: https://github.com/dhiruXDev

⭐ If you like Jarvish, consider giving the repository a star.
