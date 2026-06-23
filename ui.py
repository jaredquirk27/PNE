from database import initialize_database
from prompt_builder import build_ai_prompt
from main import get_current_day
import os

print("Current Directory:")
print(os.getcwd())

from llm_provider import generate_response

from chat import persist_chat_exchange
import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class NarrativeApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Persistent Narrative Engine")
        self.geometry("1200x800")

        self.conn, self.cursor = initialize_database()
        self.character = "Baras"
        self.build_ui()

    def build_ui(self):

        # LEFT SIDEBAR

        self.sidebar = ctk.CTkFrame(self, width=250)
        self.sidebar.pack(side="left", fill="y")

        self.title_label = ctk.CTkLabel(
            self.sidebar,
            text="Persistent Narrative Engine",
            font=("Arial", 20, "bold")
        )

        self.title_label.pack(pady=20)

        self.character_button = ctk.CTkButton(
            self.sidebar,
            text="Characters"
        )

        self.character_button.pack(
            padx=10,
            pady=5,
            fill="x"
        )

        self.memory_button = ctk.CTkButton(
            self.sidebar,
            text="Memories"
        )

        self.memory_button.pack(
            padx=10,
            pady=5,
            fill="x"
        )

        self.story_button = ctk.CTkButton(
            self.sidebar,
            text="Story State"
        )

        self.story_button.pack(
            padx=10,
            pady=5,
            fill="x"
        )

        # MAIN CHAT AREA

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(
            side="right",
            fill="both",
            expand=True
        )

        self.chat_box = ctk.CTkTextbox(
            self.main_frame
        )

        self.chat_box.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        self.input_frame = ctk.CTkFrame(
            self.main_frame
        )

        self.input_frame.pack(
            fill="x",
            padx=10,
            pady=10
        )

        self.user_input = ctk.CTkEntry(
            self.input_frame
        )

        self.user_input.pack(
            side="left",
            fill="x",
            expand=True,
            padx=5
        )

        self.send_button = ctk.CTkButton(
            self.input_frame,
            text="Send",
            command=self.send_message
        )

        self.send_button.pack(
            side="right",
            padx=5
        )

    def send_message(self):

        user_message = self.user_input.get()

        if not user_message:
            return

        self.chat_box.insert(
            "end",
            f"\nYou: {user_message}\n"
        )

        self.user_input.delete(
            0,
            "end"
        )

        self.update()

        try:

            prompt = build_ai_prompt(
                self.cursor,
                self.character,
                user_message
            )

            response = generate_response(
                prompt
            )

            self.chat_box.insert(
                "end",
                f"\n{self.character}: {response}\n"
            )

            found_memories = persist_chat_exchange(
                self.cursor,
                self.character,
                user_message,
                response,
                get_current_day(self.cursor)
            )

            self.conn.commit()

        except Exception as e:

            self.chat_box.insert(
                "end",
                f"\nERROR: {str(e)}\n"
        )

        self.chat_box.see("end", "Persistent Narrative Engine Ready\n\n")


app = NarrativeApp()
app.mainloop()