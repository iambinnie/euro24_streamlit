import os
from datetime import datetime

from config.constants import BASE_DATA_DIR


# Define full paths for all subdirectories
required_dirs = [
    BASE_DATA_DIR,
    os.path.join(BASE_DATA_DIR, "raw"),
    os.path.join(BASE_DATA_DIR, "flattened"),
    os.path.join(BASE_DATA_DIR, "errors")
]

# Setup log path
log_path = os.path.join(BASE_DATA_DIR, "setup.log")

# Create directories and write status
log_lines = [f"[{datetime.now().isoformat()}] Directory setup check:\n"]

for directory in required_dirs:
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
        log_lines.append(f"  CREATED: {directory}\n")
    else:
        log_lines.append(f"  EXISTS:  {directory}\n")

with open(log_path, "a", encoding="utf-8") as log_file:
    log_file.writelines(log_lines)

print("Directory check complete. Log written to:", log_path)
