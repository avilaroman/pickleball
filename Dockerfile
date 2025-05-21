# 1. Base Image
FROM python:3.9-slim

# 2. Set working directory
WORKDIR /app

# 3. Environment variables
ENV PYTHONUNBUFFERED=1
ENV GRADIO_SERVER_NAME="0.0.0.0"
# GRADIO_SERVER_PORT will be used as a fallback in app.py if PORT is not set
ENV GRADIO_SERVER_PORT="7860"

# 4. Install system dependencies for OpenCV and other tools like ffmpeg
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 5. Install Python dependencies
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy application files
# Note: .dockerignore should be used to exclude unnecessary files/dirs
COPY app.py ./app.py
COPY predict_video.py ./predict_video.py
COPY court_detector.py ./court_detector.py
COPY utils.py ./utils.py
COPY detection.py ./detection.py # Assuming this is a required file
COPY clf.pkl ./clf.pkl

COPY Models/ ./Models/
COPY WeightsTracknet/ ./WeightsTracknet/
COPY Yolov3/yolov3.cfg ./Yolov3/yolov3.cfg
COPY Yolov3/yolov3.txt ./Yolov3/yolov3.txt
COPY court_configurations/ ./court_configurations/
COPY TrackPlayers/ ./TrackPlayers/ # Assuming this directory and its contents are needed

# 7. Create Necessary Directories (if not copied or created by app)
# app.py already creates VideoOutput. VideoInput is for user uploads, so not needed in image.
# RUN mkdir -p /app/VideoOutput /app/VideoInput

# 8. Expose port (the actual port binding happens during `docker run -p`)
# app.py will use PORT environment variable if set, otherwise GRADIO_SERVER_PORT
EXPOSE 7860

# 9. CMD
CMD ["python", "app.py"]
