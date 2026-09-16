from ast import Return
import tkinter as tk
import logging
from config import Config

logger = logging.getLogger(__name__)


class Window():
    def __init__(self, cfg: Config, log_path: str):
        self.is_running = True
        self.cfg = cfg
        self.log_path = log_path

        self.window = tk.Tk()
        self.label_space = tk.Label(bg="black")
        self.label_A = tk.Label(anchor="w", bg="black", fg="white", font=("Helvetica", 20))
        self.label_B = tk.Label(anchor="w", bg="black", fg="white", font=("Helvetica", 20))
        self.label_C = tk.Label(anchor="w", bg="black", fg="white", font=("Helvetica", 20))
        self.label_D = tk.Label(anchor="w", bg="black", fg="white", font=("Helvetica", 20))
        self.label_E = tk.Label(anchor="w", bg="black", fg="white", font=("Helvetica", 20))
        self.label_F = tk.Label(anchor="w", bg="black", fg="white", font=("Helvetica", 20))
        self.label_space.pack(pady=30, fill="both")
        self.label_A.pack(padx=17, fill="x")
        self.label_B.pack(padx=55, fill="x")
        self.label_C.pack(padx=55, fill="x")
        self.label_D.pack(padx=55, fill="x")
        self.label_E.pack(padx=55, fill="x")
        self.label_F.pack(padx=17, fill="x")


        self.window.configure(background='black')
        self.window.title("OPCUA STATUS")
        self.window.geometry("400x300")
        self.window.resizable(False, False)

        self.window_update(None)

    def window_update(self, opcua_server_state: int | None) -> None:
        if not self.is_running:
            return
        if opcua_server_state is None:
            text = "Connecting..."
            self.label_C.config(fg="Red")
        else:
            text = "Connected!"
            self.label_C.config(fg="Green")

        self.label_A.config(text=f"{f'=' * 60}")
        self.label_B.config(text=f"Target Server : {self.cfg.OPCUA_URL}")
        self.label_C.config(text=f"Status        : {text}")
        self.label_D.config(text=f"Logs Location : {self.log_path}")
        self.label_E.config(text=f"Instructions  : Close Window to stop safely.")
        self.label_F.config(text=f"{f'=' * 60}")

        self.window_refresh()

    def window_refresh(self) -> None:
        if not self.is_running:
            return

        try:
            self.window.update()
        except tk.TclError as err:
            self.is_running = False
            logger.error(f"Unexpected GUI error: {err}", exc_info=True)
        except Exception as err:
            self.is_running = False
            logger.error(f"Unexpected GUI error: {err}", exc_info=True)


    def print_console_info(self) -> None:
        print("=" * 60)
        print(f"{' ' * 20}OPCUA MONITORING")
        print("=" * 60)
        print(f" Target Server : {self.cfg.OPCUA_URL}")
        print(" Status        : Running")
        print(f" Logs Location : {self.log_path}")
        print(" Instructions  : Press Ctrl+C to stop safely.")
        print("=" * 60)
        print()


'''gui_text = (
f"{f'=' * 60} \n"
f" Target Server : {self.cfg.OPCUA_URL}\n"
f" Status        : {text}\n"
f" Logs Location : {self.log_path}\n"
f" Instructions  : Close Window to stop safely.\n"
f"{f'=' * 60} \n"
)'''
