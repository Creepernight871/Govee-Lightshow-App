import asyncio
from PyQt6.QtWidgets import QMessageBox

async def run_wave(govee_device, params, is_animating_flag, animation_duration, animation_start_time):
    """
    Runs a wave animation on the Govee light strip.

    Args:
        govee_device: The Govee device object.
        params: A dictionary of animation parameters (color, speed, direction).
        is_animating_flag: A function that returns True if the animation should continue.
        animation_duration: The duration of the animation in seconds.
        animation_start_time: The start time of the animation.
    """
    try:
        color = params.get("color", (255, 0, 0))  # Default color is red
        speed_bpm = params.get("speed", 60)  # Default speed is 60 beats per minute
        direction = params.get("direction", "left")  # Default direction is left
        segment_count = 15  # Set the segment count to 15
        wave_interval = 60 / speed_bpm  # Calculate the time interval between wave movements
        min_duration = 1.0  # Minimum animation duration
        max_duration = 10.0  # Maximum animation duration

        # Clamp the animation duration to the allowed range
        animation_duration = max(min_duration, min(animation_duration, max_duration))

        start_time = asyncio.get_event_loop().time()  # Get the current time
        position = 1  # Start at the first segment (index 1)

        print(f"Direction: {direction}")
        print(f"Segment Count: {segment_count}")

        # Command queue to serialize commands and smooth out animation
        command_queue = asyncio.Queue()

        # Task to process commands from the queue
        async def process_commands():
            """Processes commands from the command queue."""
            while is_animating_flag():  # Check if the animation is still running
                command = await command_queue.get()
                if command["type"] == "segment_color":
                    await govee_device.set_segment_rgb_color(command["segment"], command["red"], command["green"], command["blue"])
                    await asyncio.sleep(0.04)  # Small delay between commands for smoother transitions
                command_queue.task_done()

        # Start the command processing task
        asyncio.create_task(process_commands())

        while is_animating_flag() and (asyncio.get_event_loop().time() - start_time < animation_duration):
            for i in range(1, segment_count + 1):
                # Add command to the queue to set the current segment's color
                await command_queue.put(
                    {"type": "segment_color", "segment": i, "red": color[0], "green": color[1], "blue": color[2]})
                await asyncio.sleep(0.04)  # small delay between lighting up each segment.
                if i > 1:  # Prevent index error for the first segment
                    # Add command to the queue to turn off the previous segment
                    await command_queue.put(
                        {"type": "segment_color", "segment": i - 1, "red": 0, "green": 0, "blue": 0})

            # Reset the final segment after the loop completes
            await command_queue.put(
                {"type": "segment_color", "segment": segment_count, "red": 0, "green": 0, "blue": 0})

    except Exception as e:
        print(f"Error in wave animation: {e}")
        QMessageBox.critical(None, "Animation Error", f"Error in Wave animation: {e}")
    finally:
        pass
