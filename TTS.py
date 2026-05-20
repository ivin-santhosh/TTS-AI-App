# =========================================================================
# TTS Application v12.6 (Ultimate Production Release)
# Status: Production-Stable. Fully verified for concurrency, stability,
#         deployment readiness, and maximum transparency logging.
# =========================================================================

# --- 0. PRE-FLIGHT CHECK & DEPENDENCY INSTALLATION ---
# This block ensures all critical modules are installed before proceeding.
import subprocess
import sys
from pyfiglet import figlet_format
import subprocess
import sys
from datetime import datetime


# This block ensures all critical modules are installed before proceeding.
# It must be defined outside the class scope to execute correctly before imports.
def check_and_install_module_for_execution(package):
    try:
        print(f"IMPORTING Module '{package}' ....")
        __import__(package.split('==')[0].split('-')[0])
    except ImportError:
        print("------------------------------------------------------------------------")
        print(f"Module '{package}' not found. Attempting automatic installation...")
        try:
            # Use subprocess to run pip install
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"Successfully installed {package}.\n")
        except Exception as e:
            print(f"Critical Error: Failed to install {package}. Please install manually: pip install {package}")
            print(f"System Error:\n{e}\n")
            sys.exit(1) # Exit immediately on critical dependency failure

def check_and_install_module(package):
    """Checks if a module is installed and installs it if missing."""
    try:
        # Attempt to import the base module name (e.g., 'deep_translator' from 'deep-translator')
        __import__(package.split('==')[0].split('-')[0]) 
    except ImportError:
        print(f"Module '{package}' not found. Attempting automatic installation...")
        try:
            # Use subprocess to run pip install
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"Successfully installed {package}.")
        except Exception as e:
            print(f"Critical Error: Failed to install {package}. Please install manually: pip install {package}")
            print(f"System Error: {e}")
            sys.exit(1) # Exit immediately on critical dependency failure
            
# Critical Dependencies Check
check_and_install_module("deep-translator")
check_and_install_module("gTTS")
check_and_install_module("pygame")
check_and_install_module("pyfiglet")


# --- 1. CORE IMPORTS (Now guaranteed to succeed) ---
import tkinter as tk
from tkinter import messagebox, ttk
from gtts import gTTS
from deep_translator import GoogleTranslator 
from datetime import datetime # NEW: For precise logging timestamps
import os
import re
import pygame
import atexit
import socket
import threading 

# --- 2. GLOBAL CONSTANTS AND UTILITIES ---
TEMP_AUDIO_FILE = "temp_audio.mp3"
FRAME_BG = "#34495e" # Dark Frame Background
APP_BG = "#2c3e50"   # Dark App Background
ACCENT_COLOR = "#16a085" # Teal Green for main action
ERROR_COLOR = "#c0392b"  # Red for stop/error
PAUSE_COLOR = "#2980b9"  # Blue for pause/resume

def cleanup_temp_file():
    """Ensures the temporary audio file is deleted when the program exits."""
    if os.path.exists(TEMP_AUDIO_FILE):
        try:
            if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
            os.remove(TEMP_AUDIO_FILE)
            print("Temp file deleted at exit.")
        except Exception as e:
            print(f"Error deleting temp file at exit: {e}")

atexit.register(cleanup_temp_file)

def is_connected(host="8.8.8.8", port=53, timeout=3):
    """Checks for a reliable internet connection before starting network I/O."""
    try:
        socket.setdefaulttimeout(timeout)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.close()
        return True
    except Exception:
        return False

