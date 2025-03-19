import asyncio
from PyQt6.QtWidgets import QMessageBox

async def run_wave(govee_device, params, is_animating_flag, animation_duration, animation_start_time):
    try:
        color = params.get("color", (0, 255, 0))
        num_segments = params.get("segment_count", 12) # Get segment count from params

        segment_states = [(0, 0, 0)] * num_segments  # Initialize all off

        while is_animating_flag() and (asyncio.get_event_loop().time() - start_time < animation_duration):
            for i in range(1, segment_count + 1):
                await command_queue.put({"type": "segment_color", "segment": i, "red": color[0], "green": color[1], "blue": color[2]})
                await asyncio.sleep(0.02)
                if i > 1:
                    await asyncio.sleep(0.02)
                    await command_queue.put({"type": "segment_color", "segment": i - 1, "red": 0, "green": 0, "blue": 0})

            # Reset the final segment after the loop completes
            await command_queue.put({"type": "segment_color", "segment": segment_count, "red": 0, "green": 0, "blue": 0})
            
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"Error in wave animation: {e}")
        QMessageBox.critical(None, "Animation Error", f"Error in Wave animation: {e}")
    finally:
        pass # Cleanup will be handled in AnimationControls
