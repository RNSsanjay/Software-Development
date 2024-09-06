import customtkinter as ctk
from tkinter import messagebox, simpledialog, filedialog
import os
from PIL import Image, ImageTk
import pyaudio
import wave
import speech_recognition as sr
import threading
import time

class NotesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RNS Info Helpers")
        self.root.geometry("900x700")

        # Set the taskbar icon
        self.root.iconbitmap('logonote.ico')  # Change the taskbar icon to 'logonote.ico'

        # Set appearance mode and color theme
        ctk.set_appearance_mode("Light")
        ctk.set_default_color_theme("blue")

        self.filename = 'notes.txt'
        self.notes = []
        self.load_notes()

        # Create UI components
        self.create_widgets()
        self.animate_title()
    
    # [rest of your code remains unchanged...]


    def create_widgets(self):
        # Title label
        self.title_label = ctk.CTkLabel(self.root, text="RNS Info Helpers", font=("Arial", 28, "bold"))
        self.title_label.pack(pady=20)

        # Text area for notes input
        self.text_area = ctk.CTkTextbox(self.root, wrap='word', height=10, width=60, font=("Arial", 14))
        self.text_area.pack(expand=True, fill=ctk.BOTH, padx=20, pady=10)

        # Text area for viewing notes (read-only)
        self.view_area = ctk.CTkTextbox(self.root, wrap='word', height=15, width=60, font=("Arial", 14), state="disabled")
        self.view_area.pack(expand=True, fill=ctk.BOTH, padx=20, pady=10)
        self.view_area.pack_forget()  # Initially hidden

        # Frame for buttons
        self.button_frame = ctk.CTkFrame(self.root)
        self.button_frame.pack(pady=20)

        # Create and place buttons
        self.add_button = self.create_button("Save Note", self.add_note)
        self.add_button.grid(row=0, column=0, padx=10)

        self.view_button = self.create_button("View Notes", self.toggle_view_notes)
        self.view_button.grid(row=0, column=1, padx=10)

        self.delete_button = self.create_button("Delete Note", self.delete_note)
        self.delete_button.grid(row=0, column=2, padx=10)

        self.download_button = self.create_button("Download Notes", self.download_notes)
        self.download_button.grid(row=0, column=3, padx=10)

        self.clear_button = self.create_button("Clear Notes", self.clear_notes)
        self.clear_button.grid(row=0, column=4, padx=10)

        self.img_button = self.create_button("Add Image", self.add_image)
        self.img_button.grid(row=1, column=0, padx=10)

        self.video_button = self.create_button("Add Video", self.add_video)
        self.video_button.grid(row=1, column=1, padx=10)

        self.record_button = self.create_button("Record Voice", self.record_voice)
        self.record_button.grid(row=1, column=2, padx=10)

        self.speech_button = self.create_button("Speech to Text", self.speech_to_text)
        self.speech_button.grid(row=1, column=3, padx=10)

        self.fullscreen_button = self.create_button("Full Screen", self.toggle_fullscreen)
        self.fullscreen_button.grid(row=1, column=4, padx=10)

        # Mode Switch
        self.switch_mode = ctk.CTkSwitch(self.root, text="Dark Mode", command=self.toggle_mode)
        self.switch_mode.pack(pady=10)

        # Notification label
        self.notification_label = ctk.CTkLabel(self.root, text="", font=("Arial", 12))
        self.notification_label.pack(pady=10)

    def create_button(self, text, command):
        """Create a custom button."""
        button = ctk.CTkButton(self.button_frame, text=text, command=command, corner_radius=10)
        return button

    def load_notes(self):
        """Load notes from the file."""
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as file:
                self.notes = file.readlines()
        else:
            self.notes = []

    def save_notes(self):
        """Save notes to the file."""
        with open(self.filename, 'w') as file:
            file.writelines(self.notes)

    def add_note(self):
        """Save the current content of the text area as a note."""
        note_content = self.text_area.get('1.0', ctk.END).strip()
        if note_content:
            self.notes.append(note_content + '\n')
            self.save_notes()
            self.text_area.delete('1.0', ctk.END)
            self.notification_label.configure(text="Note saved!")
        else:
            self.notification_label.configure(text="No content to save.")

    def toggle_view_notes(self):
        """Toggle view notes."""
        if self.view_area.winfo_ismapped():
            self.view_area.pack_forget()
            self.notification_label.configure(text="Notes view hidden.")
        else:
            self.view_notes()
            self.view_area.pack(expand=True, fill=ctk.BOTH, padx=20, pady=10)

    def view_notes(self):
        """View all notes."""
        if not self.notes:
            self.notification_label.configure(text="No notes available.")
        else:
            notes_str = ''.join([f"{index + 1}: {note.strip()}\n" for index, note in enumerate(self.notes)])
            self.view_area.configure(state="normal")
            self.view_area.delete('1.0', ctk.END)
            self.view_area.insert(ctk.END, notes_str)
            self.view_area.configure(state="disabled")
            self.notification_label.configure(text="Notes displayed.")

    def delete_note(self):
        """Delete a note by index."""
        if not self.notes:
            self.notification_label.configure(text="No notes available to delete.")
            return
        
        index = simpledialog.askinteger("Input", "Enter the note number to delete:")
        if index is not None and 1 <= index <= len(self.notes):
            deleted_note = self.notes.pop(index - 1)
            self.save_notes()
            self.notification_label.configure(text=f"Deleted note: {deleted_note.strip()}")
        else:
            self.notification_label.configure(text="Invalid note number.")

    def download_notes(self):
        """Download notes to a .txt file."""
        if not self.notes:
            self.notification_label.configure(text="No notes available to download.")
            return
        
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, 'w') as file:
                file.writelines(self.notes)
            self.notification_label.configure(text="Notes downloaded successfully!")

    def clear_notes(self):
        """Clear all notes."""
        if messagebox.askyesno("Confirmation", "Are you sure you want to clear all notes?"):
            self.notes = []
            self.save_notes()
            self.notification_label.configure(text="All notes cleared!")

    def add_image(self):
        """Add an image to the notes."""
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
        if file_path:
            self.notes.append(f"[Image: {file_path}]\n")
            self.save_notes()
            self.notification_label.configure(text="Image added to notes!")

    def add_video(self):
        """Add a video to the notes."""
        file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4;*.avi;*.mov")])
        if file_path:
            self.notes.append(f"[Video: {file_path}]\n")
            self.save_notes()
            self.notification_label.configure(text="Video added to notes!")

    def record_voice(self):
        """Record a voice note."""
        def record():
            chunk = 1024
            format = pyaudio.paInt16
            channels = 1
            rate = 44100
            record_seconds = 5
            output_filename = "voice_note.wav"

            p = pyaudio.PyAudio()
            stream = p.open(format=format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk)

            self.notification_label.configure(text="Recording started. Speak now!")
            self.root.update()
            frames = []

            for i in range(0, int(rate / chunk * record_seconds)):
                data = stream.read(chunk)
                frames.append(data)
                self.notification_label.configure(text=f"Recording in progress... {i * chunk / rate:.1f}s elapsed")
                self.root.update()

            stream.stop_stream()
            stream.close()
            p.terminate()

            with wave.open(output_filename, 'wb') as wf:
                wf.setnchannels(channels)
                wf.setsampwidth(p.get_sample_size(format))
                wf.setframerate(rate)
                wf.writeframes(b''.join(frames))

            self.notes.append(f"[Voice: {output_filename}]\n")
            self.save_notes()
            self.notification_label.configure(text="Recording completed and saved!")

        threading.Thread(target=record).start()

    def speech_to_text(self):
        """Convert speech to text."""
        def convert():
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                self.notification_label.configure(text="Listening... Please speak.")
                self.root.update()
                audio = recognizer.listen(source)

            try:
                text = recognizer.recognize_google(audio)
                self.text_area.insert(ctk.END, text + '\n')
                self.notification_label.configure(text="Speech converted to text!")
            except sr.UnknownValueError:
                self.notification_label.configure(text="Google Speech Recognition could not understand audio.")
            except sr.RequestError as e:
                self.notification_label.configure(text=f"Could not request results; {e}")

        threading.Thread(target=convert).start()

    def toggle_mode(self):
        """Toggle between light and dark mode."""
        if ctk.get_appearance_mode() == "Light":
            ctk.set_appearance_mode("Dark")
            self.switch_mode.configure(text="Light Mode")
        else:
            ctk.set_appearance_mode("Light")
            self.switch_mode.configure(text="Dark Mode")

    def toggle_fullscreen(self):
        """Toggle full-screen mode or exit full-screen mode."""
        if self.root.attributes("-fullscreen"):
            self.root.attributes("-fullscreen", False)
            self.fullscreen_button.configure(text="Full Screen")
        else:
            self.root.attributes("-fullscreen", True)
            self.fullscreen_button.configure(text="Exit Full Screen")

    def animate_title(self):
        """Animate the title label with fade-in and fade-out effect."""
        def fade_animation(step):
            intensity = min(max(step * 5, 0), 255)
            color = f'#{intensity:02x}{intensity:02x}{intensity:02x}'  # Create a grayscale color
            
            self.title_label.configure(fg_color=color)
            
            if step < 51:
                self.root.after(50, fade_animation, step + 1)
            elif step >= 51 and step < 102:
                self.root.after(50, fade_animation, step + 1)
            else:
                self.root.after(1000, fade_animation, 0)

        fade_animation(0)

if __name__ == "__main__":
    root = ctk.CTk()
    app = NotesApp(root)
    root.mainloop()
