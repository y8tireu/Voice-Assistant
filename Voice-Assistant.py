import customtkinter as ctk
import rate
import speech_recognition as sr
import pyttsx3
import logging
import threading
import time
from queue import Queue, Empty
from tkinter import END
from datetime import datetime
import pytz
import os  # Import os module

# Configure logging with timestamp
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


class TTSManager:
    """Manages text-to-speech functionality in its own thread."""

    def __init__(self, rate=150, volume=1.0):
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', rate)
            self.engine.setProperty('volume', volume)
            self.queue = Queue()
            self.active = True  # Initialize active BEFORE starting the worker thread
            self.worker_thread = threading.Thread(target=self._worker, daemon=True)
            self.worker_thread.start()
        except Exception as e:
            logging.error(f"Failed to initialize TTS engine: {e}")
            self.active = False

    def _worker(self):
        while self.active:
            try:
                text = self.queue.get(timeout=1.0)  # Add timeout to allow clean shutdown
                if text is None:
                    break
                logging.info("TTSManager speaking: %s", text)
                self.engine.say(text)
                self.engine.runAndWait()
            except Empty:
                continue
            except Exception as e:
                logging.error(f"TTSManager error: {e}")
            finally:
                # Only mark task as done if an item was actually retrieved.
                # (If get() times out, Empty is raised and nothing to mark done)
                try:
                    self.queue.task_done()
                except Exception:
                    pass

    def speak(self, text):
        """Queue text for speech."""
        if self.active:
            self.queue.put(text)
        else:
            logging.error("TTS Manager is not active")

    def shutdown(self):
        """Cleanly shutdown the TTS manager."""
        self.active = False
        self.queue.put(None)
        self.worker_thread.join(timeout=2.0)

    def set_rate(self, rate):
        if self.active:
            self.engine.setProperty('rate', rate)
            logging.info("Speech rate set to %s", rate)

    def set_volume(self, volume):
        if self.active:
            self.engine.setProperty('volume', volume)
            logging.info("Volume set to %s", volume)

    def set_voice(self, voice_id):
        if self.active:
            self.engine.setProperty('voice', voice_id)
            logging.info("Voice changed to %s", voice_id)

    def get_voices(self):
        if self.active:
            return self.engine.getProperty('voices')
        return []


