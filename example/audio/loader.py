import librosa

def load_audio(file_path):
    """
    Loads an audio file and returns audio data.

    Args:
        file_path (str): The path to the audio file.

    Returns:
        dict: A dictionary containing:
            'audio_data' (np.ndarray): The audio time series.
            'sample_rate' (int): The sampling rate of the audio.
            'duration' (float): The duration of the audio in seconds.
        Returns None if there's an error loading the file.
    """
    try:
        audio_data, sample_rate = librosa.load(file_path)
        duration = librosa.get_duration(y=audio_data, sr=sample_rate)
        return {
            'audio_data': audio_data,
            'sample_rate': sample_rate,
            'duration': duration
        }
    except Exception as e:
        print(f"Error loading audio file {file_path}: {e}")
        return None

if __name__ == '__main__':
    # Example usage (you'll need an audio file named 'test.mp3' in the same directory)
    audio_info = load_audio('test.mp3')
    if audio_info:
        print(f"Audio loaded successfully:")
        print(f"  Sample Rate: {audio_info['sample_rate']}")
        print(f"  Duration: {audio_info['duration']} seconds")
        print(f"  Audio Data shape: {audio_info['audio_data'].shape}")
    else:
        print("Failed to load audio.")
