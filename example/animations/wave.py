import asyncio
from PyQt6.QtWidgets import QMessageBox

async def run_wave(govee_device, params, is_animating_flag, animation_duration, animation_start_time):
    try:
        color = params.get("color", (0, 255, 0))
        speed = params.get("speed", 5)
        direction = params.get("direction", "Forward")
        interval = 0.1  # Adjust for smoother/faster wave
        num_segments = params.get("segment_count", 12) # Get segment count from params

        segment_states = [(0, 0, 0)] * num_segments  # Initialize all off

        while is_animating_flag() and (asyncio.get_event_loop().time() - animation_start_time < animation_duration):
            # Move the 'on' segment
            if direction == "Forward":
                on_index = (int((asyncio.get_event_loop().time() - animation_start_time) * speed) % num_segments)
            else:  # Backward
                on_index = (num_segments - 1 - int((asyncio.get_event_loop().time() - animation_start_time) * speed) % num_segments)

            new_states = [(0, 0, 0)] * num_segments
            new_states[on_index] = color

            await govee_device.set_segments_color(new_states)
            await asyncio.sleep(interval)
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"Error in wave animation: {e}")
        QMessageBox.critical(None, "Animation Error", f"Error in Wave animation: {e}")
    finally:
        pass # Cleanup will be handled in AnimationControls
