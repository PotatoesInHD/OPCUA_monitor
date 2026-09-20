import tkinter as tk

from config import Config
from exceptions import WindowCloseError


class Window:
    def __init__(
        self, cfg: Config, log_path: str, file_path: str="Facticulating...",
        timestamp: str="Unknown...", opcua_server_state: int | None=None
    ) -> None:

        self.cfg = cfg
        self.log_path = log_path
        self.file_path = file_path
        self.timestamp = timestamp
        self.opcua_server_state = opcua_server_state

        self.window = tk.Tk()

        self.label_space = tk.Label(bg="black")
        self.label_Title = tk.Label(anchor="w", bg="black", fg="white", font=("Consolas", 15))
        self.label_1 = tk.Label(anchor="w", bg="black", fg="white", font=("Consolas", 15))
        self.label_2 = tk.Label(anchor="w", bg="black", fg="white", font=("Consolas", 15))
        self.label_3 = tk.Label(anchor="w", bg="black", fg="white", font=("Consolas", 15))
        self.label_4 = tk.Label(anchor="w", bg="black", fg="white", font=("Consolas", 15))
        self.label_5 = tk.Label(anchor="w", bg="black", fg="white", font=("Consolas", 15))
        self.label_6 = tk.Label(anchor="w", bg="black", fg="white", font=("Consolas", 15))
        self.label_7 = tk.Label(anchor="w", bg="black", fg="white", font=("Consolas", 15))
        self.label_8 = tk.Label(anchor="w", bg="black", fg="white", font=("Consolas", 15))

        self.label_space.pack(pady=30, fill="both")
        self.label_Title.pack(padx=17, fill="x")
        self.label_1.pack(padx=17, fill="x")
        self.label_2.pack(padx=55, fill="x")
        self.label_3.pack(padx=55, fill="x")
        self.label_4.pack(padx=55, fill="x")
        self.label_5.pack(padx=55, fill="x")
        self.label_6.pack(padx=55, fill="x")
        self.label_7.pack(padx=55, fill="x")
        self.label_8.pack(padx=17, fill="x")

        self.window.configure(background='black')
        self.window.title("OPCUA FILE MONITOR")
        self.window.geometry("800x640")
        #self.window.resizable(False, False)

        self.window_update()

    def window_update(self) -> None:
        if self.opcua_server_state is None:
            text = "Connecting..."
            self.label_3.config(fg="Red")
        else:
            text = "Connected!"
            self.label_3.config(fg="Green")

        self.label_Title.config(text=f"{'=' * 60}\nOPCUA FILE MONITORING STATUS")
        self.label_1.config(text=f"{f'=' * 60}")
        self.label_2.config(text=f"Target Server   : {self.cfg.OPCUA_URL}")
        self.label_3.config(text=f"Status          : {text}")
        self.label_4.config(text=f"Logs Location   : {self.log_path}")
        self.label_5.config(text=f"Monitored File  : {self.file_path}")
        self.label_6.config(text=f"Recent TimeStamp: {self.timestamp}")
        self.label_7.config(text=f"Instructions    : Close Window to stop program safely.")
        self.label_8.config(text=f"{f'=' * 60}")

        if not self.window.winfo_exists():
            raise WindowCloseError("Program closed by user but had WindowCloseError")
        self.window.update()

    def print_console_info(self) -> None:
        print("=" * 60)
        print(f"{' ' * 20}OPCUA MONITORING")
        print("=" * 60)
        print(f" Target Server : {self.cfg.OPCUA_URL}")
        print(" Status        : Running")
        print(f" Logs Location : {self.log_path}")
        print(" Instructions  : Press Ctrl+C to stop program safely.")
        print("=" * 60)
        print()
