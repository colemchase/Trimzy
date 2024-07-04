from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options as ChromeOptions
import yt_dlp
import matplotlib.pyplot as plt
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from bs4 import BeautifulSoup

class Extractor(object):

    def __init__(self, url) -> None:
        self.video_url = url
        self.video_info = {}
        self.configure_webdriver()
        
    def configure_webdriver(self):
        chrome_options = ChromeOptions()
        # Add any Chrome options here if needed
        # chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.get(self.video_url)

    def refuse_condition(self):
        # Implement your condition handling for Chrome if needed
        pass

    def get_svg(self):
        heatmap_chapter = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "ytp-heat-map-chapter")))
        svg_html = heatmap_chapter.get_attribute('innerHTML')
        self.driver.quit()
        return svg_html
    
    def list_available_formats(self):
        ydl_opts = {'quiet': True}
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.video_url, download=False)
                formats = info.get('formats', [])
                for fmt in formats:
                    print(f"Format ID: {fmt['format_id']}, Resolution: {fmt.get('height')}, Extension: {fmt['ext']}")
        except yt_dlp.utils.DownloadError as e:
            print(f'Failed to fetch formats. Reason: {e}')

    def download_video(self, resolution=137):
        print("Launching video downloading...")
        ydl_opts = {
            'format': f"b[height={resolution}][ext=mp4]",
            'quiet': True,
            "nopart": True,
            'outtmpl': "./download/youtube_video.%(ext)s"
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.video_info = ydl.extract_info(self.video_url)
        except yt_dlp.utils.DownloadError:
            print('Interrupt the download')
            return False
        return True

    
    def extract_points_from_svg(self, svg):
        print("Launching extraction points from SVG...")
        soup = BeautifulSoup(svg, features="html.parser")
        path = soup.find("path")
        d = path.get("d")
        coordinates = d.replace("M ", "").replace("C ", "").split(" ")
        points = []
        for c in coordinates[1:]:  # Ignore first
            tab = c.split(",")
            x_coordinate = float(tab[0])
            y_coordinate = float(tab[1])
            points.append((x_coordinate, y_coordinate))
        
        x_coords, y_coords = zip(*points)
        y_coords = [90.0 - y for y in y_coords]  # Inverse graph
        y_coords = [y if y >= 0.0 else 0.0 for y in y_coords]  # Correct graph
        
        new_points = list(zip(x_coords, y_coords))[9:]
        print("Extracted points:", len(new_points))
        return new_points

    def plot_svg(self, points, threshold=80.0):
        x_coords, y_coords = zip(*points)
        plt.plot(x_coords, y_coords, marker="+")
        plt.axhline(y=threshold, color='r', linestyle='--')
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.title('SVG Curve')

    def plot_peaks(self, peaks):
        for peak in peaks:
            plt.scatter(peak[0], peak[1], marker="o")
        
    def plot_save_show(self):
        plt.savefig("./peaks/plot_svg_peaks.jpg")    
        # plt.show()
        
    def find_peaks(self, points, threshold=80.0):
        print("thresholds", threshold)
        peaks = []
        for i in range(1, len(points)-1):
            prev_y = points[i-1][1]
            curr_y = points[i][1]
            next_y = points[i+1][1]
            if curr_y > prev_y and curr_y > next_y and curr_y >= threshold:
                peaks.append(points[i])
        if len(peaks) == 0:
            return self.find_peaks(points, threshold-10)
        return peaks
    
    def peaks_to_time(self, x):
        return (x * self.video_info["duration"]) / 1000
    
    def extract_part(self, start_time, end_time, name):
        ffmpeg_extract_subclip("./download/youtube_video.mp4", start_time, end_time, targetname="peaks/"+name+".mp4")
