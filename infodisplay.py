from config import Config


def print_console_info(cfg: Config, log_path: str) -> None:
    print("=" * 60)
    print(f"{' ' * 20}OPCUA MONITORING")
    print("=" * 60)
    print(f" Target Server : {cfg.OPCUA_URL}")
    print(" Status        : Running")
    print(f" Logs Location : {log_path}")
    print(" Instructions  : Press Ctrl+C to stop safely.")
    print("=" * 60)
    print()
