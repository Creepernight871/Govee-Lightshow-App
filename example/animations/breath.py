import asyncio
from PyQt6.QtWidgets import QMessageBox

async def run_breath(govee_device, params, is_animating_flag, animation_duration, animation_start_time):
    try:
        color = params.get("color", (0, 0, 255))
        speed = params.get("speed", 3)
        interval = 0.1
        cycle_duration = 2.0 / speed  # Time for one full breath cycle (in and out)

        while is_animating_flag() and (asyncio.get_event_loop().time() - animation_start_time < animation_duration):
            time_in_cycle = (asyncio.get_event_loop().time() - animation_start_time) % cycle_duration
            if time_in_cycle < cycle_duration / 2:
                # Fade in
                brightness = int((time_in_cycle / (cycle_duration / 2)) * 100)
            else:
                # Fade out
                brightness = 100 - int(((time_in_cycle - cycle_duration / 2) / (cycle_duration / 2)) * 100)

            await govee_device.set_color_rgb(color=color)
            await govee_device.set_brightness(brightness=brightness)
            await asyncio.sleep(interval)
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"Error in breath animation: {e}")
        QMessageBox.critical(None, "Animation Error", f"Error in Breath animation: {e}")
    finally:
        pass # Cleanup will be handled in AnimationControls
