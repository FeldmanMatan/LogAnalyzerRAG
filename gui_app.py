import customtkinter as ctk
import tkinter.filedialog as filedialog
import threading
import sqlite3
import sys
import os
import warnings

# Suppress specific DeprecationWarning from langgraph
warnings.filterwarnings("ignore", category=DeprecationWarning, module="langgraph")

# Setup the path to ensure imports work correctly from the root directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from langgraph.checkpoint.sqlite import SqliteSaver
from agents.supervisor import build_team_graph
from ingestion.teaching_engine import teach_single
from agents.batch_analyzer import analyze_log_file_in_batches

def extract_clean_text(content):
    """
    Helper function to extract clean text from complex response objects.
    Safely handles strings, lists, and nested dictionaries.
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                return item.get("text")
    return str(content)

# --- Initialize CustomTkinter Appearance ---
ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class LogAnalyzerUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Backend Initialization ---
        self.conn = sqlite3.connect('memory.db', check_same_thread=False)
        self.memory = SqliteSaver(self.conn)
        self.agent_app = build_team_graph(memory=self.memory)
        self.thread_config = {'configurable': {'thread_id': 'gui_session_1'}}

        # --- Window Setup ---
        self.title("LogAnalyzer AI - Enterprise Edition")
        self.geometry("1100x700")
        self.minsize(900, 600)

        # Configure grid layout (1 row, 2 columns)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- Sidebar Frame ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="LogAnalyzer AI", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Sidebar Navigation Buttons
        self.nav_chat_btn = ctk.CTkButton(self.sidebar_frame, text="💬 Investigator Chat", command=self.show_chat_frame)
        self.nav_chat_btn.grid(row=1, column=0, padx=20, pady=10)

        self.nav_batch_btn = ctk.CTkButton(self.sidebar_frame, text="📊 Batch Analysis", command=self.show_batch_frame)
        self.nav_batch_btn.grid(row=2, column=0, padx=20, pady=10)

        self.nav_teach_btn = ctk.CTkButton(self.sidebar_frame, text="🧠 Teaching Engine", command=self.show_teach_frame)
        self.nav_teach_btn.grid(row=3, column=0, padx=20, pady=10)

        # Appearance Mode Toggle
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"], command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 20))
        self.appearance_mode_optionemenu.set("Dark")

        # --- Main Views Setup ---
        self.chat_frame = ChatFrame(self)
        self.batch_frame = BatchAnalysisFrame(self)
        self.teach_frame = TeachingEngineFrame(self)

        # Default View
        self.show_chat_frame()

    def show_chat_frame(self):
        self._hide_all_frames()
        self.chat_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

    def show_batch_frame(self):
        self._hide_all_frames()
        self.batch_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

    def show_teach_frame(self):
        self._hide_all_frames()
        self.teach_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

    def _hide_all_frames(self):
        self.chat_frame.grid_forget()
        self.batch_frame.grid_forget()
        self.teach_frame.grid_forget()

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)


# ==========================================
# 1. Chat Investigator Frame
# ==========================================
class ChatFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=10)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Chat History Text Box
        self.chat_history = ctk.CTkTextbox(self, wrap="word", font=ctk.CTkFont(size=14))
        self.chat_history.grid(row=0, column=0, columnspan=2, padx=15, pady=(15, 10), sticky="nsew")
        self.chat_history.insert("0.0", "🚀 Welcome to the LogAnalyzer AI.\nI am connected to the Multi-Agent system. How can I help you today?\n\n")
        self.chat_history.configure(state="disabled")

        # Input Field
        self.input_entry = ctk.CTkEntry(self, placeholder_text="Ask the AI investigator (e.g., 'Analyze app_logs statistics...')")
        self.input_entry.grid(row=1, column=0, padx=(15, 10), pady=(0, 15), sticky="ew")
        self.input_entry.bind("<Return>", lambda event: self.send_message())

        # Send Button
        self.send_btn = ctk.CTkButton(self, text="Send", width=100, command=self.send_message)
        self.send_btn.grid(row=1, column=1, padx=(0, 15), pady=(0, 15), sticky="e")

    def send_message(self):
        user_text = self.input_entry.get()
        if not user_text.strip():
            return

        self._append_to_chat(f"🧑‍💻 You: {user_text}\n")
        self.input_entry.delete(0, "end")
        
        # Disable input while processing
        self.input_entry.configure(state="disabled")
        self.send_btn.configure(state="disabled")
        self._append_to_chat("🤖 DevOps AI is thinking...\n")

        threading.Thread(target=self._backend_call, args=(user_text,)).start()

    def _backend_call(self, query):
        try:
            response = self.master.agent_app.invoke({"messages": [("user", query)]}, config=self.master.thread_config)
            clean_text = extract_clean_text(response["messages"][-1].content)
        except Exception as e:
            clean_text = f"Error communicating with AI: {str(e)}"
        
        self.winfo_toplevel().after(0, self._handle_ai_response, clean_text)

    def _handle_ai_response(self, response_text):
        # Remove the 'thinking' text
        current_text = self.chat_history.get("1.0", "end")
        current_text = current_text.replace("🤖 DevOps AI is thinking...\n", "")
        self.chat_history.configure(state="normal")
        self.chat_history.delete("1.0", "end")
        self.chat_history.insert("end", current_text)
        
        # Append actual response
        self._append_to_chat(f"🤖 DevOps AI:\n{response_text}\n\n")
        
        # Re-enable input
        self.input_entry.configure(state="normal")
        self.send_btn.configure(state="normal")

    def _append_to_chat(self, text):
        self.chat_history.configure(state="normal")
        self.chat_history.insert("end", text)
        self.chat_history.see("end")
        self.chat_history.configure(state="disabled")


# ==========================================
# 2. Batch Analysis Frame
# ==========================================
class BatchAnalysisFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=10)
        self.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self, text="Batch Log Analysis", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, columnspan=3, pady=(20, 20), sticky="n")

        # File Selection
        ctk.CTkLabel(self, text="Log File Path:").grid(row=1, column=0, padx=15, pady=10, sticky="w")
        self.file_entry = ctk.CTkEntry(self, placeholder_text="Select a .log file...")
        self.file_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        self.browse_btn = ctk.CTkButton(self, text="Browse", command=self.browse_file)
        self.browse_btn.grid(row=1, column=2, padx=15, pady=10)

        # Chunk Size Selection
        ctk.CTkLabel(self, text="Chunk Size:").grid(row=2, column=0, padx=15, pady=10, sticky="w")
        self.chunk_entry = ctk.CTkEntry(self, placeholder_text="e.g., 50")
        self.chunk_entry.insert(0, "50")
        self.chunk_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        # Run Button
        self.run_btn = ctk.CTkButton(self, text="Run Analysis", fg_color="green", hover_color="darkgreen", command=self.run_analysis)
        self.run_btn.grid(row=3, column=0, columnspan=3, pady=(20, 10))

        # Output/Summary Box
        self.output_box = ctk.CTkTextbox(self, wrap="word", height=300)
        self.output_box.grid(row=4, column=0, columnspan=3, padx=15, pady=15, sticky="nsew")
        self.grid_rowconfigure(4, weight=1)

    def browse_file(self):
        filename = filedialog.askopenfilename(title="Select Log File", filetypes=(("Log Files", "*.log"), ("All Files", "*.*")))
        if filename:
            self.file_entry.delete(0, "end")
            self.file_entry.insert(0, filename)

    def run_analysis(self):
        file_path = self.file_entry.get()
        chunk_size = self.chunk_entry.get()
        if not file_path:
            self.output_box.insert("end", "⚠️ Please select a file first.\n")
            return

        self.output_box.insert("end", f"🚀 Starting Batch Analysis on {file_path} (Chunk size: {chunk_size})...\n")
        self.run_btn.configure(state="disabled")

        def task():
            try:
                c_size = int(chunk_size) if chunk_size else 50
                summary = analyze_log_file_in_batches(file_path, chunk_size=c_size)
                self.winfo_toplevel().after(0, self._on_analysis_complete, summary)
            except ValueError:
                self.winfo_toplevel().after(0, self._on_analysis_complete, "Error: Invalid chunk size. Please enter a valid integer.")
            except Exception as e:
                self.winfo_toplevel().after(0, self._on_analysis_complete, f"Error: {str(e)}")

        threading.Thread(target=task).start()

    def _on_analysis_complete(self, summary):
        self.output_box.insert("end", f"\n📊 === EXECUTIVE SUMMARY ===\n{summary}\n===========================\n")
        self.run_btn.configure(state="normal")


# ==========================================
# 3. Teaching Engine Frame
# ==========================================
class TeachingEngineFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=10)
        self.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self, text="Teaching Engine - Human Context Injection", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, columnspan=3, pady=(20, 20))

        # File Path
        ctk.CTkLabel(self, text="File Path:").grid(row=1, column=0, padx=15, pady=10, sticky="w")
        self.file_entry = ctk.CTkEntry(self, placeholder_text="Path to log file...")
        self.file_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        ctk.CTkButton(self, text="Browse", width=80, command=self.browse_file).grid(row=1, column=2, padx=15)

        # Lines
        line_frame = ctk.CTkFrame(self, fg_color="transparent")
        line_frame.grid(row=2, column=0, columnspan=2, sticky="w", padx=15, pady=10)
        ctk.CTkLabel(line_frame, text="Start Line:").pack(side="left")
        self.start_entry = ctk.CTkEntry(line_frame, width=60)
        self.start_entry.pack(side="left", padx=(10, 20))
        ctk.CTkLabel(line_frame, text="End Line:").pack(side="left")
        self.end_entry = ctk.CTkEntry(line_frame, width=60)
        self.end_entry.pack(side="left", padx=10)

        # Status
        ctk.CTkLabel(self, text="Status:").grid(row=3, column=0, padx=15, pady=10, sticky="w")
        self.status_menu = ctk.CTkOptionMenu(self, values=["golden", "anomaly"])
        self.status_menu.grid(row=3, column=1, sticky="w", padx=10)

        # Human Explanation
        ctk.CTkLabel(self, text="Human Explanation:").grid(row=4, column=0, padx=15, pady=10, sticky="nw")
        self.explanation_box = ctk.CTkTextbox(self, height=100)
        self.explanation_box.grid(row=4, column=1, columnspan=2, padx=(10, 15), pady=10, sticky="ew")

        # Save to Stats Checkbox & Log Type
        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.grid(row=5, column=0, columnspan=3, sticky="w", padx=15, pady=10)
        self.save_stats_var = ctk.StringVar(value="off")
        self.stats_checkbox = ctk.CTkCheckBox(stats_frame, text="Save to Statistics DB (Dual-Save)", variable=self.save_stats_var, onvalue="on", offvalue="off")
        self.stats_checkbox.pack(side="left")
        
        ctk.CTkLabel(stats_frame, text="Log Type:").pack(side="left", padx=(30, 10))
        self.log_type_entry = ctk.CTkEntry(stats_frame, placeholder_text="e.g., app_logs")
        self.log_type_entry.pack(side="left")

        # Submit Button
        self.submit_btn = ctk.CTkButton(self, text="Submit Knowledge 🧠", command=self.submit_knowledge)
        self.submit_btn.grid(row=6, column=0, columnspan=3, pady=30)
        
        # Result Label
        self.result_label = ctk.CTkLabel(self, text="", text_color="green")
        self.result_label.grid(row=7, column=0, columnspan=3)

    def browse_file(self):
        filename = filedialog.askopenfilename()
        if filename:
            self.file_entry.delete(0, "end")
            self.file_entry.insert(0, filename)

    def submit_knowledge(self):
        # Extract data from UI
        file_path = self.file_entry.get()
        start = self.start_entry.get()
        end = self.end_entry.get()
        status = self.status_menu.get()
        explanation = self.explanation_box.get("1.0", "end-1c")
        save_stats = self.save_stats_var.get() == "on"
        log_type = self.log_type_entry.get()

        # Basic Validation
        if not file_path or not start or not end or not explanation:
            self.result_label.configure(text="⚠️ Please fill in all required fields.", text_color="red")
            return

        self.result_label.configure(text="Processing... please wait.", text_color="white")
        self.submit_btn.configure(state="disabled")
        
        def task():
            try:
                result = teach_single(file_path, int(start), int(end), status, explanation, save_to_stats=save_stats, log_type=log_type)
                self.winfo_toplevel().after(0, self._on_teach_complete, result, "green")
            except ValueError:
                self.winfo_toplevel().after(0, self._on_teach_complete, "Error: Start and End lines must be valid numbers.", "red")
            except Exception as e:
                self.winfo_toplevel().after(0, self._on_teach_complete, f"Error: {str(e)}", "red")

        threading.Thread(target=task).start()

    def _on_teach_complete(self, result_text, color):
        self.result_label.configure(text=result_text, text_color=color)
        self.submit_btn.configure(state="normal")

if __name__ == "__main__":
    app = LogAnalyzerUI()
    app.mainloop()