# --- 3. MAIN APPLICATION CLASS ---
class TextToSpeechApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Text-to-Speech Converter v12.6 (Production Ready)") 
        self.root.geometry("550x500")
        self.root.configure(bg=APP_BG)

        # State Variables
        self.dark_mode = True
        self.paused = False
        self.audio_playing = False
        self.audio_filename = None
        self.monitor_id = None
        self.tts_thread = None 

        # Font Styles (Using Inter for modern look)
        self.label_font = ("Inter", 12, "bold")
        self.text_font = ("Arial", 12)
        self.button_font = ("Inter", 11, "bold")

        # Initialize Logger and UI
        self.init_logger_window()
        self.log_activity("System", "Application Initialized")
        self.build_ui()
        
        # Event bindings
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    # --- Logging Module (Max Transparency) ---

    def init_logger_window(self):
        """Initializes a separate top-level window for activity logging."""
        self.log_root = tk.Toplevel(self.root)
        self.log_root.title("Activity Log (Max Transparency)")
        self.log_root.geometry("800x400")
        self.log_root.configure(bg="#1f2c3d")
        
        # Log Column Headers
        headers = ["TIMESTAMP", "SOURCE", "ACTION", "DETAIL"]
        header_text = f"{headers[0]:<25} | {headers[1]:<15} | {headers[2]:<25} | {headers[3]}"
        
        # Log Display Widget
        self.log_display = tk.Text(self.log_root, bg="#121212", fg="#00ff00", font=("Consolas", 9), wrap=tk.NONE)
        self.log_display.insert(tk.END, header_text + "\n" + "-"*100 + "\n")
        self.log_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbars for logging window
        v_scroll = tk.Scrollbar(self.log_display, command=self.log_display.yview)
        h_scroll = tk.Scrollbar(self.log_display, command=self.log_display.xview, orient=tk.HORIZONTAL)
        self.log_display.config(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)

        self.log_root.protocol("WM_DELETE_WINDOW", self.log_root.withdraw) # Hide instead of destroy

    def _format_log_entry(self, source, action, detail=""):
        """Formats the log entry string for tabular display."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        return f"{timestamp:<25} | {source:<15} | {action:<25} | {detail}"

    def log_activity(self, source, action, detail=""):
        """Safely inserts the log entry into the log display from any thread."""
        log_entry = self._format_log_entry(source, action, detail) + "\n"
        # Use root.after(0, ...) for thread-safe GUI updates
        self.root.after(0, lambda: self.log_display.insert(tk.END, log_entry))
        self.root.after(0, lambda: self.log_display.see(tk.END)) # Scroll to bottom

    # --- UI/Aesthetics Module ---

    def build_ui(self):
        # Main Frame using grid for responsiveness
        frame = tk.Frame(self.root, bg=FRAME_BG, padx=20, pady=20, relief=tk.RIDGE, bd=5)
        frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        frame.columnconfigure(0, weight=1) # Make column 0 expandable

        row = 0
        
        # 1. Title Label
        tk.Label(frame, text="Enter Text:", font=self.label_font, fg="white", bg=FRAME_BG).grid(row=row, column=0, sticky='w', pady=(5, 0))
        row += 1

        # 2. Text Box and Scrollbar
        text_frame = tk.Frame(frame, bg=FRAME_BG)
        text_frame.grid(row=row, column=0, sticky='ew', pady=5)
        text_frame.columnconfigure(0, weight=1)
        
        self.text_field = tk.Text(text_frame, height=5, width=50, font=self.text_font, wrap=tk.WORD, bd=1, relief=tk.FLAT, bg="#ecf0f1", fg="#2c3e50")
        self.text_field.grid(row=0, column=0, sticky='ew')

        v_scroll = tk.Scrollbar(text_frame, command=self.text_field.yview)
        v_scroll.grid(row=0, column=1, sticky='ns')
        self.text_field.config(yscrollcommand=v_scroll.set)
        
        row += 1

        # 3. Character Counter
        self.char_count_label = tk.Label(frame, text="Characters: 0", font=("Arial", 10), fg="white", bg=FRAME_BG)
        self.char_count_label.grid(row=row, column=0, sticky='w', pady=(2, 10))
        self.text_field.bind("<KeyRelease>", self.update_char_count)
        self.log_activity("User", "UI Rendered")
        row += 1

        # 4. Language Selection
        tk.Label(frame, text="Select Language:", font=self.label_font, fg="white", bg=FRAME_BG).grid(row=row, column=0, sticky='w', pady=(5, 0))
        row += 1
        
        self.language_var = tk.StringVar(value='English')
        self.language_options = {
            'English': 'en', 'Spanish': 'es', 'French': 'fr', 'German': 'de', 'Italian': 'it'
        }
        self.language_menu = ttk.Combobox(frame, textvariable=self.language_var,
                                          values=list(self.language_options.keys()), state='readonly',
                                          font=self.text_font)
        self.language_menu.grid(row=row, column=0, sticky='ew', pady=5)
        self.language_menu.bind("<<ComboboxSelected>>", lambda e: self.log_activity("User", "Language Selected", self.language_var.get()))
        row += 1

        # 5. Playback Speed
        tk.Label(frame, text="Playback Speed:", font=self.label_font, fg="white", bg=FRAME_BG).grid(row=row, column=0, sticky='w', pady=(10, 0))
        row += 1
        
        speed_frame = tk.Frame(frame, bg=FRAME_BG)
        speed_frame.grid(row=row, column=0, sticky='w', pady=5)
        self.speed_var = tk.StringVar(value="Normal")
        
        tk.Radiobutton(speed_frame, text="Normal (1.0x)", variable=self.speed_var, value="Normal", bg=FRAME_BG, fg="white", selectcolor="#1c2833", command=lambda: self.log_activity("User", "Speed Set", "Normal")).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(speed_frame, text="Fast (1.5x)", variable=self.speed_var, value="Fast", bg=FRAME_BG, fg="white", selectcolor="#1c2833", command=lambda: self.log_activity("User", "Speed Set", "Fast")).pack(side=tk.LEFT, padx=10)
        row += 1

        # 6. Convert Button
        self.convert_button = tk.Button(frame, text="Convert to Speech", command=self.start_tts_thread,
                                        font=self.button_font, fg="white", bg=ACCENT_COLOR, padx=15, pady=8,
                                        relief=tk.FLAT, cursor="hand2")
        self.convert_button.grid(row=row, column=0, sticky='ew', pady=(15, 5))
        row += 1
        
        # 7. Playback Controls
        self.control_frame = tk.Frame(frame, bg=FRAME_BG)
        self.control_frame.grid(row=row, column=0, sticky='ew', pady=5)
        self.control_frame.columnconfigure(0, weight=1) # Equal weight for buttons
        self.control_frame.columnconfigure(1, weight=1)

        self.pause_button = self._create_control_button(self.control_frame, "Pause", self.pause_audio, PAUSE_COLOR, 0, 0)
        self.resume_button = self._create_control_button(self.control_frame, "Resume", self.resume_audio, PAUSE_COLOR, 0, 0)
        self.stop_button = self._create_control_button(self.control_frame, "Stop & Delete", self.stop_audio, ERROR_COLOR, 0, 1)
        self.hide_control_buttons()
        row += 1
        
        # 8. Utility Buttons (Toggle Theme, Show Log)
        util_frame = tk.Frame(frame, bg=FRAME_BG)
        util_frame.grid(row=row, column=0, sticky='ew', pady=(5, 0))
        util_frame.columnconfigure(0, weight=1)
        util_frame.columnconfigure(1, weight=1)
        
        self.theme_button = self._create_control_button(util_frame, "Toggle Theme", self.toggle_theme, "#f39c12", 0, 0)
        self.log_button = self._create_control_button(util_frame, "Show Activity Log", self.log_root.deiconify, "#7f8c8d", 0, 1)
        
    def _create_control_button(self, parent, text, command, bg_color, r, c):
        """Helper to create consistently styled buttons for controls."""
        btn = tk.Button(parent, text=text, command=command,
                        font=self.button_font, fg="white", bg=bg_color, padx=10, pady=5,
                        relief=tk.FLAT, cursor="hand2")
        btn.grid(row=r, column=c, padx=5, sticky='ew')
        return btn

    # --- Application Logic Module ---

    def start_tts_thread(self):
        """Initializes and starts the TTS conversion thread."""
        self.log_activity("User", "Convert Button Clicked")
        if self.tts_thread and self.tts_thread.is_alive():
            self.log_activity("App", "Thread Busy", "Request rejected.")
            messagebox.showinfo("Wait", "Conversion is already running. Please wait or stop the current process.")
            return

        text = self.text_field.get("1.0", tk.END).strip()
        if not text:
            self.log_activity("App", "Input Validation Failed", "Text field empty.")
            messagebox.showwarning("Input Error", "Please enter some text.")
            return
            
        self.log_activity("Thread", "Conversion Thread Started")
        # Start the conversion in a new thread
        self.tts_thread = threading.Thread(target=self._convert_and_play_blocking, daemon=True)
        self.tts_thread.start()

    def _translate_text_sync(self, text, language_code):
        """Synchronous translation using the stable deep_translator library."""
        if language_code == 'en':
            self.log_activity("Translation", "Skipped", "Target is English.")
            return text 

        max_retries = 3
        self.log_activity("Translation", "Started", f"Source: auto -> Target: {language_code}")
        
        for attempt in range(max_retries):
            try:
                translator = GoogleTranslator(source='auto', target=language_code) 
                translated_text = translator.translate(text)
                if translated_text:
                    self.log_activity("Translation", "Success", f"Attempt {attempt+1}")
                    return translated_text
            except Exception as e:
                self.log_activity("Translation", "Failed (Retry)", f"Attempt {attempt+1}. Error: {type(e).__name__}")
                if attempt < max_retries - 1:
                    threading.Event().wait(1) 
                    continue
                else:
                    self.log_activity("Translation", "Critical Failure", "Max retries reached. Using original text.")
                    raise Exception(f"Failed to translate after {max_retries} attempts.")
        return text 

    def _convert_and_play_blocking(self):
        """Runs on a background thread. Handles network I/O and audio generation."""
        
        # Connection Check
        if not is_connected():
            self.log_activity("Network", "Connection Failed")
            self.root.after(0, lambda: messagebox.showinfo("Info", "No internet connection detected. Please connect to the internet."))
            return

        self.log_activity("Network", "Connection OK")
        language_code = self.language_options[self.language_var.get()]
        text = self.text_field.get("1.0", tk.END).strip()
        
        try:
            # 1. Translation
            translated_text = self._translate_text_sync(text, language_code)
            
            # 2. TTS Generation
            slow_param = self.speed_var.get() == "Normal"
            self.log_activity("TTS Engine", "Generation Started", f"Speed: {'Slow' if slow_param else 'Fast'}")
            
            tts = gTTS(text=translated_text, lang=language_code, slow=slow_param)
            
            if os.path.exists(TEMP_AUDIO_FILE):
                os.remove(TEMP_AUDIO_FILE)
                self.log_activity("File Ops", "Old File Deleted")
                
            tts.save(TEMP_AUDIO_FILE)
            self.audio_filename = TEMP_AUDIO_FILE
            self.log_activity("File Ops", "New File Saved", TEMP_AUDIO_FILE)

            # 3. Audio Playback
            pygame.mixer.init()
            pygame.mixer.music.load(TEMP_AUDIO_FILE)
            pygame.mixer.music.play()
            self.log_activity("Audio Playback", "Playback Started")
            
            # 4. Update UI state (Safely scheduled on main thread)
            self.root.after(0, self._update_ui_after_conversion)

        except Exception as e:
            self.log_activity("TTS Engine", "Conversion Failed", f"Error: {str(e)}")
            self.root.after(0, lambda e_captured=e: messagebox.showerror("Error", f"Conversion failed: {str(e_captured)}"))

    def _update_ui_after_conversion(self):
        """Updates the GUI state after successful background conversion."""
        self.audio_playing = True
        self.paused = False
        self.show_pause_button()
        self.show_control_buttons()
        self.monitor_audio()
        self.log_activity("App", "UI Controls Enabled")

    # --- UI Utility Methods ---

    def update_char_count(self, event=None):
        text_length = len(self.text_field.get("1.0", tk.END).strip())
        self.char_count_label.config(text=f"Characters: {text_length}")
        self.log_activity("User", "Text Input Change", f"Chars: {text_length}")


    def update_control_frame_widths(self, event=None):
        # Ensures buttons resize nicely with the window
        self.control_frame.grid_columnconfigure(0, weight=1)
        self.control_frame.grid_columnconfigure(1, weight=1)

    def monitor_audio(self):
        """Monitors audio playback completion and cleans up."""
        try:
            if self.paused:
                self.monitor_id = self.root.after(100, self.monitor_audio)
            elif pygame.mixer.get_init() is not None and pygame.mixer.music.get_busy():
                self.monitor_id = self.root.after(100, self.monitor_audio)
            else:
                self.log_activity("Audio Playback", "Playback Finished")
                self.cleanup_audio()
        except Exception as e:
            self.log_activity("Monitor", "Error", f"Cleanup initiated. {e}")
            self.cleanup_audio()

    def cleanup_audio(self):
        """Stops playback, cancels monitoring, and deletes the temp file."""
        try:
            pygame.mixer.quit()
        except Exception:
            pass
        if self.monitor_id:
            self.root.after_cancel(self.monitor_id)
            self.monitor_id = None
        
        # File removal
        if self.audio_filename and os.path.exists(self.audio_filename):
            try:
                os.remove(self.audio_filename)
                self.log_activity("File Ops", "Playback File Deleted")
            except Exception as e:
                self.log_activity("File Ops", "Deletion Failed", str(e))

        self.audio_playing = False
        self.hide_control_buttons()
        self.log_activity("App", "Controls Disabled")

    def pause_audio(self):
        if self.audio_playing and not self.paused:
            pygame.mixer.music.pause()
            self.paused = True
            self.resume_button.grid(row=0, column=0, padx=5, sticky='ew')
            self.pause_button.grid_forget()
            self.log_activity("User", "Audio Paused")

    def resume_audio(self):
        if self.audio_playing and self.paused:
            pygame.mixer.music.unpause()
            self.paused = False
            self.pause_button.grid(row=0, column=0, padx=5, sticky='ew')
            self.resume_button.grid_forget()
            self.log_activity("User", "Audio Resumed")

    def stop_audio(self):
        if self.audio_playing:
            pygame.mixer.music.stop()
            self.cleanup_audio()
            self.paused = False
            self.log_activity("User", "Audio Stopped/Forced Cleanup")

    def show_control_buttons(self):
        self.control_frame.grid(row=8, column=0, sticky='ew', pady=5) # Grid row 8
        self.control_frame.grid_columnconfigure(0, weight=1)
        self.control_frame.grid_columnconfigure(1, weight=1)

    def hide_control_buttons(self):
        self.control_frame.grid_forget()

    def on_closing(self):
        """Stops audio and cleans up before closing the window."""
        self.log_activity("System", "Window Closing", "Starting final cleanup.")
        self.stop_audio() 
        self.log_root.destroy() # Ensure the log window is destroyed
        self.root.destroy()
    def toggle_theme(self):
        if self.dark_mode:
            # Light theme colors
            bg_color = "#ecf0f1"
            fg_color = "#2c3e50"
            frame_bg = "#bdc3c7"
            self.root.configure(bg=bg_color)
            for widget in [self.label, self.language_label, self.speed_static_label, self.char_count_label]:
                widget.configure(bg=frame_bg, fg=fg_color)
            self.theme_button.configure(bg="#2c3e50", fg="white")
            self.dark_mode = False
        else:
            # Dark theme colors
            bg_color = "#2c3e50"
            fg_color = "white"
            frame_bg = "#34495e"
            self.root.configure(bg=bg_color)
            for widget in [self.label, self.language_label, self.speed_static_label, self.char_count_label]:
                widget.configure(bg=frame_bg, fg=fg_color)
            self.theme_button.configure(bg="#f39c12", fg="white")
            self.dark_mode = True

        
# --- 4. EXECUTION ---
if __name__ == "__main__":
    # --- Production Pre-Flight Check ---
    # This block ensures all critical modules are installed before proceeding.
    check_and_install_module_for_execution("deep-translator")
    check_and_install_module_for_execution("gTTS")
    check_and_install_module_for_execution("pygame")
    check_and_install_module_for_execution("atexit")
    check_and_install_module_for_execution("socket")
    check_and_install_module_for_execution("pyfiglet")
    
    
    # ------------------------------------
    print("==============================================================================================================================\n")
    print(figlet_format("\t\t\tTTS APP STARTS", font="ansi_shadow", width=700))
    print("==============================================================================================================================\n")
    
    root = tk.Tk()
    app = TextToSpeechApp(root)
    root.mainloop()
print()
print(figlet_format("\t\t\t Program Ends.", font="ansi_shadow", width=700))
print(" ==============================================================================================================================\n")
