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

def download_youtube_video(url, output_path='./download'):
    try:
        # Create a YouTube object
        yt = YouTube(url)
        
        # Get the highest resolution video-only stream
        video_stream = yt.streams.filter(only_video=True, file_extension='mp4').order_by('resolution').desc().first()
        # Download video and audio streams
        print(f"Downloading video for {yt.title}...")
        video_stream.download(output_path=output_path, filename='youtube_video.mp4')
        print("Video download completed!")
    except Exception as e:
        print(f"An error occurred: {e}")

def get_video_length(video_path):
    command = [
        'ffprobe', '-v', 'error', '-show_entries', 
        'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', video_path
    ]
    
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"Error occurred: {result.stderr}")
        return None
    
    duration = float(result.stdout.strip())
    return duration

if __name__ == "__main__":
    clear_directory()
    yt_video_url = "https://www.youtube.com/watch?v=ipbfrPZd-x4"

    duration_peak = 15 # in seconds / odd numbers

    extractor = Extractor(yt_video_url)

    svg_code = extractor.get_svg()

    points = extractor.extract_points_from_svg(svg_code)
    
    peaks = extractor.find_peaks(points)
    print(peaks)
    extractor.plot_svg(points)
    extractor.plot_peaks(peaks)
    extractor.plot_save_show()
    
    download_youtube_video(yt_video_url)
    extractor.video_info["duration"] = get_video_length("./download/youtube_video.mp4")
    for i, (x,y) in enumerate(peaks):
        x_in_sec = extractor.peaks_to_time(x)
        m, s = divmod(x_in_sec, 60)

        extractor.extract_part(x_in_sec - (duration_peak/2), x_in_sec + (duration_peak/2), str(i)+"_peak_at["+str(int(m))+"_"+str(int(s))+"]")