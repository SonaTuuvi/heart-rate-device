from ui.oled import oled, WIDTH, GRAPH_TOP, GRAPH_HEIGHT, GRAPH_BOTTOM, SIGNAL_MIN, SIGNAL_MAX, GAIN
import time
from core.hrm import calibrate_threshold, pulse_sensor


def process_sample(raw, smoothed, threshold, last_value, beat_times):
    smoothed = int(0.2 * raw + 0.8 * smoothed)
    beat = False
    interval = None

    if last_value < threshold and smoothed >= threshold:
        beat = True
        now = time.ticks_ms()
        beat_times.append(now)
        if len(beat_times) > 1:
            interval = time.ticks_diff(beat_times[-1], beat_times[-2])
            if not (250 < interval < 2000):
                interval = None

    return smoothed, beat, interval


def draw_ecg_frame(raw_data, time_left, bpm=None, beat=False, v_min=None, v_max=None):
    """
    Draw ECG graph using either adaptive or fixed scaling.
    """
    oled.fill(0)
    display_data = raw_data[-WIDTH:]

    # Adaptive or fixed vertical scaling
    local_min = min(display_data) if v_min is None else v_min
    local_max = max(display_data) if v_max is None else v_max

    def scale(val):
        if local_max == local_min:
            return GRAPH_TOP + GRAPH_HEIGHT // 2
        norm = (val - local_min) / (local_max - local_min)
        return int(GRAPH_TOP + (1.0 - norm) * (GRAPH_HEIGHT - 1))

    scaled = [scale(val) for val in display_data]

    for x in range(1, len(scaled)):
        oled.line(x - 1, scaled[x - 1], x, scaled[x], 1)

    oled.text(f"{time_left}s", 0, 0)
    if bpm is not None:
        oled.text(f"{bpm} BPM", 60, 0)
    if beat:
        oled.text("♥", 110, 0)

    oled.show()


def show_countdown_animation(duration=30):
    """
    Show ECG animation with hybrid scaling:
    - First 2 seconds use adaptive auto-scaling
    - Then switch to fixed min/max based on early data
    """
    
    start = time.ticks_ms()
    intervals = []
    beat_times = []
    last_value = 0
    smoothed = 0

    threshold = calibrate_threshold()
    buffer = [SIGNAL_MIN] * WIDTH

    scaling_samples = []  # For collecting initial signal range
    fixed_scaling_ready = False
    v_min_fixed = None
    v_max_fixed = None

    while time.ticks_diff(time.ticks_ms(), start) < duration * 1000:
        now = time.ticks_ms()
        elapsed = (now - start) // 1000
        remaining = duration - elapsed

        raw = pulse_sensor.read_u16()
        smoothed, beat, interval = process_sample(
            raw, smoothed, threshold, last_value, beat_times)
        last_value = smoothed

        if interval:
            intervals.append(interval)

        buffer.append(smoothed)
        if len(buffer) > WIDTH:
            buffer.pop(0)

        # Collect samples for scaling during first 2 seconds
        if not fixed_scaling_ready:
            scaling_samples.append(smoothed)
            if elapsed >= 2:
                v_min_fixed = min(scaling_samples)
                v_max_fixed = max(scaling_samples)
                fixed_scaling_ready = True

        # Draw frame with fixed or adaptive scaling
        if fixed_scaling_ready:
            draw_ecg_frame(buffer, time_left=remaining, bpm=intervals and 60000 // intervals[-1], beat=beat,
                           v_min=v_min_fixed, v_max=v_max_fixed)
        else:
            draw_ecg_frame(buffer, time_left=remaining, bpm=intervals and 60000 // intervals[-1], beat=beat)

        time.sleep_ms(20)

    return intervals

def show_countdown_animation_kubios(duration=30):
    start = time.ticks_ms()
    last_second = -1

    intervals = []
    beat_times = []
    threshold = calibrate_threshold()
    last_value = 0

    ecg_buffer = []         # small rolling window of recent sensor values
    max_ecg_length = 128    # width of the OLED

    while time.ticks_diff(time.ticks_ms(), start) < duration * 1000:
        elapsed = time.ticks_diff(time.ticks_ms(), start) // 1000
        remaining = duration - elapsed

        # --- Read pulse sensor ---
        value = pulse_sensor.read_u16()

        # Update ECG buffer
        ecg_buffer.append(value)
        if len(ecg_buffer) > max_ecg_length:
            ecg_buffer.pop(0)

        # --- Detect beats (same logic as before) ---
        if last_value < threshold and value >= threshold:
            now = time.ticks_ms()
            beat_times.append(now)
            if len(beat_times) > 1:
                interval = time.ticks_diff(beat_times[-1], beat_times[-2])
                if 250 < interval < 2000:
                    intervals.append(interval)
        last_value = value

        # --- Only update text header once per second ---
        if remaining != last_second:
            last_second = remaining

        # --- Draw ECG graph (FULL SCREEN UPDATE) ---
        draw_ecg_frame_kubios(
            data=ecg_buffer,
            time_left=remaining,
            bpm=None  # optional: compute live BPM if wanted
        )

        time.sleep_ms(5)

    return intervals



def draw_ecg_frame_kubios(data, time_left, bpm=None):
    oled.fill_rect(0, 14, 128, 50, 0)
    if not data:
        oled.show()
        return

    # -------- OPTIONAL SMOOTHING (makes graph less noisy) ----------
    def smooth(arr, window=3):
        if len(arr) < window:
            return arr
        sm = []
        for i in range(len(arr)):
            s = max(0, i - window)
            e = min(len(arr), i + window)
            sm.append(sum(arr[s:e]) // (e - s))
        return sm

    data = smooth(data, window=3)

    # -------- SCALING & CENTERING IMPROVEMENTS ----------
    max_val = max(data)
    min_val = min(data)

    graph_height = 48
    top_margin = 14

    # Use 80% of area for the waveform → padding on top/bottom
    usable_height = int(graph_height * 0.8)
    vertical_offset = int(graph_height * 0.1)

    scale = usable_height / (max_val - min_val) if max_val != min_val else 1

    # Draw waveform line-by-line
    for x in range(len(data) - 1):
        y1 = top_margin + vertical_offset + usable_height - int((data[x] - min_val) * scale)
        y2 = top_margin + vertical_offset + usable_height - int((data[x + 1] - min_val) * scale)
        oled.line(x, y1, x + 1, y2, 1)

    # Header bar
    oled.fill_rect(0, 0, 128, 13, 0)
    oled.text(f"{time_left}s", 0, 0)
    if bpm is not None:
        oled.text(f"{bpm} BPM", 64, 0)

    oled.show()
