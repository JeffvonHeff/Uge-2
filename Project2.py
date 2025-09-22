import os
from typing import Dict

def split_log_by_level(log_path: str, output_dir: str) -> Dict[str, str]:
    level_to_path: Dict[str, str] = {}
    level_handles = {}
    try:
        with open(log_path, "r", encoding="utf-8") as log_file:
            for raw_line in log_file:
                line = raw_line.strip()
                if not line:
                    continue
                parts = line.split(maxsplit=3)
                if len(parts) < 3:
                    continue
                level = parts[2]
                if level not in level_handles:
                    output_path = os.path.join(output_dir, f"{level}_logs.txt")
                    level_handles[level] = open(output_path, "w", encoding="utf-8")
                    level_to_path[level] = output_path
                level_handles[level].write(raw_line)
    finally:
        for handle in level_handles.values():
            handle.close()
    return level_to_path

def verify_log_file(log_path: str) -> int:
    with open(log_path, "r", encoding="utf-8") as log_file:
        return sum(1 for _ in log_file)

def main() -> None:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    log_filename = "app_log (logfil analyse) - random.txt"
    log_path = os.path.join(base_dir, log_filename)

    if not os.path.exists(log_path):
        print(f"Log file '{log_filename}' not found at {base_dir}.")
        return

    level_files = split_log_by_level(log_path, base_dir)
    total_lines = verify_log_file(log_path)

    print(f"Processed {total_lines} log lines from '{log_filename}'.")
    if level_files:
        print("Created the following per-level log files:")
        for level, path in sorted(level_files.items()):
            print(f"  {level}: {path}")
    else:
        print("No log entries were found to split.")

if __name__ == "__main__":
    main()
