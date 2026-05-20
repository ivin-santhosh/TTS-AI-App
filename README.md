# 🎙️ TTS AI Application

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)
![gTTS](https://img.shields.io/badge/gTTS-Audio_Synthesis-orange?style=for-the-badge)
![pygame](https://img.shields.io/badge/pygame-Playback_Engine-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Production_Ready-brightgreen?style=for-the-badge)

## 📖 Overview
The **TTS AI Application** is a production-ready, cross-platform desktop tool designed to transform written text into natural-sounding spoken audio. Built with a futuristic and modular GUI using `tkinter`, it provides a highly responsive user experience by leveraging asynchronous background threading. The system emphasizes user privacy, network stability, and automated resource optimization.

---

## ✨ Key Features
* **Multi-Language Support & Translation:** Integrates `deep-translator` to dynamically translate and synthesize speech across multiple languages, including French, German, and Italian.
* **Responsive Asynchronous GUI:** Utilizes background `threading` to ensure the interface remains completely fluid and freeze-free during network requests, audio generation, and playback.
* **Customizable Playback Controls:** Allows users to adjust core speech parameters, including voice selection and playback speed, powered by `pygame` audio controls.
* **Automated Resource Lifecycle Management:** Employs an intelligent storage system that automatically deletes temporary `.mp3` files immediately post-playback, ensuring user privacy and optimizing local disk space.
* **Robust Error Handling:** Built-in fault tolerance designed to manage network instability, concurrency issues, and seamless fallback states.

---

## 🏗️ Architecture & Modules
The application is structured using a strict, data-flow-oriented modular architecture:
1. **User Interaction Module (GUI):** The frontend interface handling user inputs, language selection, theme management, and parameter tuning.
2. **Text Preprocessing Module:** Cleanses, parses, and translates the input text using `deep-translator` before feeding it to the synthesis engine.
3. **AI Synthesis Engine:** The core logic leveraging `gTTS` (and `pyttsx3` for offline functionality) to convert processed text into high-quality audio streams.
4. **Playback & Storage Optimizer:** Controls real-time audio playback using `pygame` and autonomously manages the creation and deletion of temporary audio files.

---

## 💻 Tech Stack
* **Core Language:** Python
* **Speech Synthesis:** `gTTS` (Google Text-to-Speech), `pyttsx3`
* **Audio Playback:** `pygame`
* **Translation Engine:** `deep-translator`
* **Concurrency:** `threading`
* **UI Framework:** `tkinter`

---

## 🚀 Installation & Setup
1. Clone the repository to your local machine.
2. Ensure Python 3.x is installed on your system.
3. Install the required dependencies:
   ```bash
   pip install gTTS pyttsx3 pygame deep-translator
   ```
4. Execute the main Python script to launch the application interface.

---

## UI Screenshots

<img width="842" height="787" alt="image" src="https://github.com/user-attachments/assets/d1d8ce48-599c-4647-9de1-6522d4b74a3d" />

<br/>

---

## 🔒 Security & Privacy
This application is designed with a strict privacy-first approach. All generated audio files are treated as ephemeral data. The built-in resource optimizer ensures that temporary files are aggressively purged from local storage the moment playback completes, leaving no residual footprint or cached data on the host machine.
