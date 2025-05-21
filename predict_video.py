import argparse
import queue
import pandas as pd 
import pickle
import imutils
import os
import requests # Added for downloading YOLO weights
from PIL import Image, ImageDraw
import cv2
import numpy as np
import torch
import sys
import time

from sktime.datatypes._panel._convert import from_2d_array_to_nested
from court_detector import CourtDetector
from Models.tracknet import trackNet
from TrackPlayers.trackplayers import *
from utils import get_video_properties, get_dtype
from detection import *
from pickle import load


# Global variables / model paths
n_classes = 256
save_weights_path = 'WeightsTracknet/model.1'
yolo_classes = 'Yolov3/yolov3.txt' # This will be replaced by YOLO_CLASSES_PATH
# yolo_weights = 'Yolov3/yolov3.weights' # This will be replaced by YOLO_WEIGHTS_PATH
# yolo_config = 'Yolov3/yolov3.cfg' # This will be replaced by YOLO_CONFIG_PATH

# Define YOLO constants
YOLO_DIR = "Yolov3"
YOLO_WEIGHTS_PATH = os.path.join(YOLO_DIR, "yolov3.weights")
YOLO_CONFIG_PATH = os.path.join(YOLO_DIR, "yolov3.cfg")
YOLO_CLASSES_PATH = os.path.join(YOLO_DIR, "yolov3.txt")
YOLO_WEIGHTS_URL = "https://pjreddie.com/media/files/yolov3.weights"

