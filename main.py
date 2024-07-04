import os
import shutil
from pytube import YouTube
from Extractor import Extractor
import subprocess

# Function to clear directory contents
def clear_directory():
    try:
        os.remove("download/youtube_video.mp4")
    except Exception as e:
        print("no prev source to delete")
    for filename in os.listdir("./peaks"):
        file_path = os.path.join("./peaks", filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")

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
        output_file = os.path.join(output_path, f"./download/youtube_video.mp4")

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

if __name__ == "__main__":
    clear_directory()
    yt_video_url = "https://www.youtube.com/watch?v=ipbfrPZd-x4"

    duration_peak = 15 # in seconds / odd numbers

    extractor = Extractor(yt_video_url)

    svg_code = extractor.get_svg()

    points = extractor.extract_points_from_svg(svg_code)
    
    peaks = extractor.find_peaks(points, 40)
    print(peaks)
    extractor.plot_svg(points)
    extractor.plot_peaks(peaks)
    extractor.plot_save_show()
    
    download_youtube_video(yt_video_url)

    for i, (x,y) in enumerate(peaks):
        x_in_sec = extractor.peaks_to_time(x)
        m, s = divmod(x_in_sec, 60)

        extractor.extract_part(x_in_sec - (duration_peak/2), x_in_sec + (duration_peak/2), str(i)+"_peak_at["+str(int(m))+"_"+str(int(s))+"]")