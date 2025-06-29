import os
import shutil

from config.constants import FLATTENED_DIR, ERRORS_DIR
from config.constants import BASE_DATA_DIR



def remove_contents(folder):
    if not os.path.exists(folder):
        print(f"Skipped: {folder} does not exist.")
        return

    files = os.listdir(folder)
    if not files:
        print(f"No files to remove in: {folder}")
        return

    for filename in files:
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Error removing {file_path}: {e}")
    print(f"Removed all contents from: {folder}")

# === Run cleanup ===
remove_contents(FLATTENED_DIR)
remove_contents(ERRORS_DIR)

# combined_path = os.path.join(BASE_DATA_DIR, "euro24_all_events_combined.csv")
# if os.path.exists(combined_path):
#     os.remove(combined_path)
#     print(f"Removed combined CSV: {combined_path}")



