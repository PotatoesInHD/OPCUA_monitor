from config import Config


def print_console_info(cfg: Config, log_path: str) -> None:
    print("=" * 60)
    print(f"{' ' * 20}OPC UA MONITORING")
    print("=" * 60)
    print(f" Target Server : {cfg.OPCUA_URL}")
    print(f" Status        : Running")
    print(f" Logs Location : {log_path}")
    print(f" Instructions  : Press Ctrl+C to stop safely.")
    print(f"=" * 60)
    print()
