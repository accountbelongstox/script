from moviepy.editor import VideoFileClip
import os
import datetime
import sys

def write_audio(filename, output_dir="out/audio"):
    video = VideoFileClip(filename)

    audio = video.audio

    current_time = datetime.datetime.now()
    timestamp = current_time.strftime("%Y-%m-%d_%H-%M-%S")

    output_path = os.path.join(output_dir, timestamp)
    os.makedirs(output_path, exist_ok=True)

    wav_filename = f"{timestamp}.wav"
    mp3_filename = f"{timestamp}.mp3"

    audio.write_audiofile(os.path.join(output_path, wav_filename))
    audio.write_audiofile(os.path.join(output_path, mp3_filename), codec='mp3')  

if __name__ == "__main__":
    if len(sys.argv) > 1:
        video_file = sys.argv[1]
    else:
        video_file = "./video/meeting_02.mp4"
    write_audio(video_file)
