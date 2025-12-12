from machine import Pin
import time
from fifo import Fifo

"""
Encoder utility module for rotary input with button debounce.

This module provides support for reading a mechanical rotary encoder and
detecting rotation direction, with optional encoder button debounce.

Main features:
1. A `Pin` is initialized for the encoder button with internal pull-up.
2. A global debounce function `is_encoder_pressed()` filters button noise.
3. A `Encoder` class handles quadrature signal reading using GPIO interrupts.
   - Tracks signal on channel A and B.
   - Uses a FIFO to queue turn direction: -1 (left), +1 (right).
   - Supports polling via `get_turn()` method.
4. All IRQs use `hard=True` for low-latency response, suitable for MicroPython.

Dependencies:
- `machine.Pin` for GPIO input.
- `fifo.Fifo` custom FIFO class for tracking event queue.
"""

def scale(value, v_min, v_max, y_min=0, y_max=63):
    """
    Scales a value from input range [v_min, v_max] to output range [y_min, y_max].
    """
    if v_max == v_min:
        return (y_min + y_max) // 2  # prevent divide-by-zero
    norm = (value - v_min) / (v_max - v_min)
    return int(y_min + (1.0 - norm) * (y_max - y_min))


ENCODER_BUTTON_PIN = 12
encoder_button = Pin(ENCODER_BUTTON_PIN, Pin.IN, Pin.PULL_UP)
last_press_time = 0

def is_encoder_pressed():
    """
    Check if the encoder button is pressed with debounce.

    This function implements a simple software debounce using time ticks.
    The encoder button is considered 'pressed' if:
    - The pin reads LOW (`value() == 0`).
    - At least 300ms have passed since the last registered press.

    Returns:
        bool: True if a valid (debounced) button press is detected,
              False otherwise.
    """

    global last_press_time
    if encoder_button.value() == 0:
        now = time.ticks_ms()
        if time.ticks_diff(now, last_press_time) > 300:
            last_press_time = now
            return True
    return False

class Encoder:
    """
    Rotary encoder handler with direction detection and FIFO queuing.

    This class provides:
    - Initialization of encoder pins A and B as GPIO inputs.
    - IRQ handler on pin A (rising edge) to detect rotation.
    - Direction detection using the state of pin B.
    - Enqueueing of turn direction into a FIFO for later polling.

    Usage:
        enc = Encoder(pin_a=14, pin_b=15)
        dir = enc.get_turn()  # Returns -1, 1, or 0
    """

    def __init__(self, pin_a, pin_b):
        """
        Initialize encoder pins and attach interrupt.

        Args:
            pin_a (int): GPIO pin number connected to encoder channel A.
            pin_b (int): GPIO pin number connected to encoder channel B.

        Behaviour:
        - Configures both pins as input.
        - Allocates a FIFO buffer (30 items, int type).
        - Attaches IRQ to pin A for rising edge events.
        - When triggered, `handler` is called to detect direction.
        """

        self.a = Pin(pin_a, Pin.IN)
        self.b = Pin(pin_b, Pin.IN)
        self.fifo = Fifo(30, typecode='i')
        self.a.irq(trigger=Pin.IRQ_RISING, handler=self.handler, hard=True)

    def handler(self, pin):
        """
        Interrupt handler for encoder rotation.

        Behaviour:
        - If pin B is HIGH when A rises, it’s counter-clockwise (-1).
        - If pin B is LOW when A rises, it’s clockwise (+1).
        - The direction value is pushed to the FIFO.

        This method is intended to be used as a hardware IRQ callback.
        """

        if self.b():
            self.fifo.put(-1)
        else:
            self.fifo.put(1)

    def get_turn(self):
        """
        Poll the encoder for the latest turn direction.

        Returns:
            int: -1 if rotated left, 1 if rotated right, 0 if no rotation.
                 Values are dequeued from FIFO, so repeated calls yield new events.
        """
        
        if self.fifo.has_data():
            return self.fifo.get()
        return 0
