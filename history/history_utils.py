"""
Local HRV history storage and retrieval.

This module provides lightweight persistent storage of HRV analysis
results in a local JSON file, with a cap on maximum stored entries.

Features:
1. Uses `/history/history.json` to store HRV records.
2. Appends new entries with human-readable timestamps.
3. Keeps only the latest 20 entries to avoid unbounded growth.
4. Supports loading history as a list of records for display or sync.

Each entry contains:
- `timestamp`: formatted as "dd.mm.yyyy hh:mm"
- Rounded HRV metrics: mean_hr, mean_ppi, rmssd, sdnn, sns, pns

If the file does not exist or is corrupted, empty list is returned.
"""

import ujson
import time
import os

BASE_DIR = "/history"  
HISTORY_FILE = BASE_DIR + "/history.json"

HISTORY_FILE_hrv = BASE_DIR + "/hrv_analysis.json"

def save_to_history(data):
    """
    Save a new HRV data record to local history.

    Behaviour:
    - Attempts to load existing history file.
    - If file doesn't exist or is unreadable, starts with empty list.
    - Adds a human-readable timestamp to the record.
    - Rounds numerical HRV metrics to whole numbers for consistency.
    - Appends the new entry to the history list.
    - Retains only the most recent 20 entries (FIFO buffer).
    - Overwrites the history file with the updated list.

    Args:
        data (dict): HRV record containing keys like
            mean_hr, mean_ppi, rmssd, sdnn, sns, pns.
    """

    try:
        with open(HISTORY_FILE, "r") as f:
            history = ujson.load(f)
    except:
        history = []
        
    timestamp = time.localtime()
    data["timestamp"] = "{:02}.{:02}.{:04} {:02}:{:02}".format(
        timestamp[2],  # day
        timestamp[1],  # month
        timestamp[0],  # year
        timestamp[3],  # hour
        timestamp[4]   # minute
    )

    for key in ["mean_hr", "mean_ppi", "rmssd", "sdnn", "sns", "pns"]:
        if key in data:
            data[key] = round(data[key])

    history.append(data)

    if len(history) > 20:
        history = history[-20:]

    with open(HISTORY_FILE, "w") as f:
        ujson.dump(history, f)

def load_history():
    """
    Load saved HRV history records from JSON file.

    Returns:
        list: List of saved HRV records.
              Returns an empty list if the file is missing or unreadable.
    """
    
    try:
        with open(HISTORY_FILE, "r") as f:
            return ujson.load(f)
    except:
        return []


def append_to_hrv_history(data):
    try:
        # Читаем историю из уже существующего (даже если он пустой)
        with open(HISTORY_FILE_hrv, "r") as f:
            content = f.read()
            if not content.strip():
                history = []
            else:
                history = ujson.loads(content)

        # Добавляем метку времени
        timestamp = time.localtime()
        data["timestamp"] = "{:02}.{:02}.{:04} {:02}:{:02}".format(
            timestamp[2], timestamp[1], timestamp[0], timestamp[3], timestamp[4]
        )

        # Добавляем новую запись
        history.append(data)

        # Записываем обратно
        with open(HISTORY_FILE_hrv, "w") as f:
            ujson.dump(history, f)
            f.flush()
            time.sleep(0.1)

    except Exception as e:
        print("[HRV] ❌ Ошибка при сохранении:", e)