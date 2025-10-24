import tkinter as tk
from tkinter import font as tkfont
import json
import pyttsx3

class ENG_GER:
    def __init__(self, json_file=None):
        self.json_file = json_file
        self.translations = []
        self.de_id = "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_DE-DE_HEDDA_11.0"
        self.en_id = "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_DAVID_11.0"
        self.engine = pyttsx3.init()
    
    def load_translations(self):
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
        except FileNotFoundError:
            print(f"File {self.json_file} not found.")
            self.translations = []
        except json.JSONDecodeError:
            print(f"Error decoding JSON from file {self.json_file}.")
            self.translations = []
    
    def read_words(self, word, lang):
        if not self.translations:
            print("No translations loaded.")
            return
        if lang == "deutsch":
            self.engine.setProperty('rate', 125)
            self.engine.setProperty('volume', 1.0)
            self.engine.setProperty('voice', self.de_id)
            self.engine.say(word)
        else:
            self.engine.setProperty('rate', 125)
            self.engine.setProperty('volume', 1.0)
            self.engine.setProperty('voice', self.en_id)
            self.engine.say(word)

class FlashcardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Language Flashcards")
        self.root.geometry("1000x690")
        self.root.configure(bg="#1a1a2e")
        
        # Initialize translator and load cards
        self.translator = ENG_GER("./data/deutsch_translations.json")
        self.translator.load_translations()
        self.cards = self.translator.translations
        
        self.current_index = 0
        self.is_flipped = False
        self.flip_animation_id = None
        
        self.setup_ui()
        self.show_card()
        
    def setup_ui(self):
        # Header
        header_frame = tk.Frame(self.root, bg="#16213e", height=80)
        header_frame.pack(fill="x", pady=(0, 20))
        header_frame.pack_propagate(False)
        
        title_font = tkfont.Font(family="Helvetica", size=28, weight="bold")
        title = tk.Label(
            header_frame, 
            text="✨ Language Flashcards", 
            font=title_font,
            bg="#16213e", 
            fg="#00d4ff"
        )
        title.pack(pady=20)
        
        # Main card container
        self.card_container = tk.Frame(self.root, bg="#1a1a2e")
        self.card_container.pack(expand=True, fill="both", padx=40, pady=20)
        
        # Card frame with shadow effect
        self.shadow_frame = tk.Frame(
            self.card_container,
            bg="#0f0f1e",
            highlightthickness=0
        )
        self.shadow_frame.place(relx=0.5, rely=0.45, anchor="center", relwidth=0.85, relheight=0.6)
        
        self.card_frame = tk.Frame(
            self.card_container,
            bg="#ffffff",
            highlightthickness=0,
            relief="flat"
        )
        self.card_frame.place(relx=0.5, rely=0.43, anchor="center", relwidth=0.85, relheight=0.6)
        
        # Card content
        self.language_label = tk.Label(
            self.card_frame,
            text="",
            font=("Helvetica", 14),
            bg="#ffffff",
            fg="#666666"
        )
        self.language_label.pack(pady=(40, 10))
        
        self.word_label = tk.Label(
            self.card_frame,
            text="",
            font=("Helvetica", 38, "bold"),
            bg="#ffffff",
            fg="#1a1a2e",
            wraplength=500
        )
        self.word_label.pack(pady=20, expand=True)
        
        # Audio button
        self.audio_btn = tk.Button(
            self.card_frame,
            text="Play",
            font=("Helvetica", 12),
            bg="#00d4ff",
            fg="white",
            activebackground="#00b8e6",
            activeforeground="white",
            relief="flat",
            padx=30,
            pady=20,
            cursor="hand2",
            command=self.play_audio
        )
        self.audio_btn.pack(pady=20)
        
        # Flip hint
        self.flip_hint = tk.Label(
            self.card_frame,
            text="Click card to flip →",
            font=("Helvetica", 11, "italic"),
            bg="#ffffff",
            fg="#999999"
        )
        self.flip_hint.pack(side="bottom", pady=15)
        
        # Bind click event to flip and play audio
        self.card_frame.bind("<Button-1>", lambda e: self.flip_and_play())
        self.word_label.bind("<Button-1>", lambda e: self.flip_and_play())
        self.language_label.bind("<Button-1>", lambda e: self.flip_and_play())
        self.flip_hint.bind("<Button-1>", lambda e: self.flip_and_play())
        
        # Bottom controls
        controls_frame = tk.Frame(self.root, bg="#1a1a2e", height=100)
        controls_frame.pack(fill="x", side="bottom", pady=20)
        
        # Counter
        self.counter_label = tk.Label(
            controls_frame,
            text="",
            font=("Helvetica", 12),
            bg="#1a1a2e",
            fg="#999999"
        )
        self.counter_label.pack(pady=(0, 15))
        
        # Navigation buttons
        btn_frame = tk.Frame(controls_frame, bg="#1a1a2e")
        btn_frame.pack()
        
        btn_style = {
            "font": ("Helvetica", 14, "bold"),
            "bg": "#00d4ff",
            "fg": "white",
            "activebackground": "#00b8e6",
            "activeforeground": "white",
            "relief": "flat",
            "padx": 30,
            "pady": 12,
            "cursor": "hand2",
            "width": 10
        }
        
        self.prev_btn = tk.Button(
            btn_frame,
            text="← Previous",
            command=self.prev_card,
            **btn_style
        )
        self.prev_btn.pack(side="left", padx=10)
        
        self.next_btn = tk.Button(
            btn_frame,
            text="Next →",
            command=self.next_card,
            **btn_style
        )
        self.next_btn.pack(side="left", padx=10)
        
        # Keyboard bindings
        self.root.bind("<Left>", lambda e: self.prev_card())
        self.root.bind("<Right>", lambda e: self.next_card())
        self.root.bind("<space>", lambda e: self.flip_card())
        
    def show_card(self):
        card = self.cards[self.current_index]
        self.is_flipped = False
        
        # Show source side
        self.language_label.config(text=card["source_language"].upper())
        self.word_label.config(text=card["source_word"], fg="#1a1a2e")
        self.card_frame.config(bg="#ffffff")
        self.language_label.config(bg="#ffffff")
        self.word_label.config(bg="#ffffff")
        self.flip_hint.config(bg="#ffffff")
        
        # Update counter
        self.counter_label.config(
            text=f"Card {self.current_index + 1} of {len(self.cards)}"
        )
        
        # Update button states
        self.prev_btn.config(state="normal" if self.current_index > 0 else "disabled")
        self.next_btn.config(state="normal" if self.current_index < len(self.cards) - 1 else "disabled")
        
    def flip_and_play(self):
        """Flip card and play audio for the current side"""
        self.flip_card()
        # Play audio after flip animation starts
        self.root.after(10, self.play_audio)
    
    def flip_card(self):
        if self.flip_animation_id:
            return
            
        card = self.cards[self.current_index]
        self.is_flipped = not self.is_flipped
        
        # Animate flip
        self.animate_flip(card)
        
    def animate_flip(self, card):
        # Simple scale animation
        steps = 10
        current_step = [0]
        
        def step():
            current_step[0] += 1
            if current_step[0] <= steps // 2:
                # Shrink
                scale = 1 - (current_step[0] / (steps // 2)) * 0.1
            else:
                # Grow back
                scale = 0.9 + ((current_step[0] - steps // 2) / (steps // 2)) * 0.1
                
            self.card_frame.place(
                relx=0.5, 
                rely=0.43, 
                anchor="center", 
                relwidth=0.85 * scale, 
                relheight=0.6
            )
            
            # Change content at middle
            if current_step[0] == steps // 2:
                if self.is_flipped:
                    self.language_label.config(text=card["translation"]["target_language"].upper())
                    self.word_label.config(text=card["translation"]["target_word"], fg="#ffffff")
                    self.card_frame.config(bg="#00d4ff")
                    self.language_label.config(bg="#00d4ff", fg="#ffffff")
                    self.word_label.config(bg="#00d4ff")
                    self.flip_hint.config(bg="#00d4ff", fg="#ffffff", text="Click card to flip back ←")
                else:
                    self.language_label.config(text=card["source_language"].upper())
                    self.word_label.config(text=card["source_word"], fg="#1a1a2e")
                    self.card_frame.config(bg="#ffffff")
                    self.language_label.config(bg="#ffffff", fg="#666666")
                    self.word_label.config(bg="#ffffff")
                    self.flip_hint.config(bg="#ffffff", fg="#999999", text="Click card to flip →")
            
            if current_step[0] < steps:
                self.flip_animation_id = self.root.after(20, step)
            else:
                self.flip_animation_id = None
                
        step()
        
    def next_card(self):
        if self.current_index < len(self.cards) - 1:
            self.current_index += 1
            self.show_card()
            self.play_audio()
            
    def prev_card(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.show_card()
            self.play_audio()
            
    def play_audio(self):
        card = self.cards[self.current_index]
        if self.is_flipped:
            word = card["translation"]["target_word"]
            lang = card["translation"]["target_language"]
        else:
            word = card["source_word"]
            lang = card["source_language"]
        
        # Map language to the format your TTS expects
        lang_map = {
            "German": "deutsch",
            "English": "english"
        }
        tts_lang = lang_map.get(lang, "english").lower()
        
        # Call TTS and run engine
        self.translator.read_words(word, tts_lang)
        

if __name__ == "__main__":
    
    Check = pyttsx3.init()
    props = Check.getProperty('voices')
    exist = False
    
    for prop in props:
        if "German" in prop.name :
            exist = True
            break
    
    if not exist:
        print("Deutsch voice is not installed in this device")
        print("Make sure that you install DE and EN Before Using This APP")
        exit(0)
    
    root = tk.Tk()
    app = FlashcardApp(root)
    app.translator.engine.runAndWait()
    root.mainloop()