def download_yolo_weights():
    if not os.path.exists(YOLO_WEIGHTS_PATH):
        print(f"{YOLO_WEIGHTS_PATH} not found. Downloading from {YOLO_WEIGHTS_URL}...")
        os.makedirs(YOLO_DIR, exist_ok=True)
        try:
            response = requests.get(YOLO_WEIGHTS_URL, stream=True)
            response.raise_for_status() # Raise an exception for bad status codes
            with open(YOLO_WEIGHTS_PATH, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print("Download complete.")
        except requests.exceptions.RequestException as e:
            print(f"Error downloading YOLO weights: {e}")
            # Optionally, re-raise the error or handle it as critical
            raise
    else:
        print(f"{YOLO_WEIGHTS_PATH} found.")

def process_video_core(input_video_path, output_video_path, minimap_option, bounce_option):
    # Download YOLO weights if not present
    download_yolo_weights()

    # Ensure VideoOutput directory exists
    os.makedirs(os.path.dirname(output_video_path), exist_ok=True)

    # get video fps&video size
    video = cv2.VideoCapture(input_video_path)
    fps = int(video.get(cv2.CAP_PROP_FPS))
    print('fps : {}'.format(fps))
    output_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    output_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # try to determine the total number of frames in the video file
    if imutils.is_cv2() is True :
        prop = cv2.cv.CV_CAP_PROP_FRAME_COUNT
    else : 
        prop = cv2.CAP_PROP_FRAME_COUNT
    total = int(video.get(prop))

    # start from first frame
    currentFrame = 0

    # width and height in TrackNet
    width, height = 640, 360
    img, img1, img2 = None, None, None

    # load TrackNet model
    modelFN = trackNet
    m = modelFN(n_classes, input_height=height, input_width=width)
    m.compile(loss='categorical_crossentropy', optimizer='adadelta', metrics=['accuracy'])
    m.load_weights(save_weights_path)

    # In order to draw the trajectory of tennis, we need to save the coordinate of previous 7 frames
    q = queue.deque()
    for i in range(0, 8):
        q.appendleft(None)

    # save prediction images as videos
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    # Use the output_video_path argument for the main output
    processed_video_writer = cv2.VideoWriter(output_video_path, fourcc, fps, (output_width, output_height))


    # load yolov3 labels
    if not os.path.exists(YOLO_CLASSES_PATH):
        print(f"Error: YOLO classes file not found at {YOLO_CLASSES_PATH}")
        raise FileNotFoundError(f"YOLO classes file not found at {YOLO_CLASSES_PATH}")
    LABELS = open(YOLO_CLASSES_PATH).read().strip().split("\n")
    
    # yolo net
    if not os.path.exists(YOLO_CONFIG_PATH):
        print(f"Error: YOLO config file not found at {YOLO_CONFIG_PATH}")
        raise FileNotFoundError(f"YOLO config file not found at {YOLO_CONFIG_PATH}")
    net = cv2.dnn.readNet(YOLO_WEIGHTS_PATH, YOLO_CONFIG_PATH)

    # court
    court_detector = CourtDetector()

    # players tracker
    dtype = get_dtype()
    detection_model = DetectionModel(dtype=dtype)

    # get videos properties
    # fps, length, v_width, v_height = get_video_properties(video) # fps is already obtained, length is total
    v_width, v_height = output_width, output_height # Use the video's original width and height

    coords = []
    frame_i = 0
    frames_list = [] # Renamed from frames to avoid conflict
    t = []

    while True:
      ret, frame_data = video.read() # Renamed frame to frame_data
      frame_i += 1

      if ret:
        if frame_i == 1:
          print('Detecting the court and the players...')
          lines = court_detector.detect(frame_data)
        else: # then track it
          lines = court_detector.track_court(frame_data)
        detection_model.detect_player_1(frame_data, court_detector)
        detection_model.detect_top_persons(frame_data, court_detector, frame_i)
        
        for i in range(0, len(lines), 4):
          x1, y1, x2, y2 = lines[i],lines[i+1], lines[i+2], lines[i+3]
          cv2.line(frame_data, (int(x1),int(y1)),(int(x2),int(y2)), (0,0,255), 5)
        new_frame = cv2.resize(frame_data, (v_width, v_height))
        frames_list.append(new_frame)
      else:
        break
    video.release() # Release after reading all frames
    print('Finished court and player detection!')

    detection_model.find_player_2_box()

    # second part 
    player1_boxes = detection_model.player_1_boxes
    player2_boxes = detection_model.player_2_boxes

    # Re-initialize video capture for ball tracking pass if necessary, or use frames_list
    # Using frames_list directly is more efficient
    currentFrame = 0 # Reset for processing frames_list

    last = time.time() # start counting 
    for frame_data in frames_list: # Iterate over the collected frames
        print('Tracking the ball: {}%'.format(round( (currentFrame / total) * 100, 2) if total > 0 else 0))
        
        output_img = frame_data.copy() # Work on a copy for drawing

        # resize it for TrackNet
        img_resized_for_tracknet = cv2.resize(frame_data, (width, height))
        # input must be float type
        img_resized_for_tracknet = img_resized_for_tracknet.astype(np.float32)

        # since the odering of TrackNet  is 'channels_first', so we need to change the axis
        X = np.rollaxis(img_resized_for_tracknet, 2, 0)
        # prdict heatmap
        pr = m.predict(np.array([X]))[0]

        # since TrackNet output is ( net_output_height*model_output_width , n_classes )
        # so we need to reshape image as ( net_output_height, model_output_width , n_classes(depth) )
        pr = pr.reshape((height, width, n_classes)).argmax(axis=2)

        # cv2 image must be numpy.uint8, convert numpy.int64 to numpy.uint8
        pr = pr.astype(np.uint8)

        # reshape the image size as original input image
        heatmap = cv2.resize(pr, (output_width, output_height))

        # heatmap is converted into a binary image by threshold method.
        ret, heatmap = cv2.threshold(heatmap, 127, 255, cv2.THRESH_BINARY)

        # find the circle in image with 2<=radius<=7
        circles = cv2.HoughCircles(heatmap, cv2.HOUGH_GRADIENT, dp=1, minDist=1, param1=50, param2=2, minRadius=2,
                                  maxRadius=7)

        output_img = mark_player_box(output_img, player1_boxes, currentFrame) # Use currentFrame index
        output_img = mark_player_box(output_img, player2_boxes, currentFrame) # Use currentFrame index
        
        PIL_image = cv2.cvtColor(output_img, cv2.COLOR_BGR2RGB)
        PIL_image = Image.fromarray(PIL_image)

        # check if there have any tennis be detected
        if circles is not None:
            if len(circles) == 1:
                x = int(circles[0][0][0])
                y = int(circles[0][0][1])
                coords.append([x,y])
                t.append(time.time()-last)
                q.appendleft([x, y])
                q.pop()
            else:
                coords.append(None)
                t.append(time.time()-last)
                q.appendleft(None)
                q.pop()
        else:
            coords.append(None)
            t.append(time.time()-last)
            q.appendleft(None)
            q.pop()

        for i in range(0, 8):
            if q[i] is not None:
                draw_x = q[i][0]
                draw_y = q[i][1]
                bbox = (draw_x - 2, draw_y - 2, draw_x + 2, draw_y + 2)
                draw = ImageDraw.Draw(PIL_image)
                draw.ellipse(bbox, outline='yellow')
                del draw

        opencvImage = cv2.cvtColor(np.array(PIL_image), cv2.COLOR_RGB2BGR)
        processed_video_writer.write(opencvImage)
        currentFrame += 1

    processed_video_writer.release() # Release the main video writer

    # Path for the video after ball tracking (before minimap/bounce)
    ball_tracked_video_path = output_video_path
    final_output_path = output_video_path # This will be updated if minimap or bounce is applied

    if minimap_option:
      game_video = cv2.VideoCapture(ball_tracked_video_path) # Use the output from previous step
      fps1 = int(game_video.get(cv2.CAP_PROP_FPS))
      output_width_map = int(game_video.get(cv2.CAP_PROP_FRAME_WIDTH))
      output_height_map = int(game_video.get(cv2.CAP_PROP_FRAME_HEIGHT))
      
      # Define path for video with minimap
      video_with_map_path = os.path.join(os.path.dirname(output_video_path), "video_with_map.mp4")
      minimap_video_writer = cv2.VideoWriter(video_with_map_path, fourcc, fps1, (output_width_map, output_height_map))
      
      print('Adding the mini-map...')
      # Remove Outliers 
      x_coords, y_coords = diff_xy(coords) # Renamed x,y to x_coords, y_coords
      remove_outliers(x_coords, y_coords, coords)
      # Interpolation
      coords = interpolation(coords)
      # Ensure fps is passed correctly, it was defined at the start of the function
      create_top_view(court_detector, detection_model, coords, fps) 
      
      minimap_frames_path = 'VideoOutput/minimap.mp4' # This is where create_top_view saves its output
      if not os.path.exists(minimap_frames_path):
          print(f"Error: Minimap base video not found at {minimap_frames_path}")
          # Handle error: maybe return or skip minimap
      else:
          minimap_video_capture = cv2.VideoCapture(minimap_frames_path)
          fps2 = int(minimap_video_capture.get(cv2.CAP_PROP_FPS))
          print('minimap fps: {}'.format(fps2))
          
          while True:
            ret_game, frame_game = game_video.read()
            ret_map, frame_map = minimap_video_capture.read()
            if ret_game:
              if ret_map:
                output = merge(frame_game, frame_map)
                minimap_video_writer.write(output)
              else: # If minimap video ends, write remaining game frames
                minimap_video_writer.write(frame_game)
            else:
              break
          game_video.release()
          minimap_video_capture.release()
          minimap_video_writer.release()
          final_output_path = video_with_map_path # Update final output path
          print(f"Minimap video saved to {video_with_map_path}")


    # Post-processing (outlier removal, interpolation) - applied on original coords
    for _ in range(3):
      x_coords, y_coords = diff_xy(coords)
      remove_outliers(x_coords, y_coords, coords)
    coords = interpolation(coords)

    # Velocity calculation
    Vx = []
    Vy = []
    V = []
    # frames_indices = [*range(len(coords))] # Renamed from frames

    for i in range(len(coords)-1):
      p1 = coords[i]
      p2 = coords[i+1]
      if p1 is None or p2 is None or t[i] is None or t[i+1] is None or t[i] == t[i+1]: # Check for None and division by zero
          Vx.append(0) # Or some other placeholder
          Vy.append(0)
          continue
      x_vel = (p1[0]-p2[0])/(t[i]-t[i+1]) # Corrected time difference
      y_vel = (p1[1]-p2[1])/(t[i]-t[i+1]) # Corrected time difference
      Vx.append(x_vel)
      Vy.append(y_vel)

    for i in range(len(Vx)):
      vx = Vx[i]
      vy = Vy[i]
      v_mag = (vx**2+vy**2)**0.5
      V.append(v_mag)

    xy = coords[:] # Make a copy

    if bounce_option:
      if not V: # Check if V is empty
          print("Velocity list is empty, skipping bounce detection.")
      else:
          print('Predicting bounces...')
          # Predicting Bounces 
          # Ensure coords[:-1] and V have compatible lengths
          min_len = min(len(xy)-1, len(V))
          test_df = pd.DataFrame({'x': [c[0] for c in xy[:min_len]], 
                                  'y':[c[1] for c in xy[:min_len]], 
                                  'V': V[:min_len]})

          for i in range(20, 0, -1): 
            test_df[f'lagX_{i}'] = test_df['x'].shift(i, fill_value=0)
          for i in range(20, 0, -1): 
            test_df[f'lagY_{i}'] = test_df['y'].shift(i, fill_value=0)
          for i in range(20, 0, -1): 
            test_df[f'lagV_{i}'] = test_df['V'].shift(i, fill_value=0)

          test_df.drop(['x', 'y', 'V'], axis=1, inplace=True) # Use axis=1 for columns

          Xs = test_df[['lagX_20', 'lagX_19', 'lagX_18', 'lagX_17', 'lagX_16',
                'lagX_15', 'lagX_14', 'lagX_13', 'lagX_12', 'lagX_11', 'lagX_10',
                'lagX_9', 'lagX_8', 'lagX_7', 'lagX_6', 'lagX_5', 'lagX_4', 'lagX_3',
                'lagX_2', 'lagX_1']]
          Xs = from_2d_array_to_nested(Xs.to_numpy())

          Ys = test_df[['lagY_20', 'lagY_19', 'lagY_18', 'lagY_17',
                'lagY_16', 'lagY_15', 'lagY_14', 'lagY_13', 'lagY_12', 'lagY_11',
                'lagY_10', 'lagY_9', 'lagY_8', 'lagY_7', 'lagY_6', 'lagY_5', 'lagY_4',
                'lagY_3', 'lagY_2', 'lagY_1']]
          Ys = from_2d_array_to_nested(Ys.to_numpy())

          Vs = test_df[['lagV_20', 'lagV_19', 'lagV_18',
                'lagV_17', 'lagV_16', 'lagV_15', 'lagV_14', 'lagV_13', 'lagV_12',
                'lagV_11', 'lagV_10', 'lagV_9', 'lagV_8', 'lagV_7', 'lagV_6', 'lagV_5',
                'lagV_4', 'lagV_3', 'lagV_2', 'lagV_1']]
          Vs = from_2d_array_to_nested(Vs.to_numpy())

          X_bounce_features = pd.concat([Xs, Ys, Vs], axis=1) # Use axis=1 for columns

          clf = load(open('clf.pkl', 'rb'))
          predicted_bounces = clf.predict(X_bounce_features)
          bounce_indices = list(np.where(predicted_bounces == 1)[0])
          bounce_indices = np.array(bounce_indices) - 10 # Adjust indices
          
          # Determine the source video for bounce marking
          bounce_input_video_path = final_output_path # This is either original_output_video_path or video_with_map_path
          video_for_bounce = cv2.VideoCapture(bounce_input_video_path)
          
          fps_bounce = int(video_for_bounce.get(cv2.CAP_PROP_FPS))
          output_width_bounce = int(video_for_bounce.get(cv2.CAP_PROP_FRAME_WIDTH))
          output_height_bounce = int(video_for_bounce.get(cv2.CAP_PROP_FRAME_HEIGHT))
          
          # Define path for final video with bounces
          final_video_with_bounces_path = os.path.join(os.path.dirname(output_video_path), "final_video_with_bounces.mp4")
          bounce_video_writer = cv2.VideoWriter(final_video_with_bounces_path, fourcc, fps_bounce, (output_width_bounce, output_height_bounce))
          
          frame_idx = 0
          while True:
            ret_bounce, frame_bounce = video_for_bounce.read()
            if ret_bounce:
              if frame_idx in bounce_indices:
                # Ensure xy has this index and it's not None
                if frame_idx < len(xy) and xy[frame_idx] is not None:
                    center_coordinates = int(xy[frame_idx][0]), int(xy[frame_idx][1])
                    radius = 10 # Increased radius for visibility
                    color = (0, 0, 255) # Red color for bounce
                    thickness = -1 # Filled circle
                    cv2.circle(frame_bounce, center_coordinates, radius, color, thickness)
              bounce_video_writer.write(frame_bounce)
              frame_idx += 1
            else:
              break
          video_for_bounce.release()
          bounce_video_writer.release()
          final_output_path = final_video_with_bounces_path # Update final output path
          print(f"Bounce video saved to {final_video_with_bounces_path}")

    return final_output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_video_path", type=str, required=True)
    parser.add_argument("--output_video_path", type=str, default="")
    parser.add_argument("--minimap", type=int, default=0) 
    parser.add_argument("--bounce", type=int, default=0)

    args = parser.parse_args()

    final_output_video_path = args.output_video_path
    # Create default output path if not provided
    if final_output_video_path == "":
        # Ensure VideoOutput directory exists
        os.makedirs("VideoOutput", exist_ok=True) 
        base_name = os.path.basename(args.input_video_path)
        name_part = base_name.split('.')[0]
        final_output_video_path = os.path.join("VideoOutput", f"{name_part}_processed.mp4")
    
    # Ensure the directory for the output video exists
    os.makedirs(os.path.dirname(final_output_video_path), exist_ok=True)

    # Call the main processing function
    result_path = process_video_core(args.input_video_path, final_output_video_path, bool(args.minimap), bool(args.bounce))
    print(f"Processing complete. Output video saved to: {result_path}")
