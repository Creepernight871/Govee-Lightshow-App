import asyncio
from PyQt6.QtWidgets import QMessageBox

async def run_explode(govee_device, params, is_animating_flag, animation_duration, animation_start_time):
    try:
        color = params.get("color", (255, 0, 255))
        speed = params.get("speed", 5)
        interval = 0.2
        num_segments = params.get("segment_count", 12) # Get segment count from params
        center = num_segments // 2

        while is_animating_flag() and (asyncio.get_event_loop().time() - animation_start_time < animation_duration):
            time_elapsed = asyncio.get_event_loop().time() - animation_start_time
            progress = int(time_elapsed * speed)

            segment_colors = [(0, 0, 0)] * num_segments
            for i in range(num_segments):
                distance_from_center = abs(i - center)
                if (num_segments - 1 - distance_from_center) < progress:
                    segment_colors[i] = color
            await govee_device.set_segment_color_rgb(segment_colors)
            await asyncio.sleep(interval)
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"Error in explode animation: {e}")
        QMessageBox.critical(None, "Animation Error", f"Error in Explode animation: {e}")
    finally:
        pass # Cleanup will be handled in AnimationControls
