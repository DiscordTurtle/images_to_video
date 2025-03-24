import cv2
import numpy as np
import os
import random
from moviepy.editor import VideoFileClip, AudioFileClip

# Parameters
image_folder = "images"
music_folder = "music"
video_folder = "videos"
#calculate final output name as last video name in the folder + 1
final_output = str("video_" + str(len(os.listdir(video_folder)) + 1) + ".mp4")
video_width, video_height = 1080, 1920  # Video resolution
fps = 30
image_duration = 2.5  # Seconds each image is fully visible
transition_duration = 0.5  # Seconds for crossfade transition
#calculate total duration based on the number of images
total_duration = int(len(os.listdir(image_folder)) * image_duration + (len(os.listdir(image_folder)) - 1) * transition_duration)


frames_per_image = int(fps * image_duration)
frames_per_transition = int(fps * transition_duration)
total_frames = int(fps * total_duration)

# Get images
image_files = sorted([os.path.join(image_folder, f) for f in os.listdir(image_folder) if f.endswith(('.jpg', '.png'))])
if len(image_files) < total_duration // image_duration:
    raise ValueError("Not enough images to fill the video duration")

# Get a random music file
music_files = [os.path.join(music_folder, f) for f in os.listdir(music_folder) if f.endswith(('.mp3', '.wav'))]
if not music_files:
    raise ValueError("No audio files found in the music folder")
random_music = random.choice(music_files)

# Prepare video writer
fourcc = cv2.VideoWriter_fourcc(*'XVID')
temp_video = "temp_video.avi"
video = cv2.VideoWriter(temp_video, fourcc, fps, (video_width, video_height))

def resize_and_fit(image, target_width, target_height):
    """ Resize image while keeping aspect ratio and fitting it into the target frame with black borders. """
    h, w = image.shape[:2]
    scale = min(target_width / w, target_height / h)  # Scale to fit while keeping aspect ratio
    new_w, new_h = int(w * scale), int(h * scale)
    
    resized = cv2.resize(image, (new_w, new_h))  # Resize while keeping aspect ratio
    
    # Create a black canvas
    fitted_image = np.zeros((target_height, target_width, 3), dtype=np.uint8)
    
    # Compute top-left position to center the image
    x_offset = (target_width - new_w) // 2
    y_offset = (target_height - new_h) // 2
    
    # Paste the resized image onto the black canvas
    fitted_image[y_offset:y_offset + new_h, x_offset:x_offset + new_w] = resized
    
    return fitted_image

# Process images with transitions
for i in range(len(image_files) - 1):
    img1 = cv2.imread(image_files[i])
    img2 = cv2.imread(image_files[i + 1])

    img1 = resize_and_fit(img1, video_width, video_height)
    img2 = resize_and_fit(img2, video_width, video_height)

    # Show img1 for the set duration
    for _ in range(frames_per_image):
        video.write(img1)

    # Transition (crossfade from img1 to img2)
    for t in range(frames_per_transition):
        alpha = t / frames_per_transition
        blended = cv2.addWeighted(img1, 1 - alpha, img2, alpha, 0)
        video.write(blended)

# Show the last image fully for its duration
for _ in range(frames_per_image):
    video.write(img2)

# Cleanup
video.release()
cv2.destroyAllWindows()

# Add music to video
video_clip = VideoFileClip(temp_video)
audio_clip = AudioFileClip(random_music).subclip(0, total_duration)
final_clip = video_clip.set_audio(audio_clip)


final_clip.write_videofile(video_folder + '/' + final_output, codec='libx264', audio_codec='aac')

# Remove temporary video
os.remove(temp_video)

print(f"Final video with music saved as {final_output}")
