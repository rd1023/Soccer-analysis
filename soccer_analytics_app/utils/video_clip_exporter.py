from moviepy.video.io.VideoFileClip import VideoFileClip
import os

def export_clip(video_path, start_time, end_time, output_path):
    with VideoFileClip(video_path) as video:
        clip = video.subclip(start_time, end_time)
        clip.write_videofile(output_path, codec="libx264")
