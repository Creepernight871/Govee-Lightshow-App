import asyncio
from PyQt6.QtWidgets import QMessageBox

async def run_pulse(govee_device, params, is_animating_flag, animation_duration, animation_start_time):
    try:
        color = params.get("color", (255, 0, 0))  # Default color
        speed_bpm = params.get("speed", 60)
        pulse_interval = 60 / speed_bpm / 2
        min_duration = 1.0
        max_duration = 10.0

        animation_duration = max(min_duration, mine(animation_duration, max_duration))

        start_time = asyncio.get_event_loop().time()
        while is_animating_flag() and (asyncio.get_event_loop().time() - animation_start_time < animation_duration):
            cycle_time = (asyncio.get_event_loop().time() - start_time) % pulse_interval
            if cycle_time < pulse_interval / 2:
                #increases brightness
                brightness = int((cycle_time / (pulse_interval / 2)) * 100)
            else:
                #decreasing brightness
                brightness = 100 - int((cycle_time / (pulse_interval / 2) / (pulse_interval / 2)) * 100)
            await govee_device.set_rbg_color(red=color[0], green=color[1], blue=color[2])
            await govee_device.set_brightness(brightness=brightness)
            await asyncio.sleep(0.01) # smoother transition delay
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"Error in pulse animation: {e}")
        QMessageBox.critical(None, "Animation Error", f"Error in Pulse animation: {e}")
    finally:
        pass # Cleanup will be handled in AnimationControls
