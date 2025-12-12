from machine import ADC, Pin
import rp2

adc = ADC(Pin(26))  

@rp2.asm_pio()
def sampler():
    label("loop")
    nop()       [31]     
    push()
    jmp("loop")

sm = rp2.StateMachine(0, sampler, freq=2_000_000) 

def start_sampling():
    sm.active(1)

def stop_sampling():
    sm.active(0)

def read_sample():
    if sm.rx_fifo():
        _ = sm.get()  
        value = adc.read_u16()
        return value
    return None