class VoiceAssistantGUI:
    def __init__(self, master):
        self.master = master
        master.title("Voice Assistant")
        master.geometry("800x600")  # Increased width for better visibility

        # Store the creation time
        self.creation_time = datetime.now(pytz.UTC)

        # Initialize speech recognizer with adjusted settings
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 4000  # Increased sensitivity
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8  # Reduced pause threshold

        # Initialize variables to avoid attribute errors
        self.voice_names = []       # Initialize voice names
        self.continuous_mode = False  # Initialize continuous mode

        # Initialize TTS manager
        self.tts_manager = TTSManager()

        self._setup_gui()
        self._initialize_voice_system()

        # Add status bar
        self.status_bar = ctk.CTkLabel(
            master,
            text=f"Started: {self.creation_time.strftime('%Y-%m-%d %H:%M:%S UTC')}",
            anchor="w"
        )
        self.status_bar.pack(side="bottom", fill="x", padx=5, pady=2)

        # Setup periodic status updates
        self._update_status()

    def _setup_gui(self):
        # Create main frames
        self.control_frame = ctk.CTkFrame(self.master)
        self.control_frame.pack(pady=10, padx=10, fill="x")

        self.log_frame = ctk.CTkFrame(self.master)
        self.log_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Add control buttons
        self._create_control_buttons()
        self._create_sliders()
        self._create_voice_controls()
        self._create_text_input()
        self._create_log_area()

    def _create_control_buttons(self):
        button_frame = ctk.CTkFrame(self.control_frame)
        button_frame.pack(fill="x", pady=5)

        buttons = [
            ("Start Listening", self.start_listening_thread),
            ("Stop Listening", self.stop_listening),
            ("Clear Transcript", self.clear_transcript),
            ("Save Transcript", self.save_transcript)
        ]

        for text, command in buttons:
            btn = ctk.CTkButton(
                button_frame,
                text=text,
                command=command,
                width=120
            )
            btn.pack(side="left", padx=5)

        # Add continuous mode checkbox
        self.continuous_var = ctk.BooleanVar(value=False)
        self.continuous_checkbox = ctk.CTkCheckBox(
            button_frame,
            text="Continuous Mode",
            variable=self.continuous_var,
            command=self.toggle_continuous
        )
        self.continuous_checkbox.pack(side="right", padx=5)

    def _create_sliders(self):
        slider_frame = ctk.CTkFrame(self.control_frame)
        slider_frame.pack(fill="x", pady=5)

        # Rate slider
        rate_frame = ctk.CTkFrame(slider_frame)
        rate_frame.pack(side="left", fill="x", expand=True, padx=5)

        ctk.CTkLabel(rate_frame, text="Speech Rate").pack(side="top")
        self.rate_slider = ctk.CTkSlider(
            rate_frame,
            from_=100,
            to=300,
            number_of_steps=20,
            command=self.update_rate
        )
        self.rate_slider.set(150)
        self.rate_slider.pack(fill="x", padx=5)

        # Volume slider
        volume_frame = ctk.CTkFrame(slider_frame)
        volume_frame.pack(side="right", fill="x", expand=True, padx=5)

        ctk.CTkLabel(volume_frame, text="Volume").pack(side="top")
        self.volume_slider = ctk.CTkSlider(
            volume_frame,
            from_=0,
            to=1,
            number_of_steps=10,
            command=self.update_volume
        )
        self.volume_slider.set(1.0)
        self.volume_slider.pack(fill="x", padx=5)

    def _create_voice_controls(self):
        voice_frame = ctk.CTkFrame(self.control_frame)
        voice_frame.pack(fill="x", pady=5)

        self.voice_label = ctk.CTkLabel(voice_frame, text="Voice")
        self.voice_label.pack(side="left", padx=5)

        self.voice_optionmenu = ctk.CTkOptionMenu(
            voice_frame,
            values=self.voice_names,
            command=self.change_voice
        )
        if self.voice_names:
            self.voice_optionmenu.set(self.voice_names[0])
        self.voice_optionmenu.pack(side="left", padx=5)

    def _create_text_input(self):
        text_frame = ctk.CTkFrame(self.control_frame)
        text_frame.pack(fill="x", pady=5)

        self.say_label = ctk.CTkLabel(text_frame, text="Enter text to speak:")
        self.say_label.pack(side="left", padx=5)

        self.say_entry = ctk.CTkEntry(text_frame, placeholder_text="Type something...")
        self.say_entry.pack(side="left", fill="x", expand=True, padx=5)

        self.say_button = ctk.CTkButton(text_frame, text="Speak", command=self.say_stuff)
        self.say_button.pack(side="right", padx=5)

    def _create_log_area(self):
        self.log_textbox = ctk.CTkTextbox(self.log_frame, wrap="word")
        self.log_textbox.pack(side="left", fill="both", expand=True)

        self.scrollbar = ctk.CTkScrollbar(self.log_frame, command=self.log_textbox.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.log_textbox.configure(yscrollcommand=self.scrollbar.set)

    def _initialize_voice_system(self):
        voices = self.tts_manager.get_voices()
        self.english_voices = []

        for voice in voices:
            try:
                langs = [lang.decode('utf-8') if isinstance(lang, bytes) else lang
                         for lang in voice.languages]
                if any("en" in lang.lower() for lang in langs) or "english" in voice.name.lower():
                    self.english_voices.append(voice)
            except Exception as e:
                logging.warning(f"Error processing voice {voice.name}: {e}")

        if not self.english_voices:
            self.english_voices = voices  # fallback

        self.voice_names = [voice.name for voice in self.english_voices]
        if self.voice_names:
            self.voice_optionmenu.configure(values=self.voice_names)
            self.voice_optionmenu.set(self.voice_names[0])
            self.tts_manager.set_voice(self.english_voices[0].id)

    def _update_status(self):
        """Update status bar with current information"""
        current_time = datetime.now(pytz.UTC)
        uptime = current_time - self.creation_time
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)

        status_text = (
            f"Current Time: {current_time.strftime('%Y-%m-%d %H:%M:%S UTC')} | "
            f"Uptime: {hours:02d}:{minutes:02d}:{seconds:02d}"
        )
        self.status_bar.configure(text=status_text)
        self.master.after(1000, self._update_status)  # Update every second

    def listen(self):
        """Record from microphone and return recognized text."""
        try:
            with sr.Microphone() as mic:
                logging.info("Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(mic, duration=0.5)
                logging.info("Listening...")

                try:
                    audio = self.recognizer.listen(mic, timeout=5, phrase_time_limit=10)
                except sr.WaitTimeoutError:
                    logging.error("Listening timed out waiting for phrase to start")
                    return "Listening timed out"

                try:
                    text = self.recognizer.recognize_google(audio, language="en-US")
                    logging.info("Recognized: %s", text)
                    return text
                except sr.UnknownValueError:
                    logging.error("Speech was unintelligible")
                    return "Could not understand audio"
                except sr.RequestError as e:
                    logging.error("Request error: %s", e)
                    return "Speech recognition request error"
        except Exception as e:
            logging.error(f"Unexpected error in listen(): {e}")
            return f"Error: {str(e)}"

    def process_voice(self):
        """Process a single voice interaction."""
        try:
            self.speak("How can I help you?")
            recognized_text = self.listen()
            self.update_log(f"User: {recognized_text}")
            self.speak(f"You said: {recognized_text}")
            self.update_log(f"Assistant: You said: {recognized_text}")
        except Exception as e:
            logging.error(f"Error in process_voice: {e}")
            self.update_log(f"Error: {str(e)}")

    def process_continuous_voice(self):
        """Process continuous voice interactions."""
        self.listening = True
        while self.listening:
            try:
                self.speak("How can I help you?")
                recognized_text = self.listen()

                if not self.listening:  # Check if stopped while listening
                    break

                self.update_log(f"User: {recognized_text}")
                self.speak(f"You said: {recognized_text}")
                self.update_log(f"Assistant: You said: {recognized_text}")

                if recognized_text.lower() in ["stop listening", "stop"]:
                    self.update_log("Assistant: Stopping continuous listening.")
                    self.speak("Stopping continuous listening.")
                    self.listening = False
                    break

                time.sleep(0.5)
            except Exception as e:
                logging.error(f"Error in continuous voice processing: {e}")
                self.update_log(f"Error: {str(e)}")
                time.sleep(1)  # Prevent rapid error loops

    def update_log(self, message):
        """Update the log with a new message."""
        timestamp = datetime.now(pytz.UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
        formatted_message = f"[{timestamp}] {message}\n"

        # Schedule GUI updates in the main thread
        self.master.after(0, lambda: self.log_textbox.insert(END, formatted_message))
        self.master.after(0, lambda: self.log_textbox.see(END))

    def start_listening_thread(self):
        """Start the listening process in a separate thread."""
        if self.continuous_mode:
            threading.Thread(target=self.process_continuous_voice, daemon=True).start()
        else:
            threading.Thread(target=self.process_voice, daemon=True).start()

    def stop_listening(self):
        """Stop the listening process."""
        self.listening = False
        logging.info("Listening stopped by user")
        self.update_log("System: Listening stopped by user")

    def speak(self, text):
        """Queue text for speech."""
        logging.info("Queueing text for TTS: %s", text)
        self.tts_manager.speak(text)

    def clear_transcript(self):
        """Clear the transcript log."""
        self.log_textbox.delete("1.0", END)
        self.update_log("System: Transcript cleared")

    def save_transcript(self):
        """Save the transcript to a file."""
        transcript = self.log_textbox.get("1.0", END).strip()
        if transcript:
            timestamp = datetime.now(pytz.UTC).strftime("%Y%m%d_%H%M%S")
            filename = f"transcript_{timestamp}.txt"
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(transcript)
                self.update_log(f"System: Transcript saved to {filename}")
            except Exception as e:
                self.update_log(f"Error saving transcript: {str(e)}")
        else:
            self.update_log("System: No transcript to save")

    def update_rate(self, value):
        """Update speech rate."""
        rate_val = int(float(value))
        self.tts_manager.set_rate(rate_val)

    def update_volume(self, value):
        """Update volume level."""
        volume = float(value)
        self.tts_manager.set_volume(volume)

    def change_voice(self, selected_voice):
        """Change the selected voice."""
        for voice in self.english_voices:
            if voice.name == selected_voice:
                self.tts_manager.set_voice(voice.id)
                break

    def toggle_continuous(self):
        """Toggle continuous mode."""
        self.continuous_mode = self.continuous_var.get()
        logging.info("Continuous mode set to %s", self.continuous_mode)

    def say_stuff(self):
        """Speak the text entered in the text entry field."""
        if self.continuous_mode:
            logging.info("Disable continuous mode to use text-to-speech.")
            self.update_log("System: Disable continuous mode to use text-to-speech.")
            return
        text_to_speak = self.say_entry.get().strip()
        if text_to_speak:
            self.update_log(f"Assistant says: {text_to_speak}")
            self.speak(text_to_speak)
            self.say_entry.delete(0, END)
        else:
            self.update_log("System: No text entered to speak.")

    def cleanup(self):
        """Clean up resources before closing."""
        try:
            self.tts_manager.shutdown()
        except Exception as e:
            logging.error(f"Error during cleanup: {e}")


if __name__ == "__main__":
    try:
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        root = ctk.CTk()
        app = VoiceAssistantGUI(root)
        root.protocol("WM_DELETE_WINDOW", app.cleanup)  # Proper cleanup on close
        root.mainloop()
    except Exception as e:
        logging.critical(f"Critical error in main: {e}")
