from pytube import YouTube
import os
import subprocess

# Function to download YouTube video and audio, then merge them
def download_youtube_video(url, output_path='.'):
    try:
        # Create a YouTube object
        yt = YouTube(url)
        
        # Get the highest resolution video-only stream
        video_stream = yt.streams.filter(only_video=True, file_extension='mp4').order_by('resolution').desc().first()
        # Get the highest quality audio-only stream
        audio_stream = yt.streams.filter(only_audio=True, file_extension='mp4').order_by('abr').desc().first()

        # Download video and audio streams
        print(f"Downloading video for {yt.title}...")
        video_file = os.path.join(output_path, 'video_temp.mp4')
        video_stream.download(output_path=output_path, filename='video_temp.mp4')
        print("Video download completed!")

        print(f"Downloading audio for {yt.title}...")
        audio_file = os.path.join(output_path, 'audio_temp.mp4')
        audio_stream.download(output_path=output_path, filename='audio_temp.mp4')
        print("Audio download completed!")

        # Ensure a valid filename for the output file
        safe_title = yt.title.replace('/', '_').replace('\\', '_')
        output_file = os.path.join(output_path, f"{safe_title}.mp4")

        # Merge video and audio using ffmpeg
        command = [
            'ffmpeg', '-i', video_file, '-i', audio_file, 
            '-c', 'copy', output_file
        ]
        subprocess.run(command, check=True)

        # Clean up temporary files
        os.remove(video_file)
        os.remove(audio_file)

        print(f"Merge completed! File saved as {output_file}")
    except Exception as e:
        print(f"An error occurred: {e}")

# URL of the YouTube video
url = 'https://www.youtube.com/watch?v=91sUAWUBfpE&t=8s'

# Call the function to download and merge the video
download_youtube_video(url)
