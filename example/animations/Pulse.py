import asyncio
from PyQt6.QtWidgets import QMessageBox

async def run_pulse(govee_device, params, is_animating_flag, animation_duration, animation_start_time):
    try:
        color = params.get("color", (255, 0, 0))  # Default color
        speed_bpm = params.get("speed", 60)
        pulse_interval = 60 / speed_bpm / 2

        while is_animating_flag() and (asyncio.get_event_loop().time() - animation_start_time < animation_duration):
            await govee_device.set_rbg_color(red=color[0], green=color[1], blue=color[2])
            await asyncio.sleep(pulse_interval)
            await govee_device.set_color_rgb(color=(0, 0, 0))
            await asyncio.sleep(pulse_interval)
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"Error in pulse animation: {e}")
        QMessageBox.critical(None, "Animation Error", f"Error in Pulse animation: {e}")
    finally:
        pass # Cleanup will be handled in AnimationControls
