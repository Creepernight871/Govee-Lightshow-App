import asyncio
from PyQt6.QtWidgets import QMessageBox

async def run_segment_pulse(govee_device, params, is_animating_flag, animation_duration, animation_start_time):
    try:
        color = params.get("color", (255, 165, 0))
        speed_bpm = params.get("speed", 60)
        pulse_interval = 60 / speed_bpm / 2
        num_segments = params.get("segment_count", 12) # Get segment count from params

        while is_animating_flag() and (asyncio.get_event_loop().time() - animation_start_time < animation_duration):
            for i in range(num_segments):
                segment_colors = [(0, 0, 0)] * num_segments
                segment_colors[i] = color
                await govee_device.set_segments_color(segment_colors)
                await asyncio.sleep(pulse_interval / num_segments) # Stagger the pulses
                if not is_animating_flag():
                    break
            if not is_animating_flag():
                break
            await asyncio.sleep(pulse_interval) # Wait for the full cycle
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"Error in segment pulse animation: {e}")
        QMessageBox.critical(None, "Animation Error", f"Error in Segment Pulse animation: {e}")
    finally:
        pass # Cleanup will be handled in AnimationControls
