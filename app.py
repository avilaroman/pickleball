import gradio as gr
import os
import uuid # For unique filenames
from predict_video import process_video_core, download_yolo_weights # download_yolo_weights is called in process_video_core

# Ensure necessary directories exist
os.makedirs("VideoInput", exist_ok=True)
os.makedirs("VideoOutput", exist_ok=True) # Already created for dummy, but good to ensure

# Remove dummy video creation if it exists, as we are now processing real videos
dummy_video_path = "VideoOutput/dummy_output.mp4"
if os.path.exists(dummy_video_path):
    try:
        os.remove(dummy_video_path)
        print(f"Removed dummy video: {dummy_video_path}")
    except OSError as e:
        print(f"Error removing dummy video {dummy_video_path}: {e.strerror}")


def process_video_interface(uploaded_video_file, minimap_option, bounce_option):
    if uploaded_video_file is None:
        print("No video uploaded.")
        # Optionally, return a message to Gradio UI, e.g., using gr.Info() or by raising gr.Error
        # For now, returning None will clear the video output
        return None 

    input_video_path = uploaded_video_file.name # Path to the uploaded temp file

    # Create a unique output filename to prevent overwrites
    unique_id = uuid.uuid4()
    output_filename = f"{unique_id}_processed.mp4"
    # The process_video_core function will create subdirectories if needed,
    # so we give it the base output path.
    output_video_path = os.path.join("VideoOutput", output_filename)

    print(f"Input video: {input_video_path}")
    print(f"Target base output video: {output_video_path}")
    print(f"Minimap: {minimap_option}, Bounce: {bounce_option}")

    try:
        # download_yolo_weights() # Called within process_video_core, no need to call here explicitly unless for early check
        
        # Call the actual processing function
        processed_video_returned_path = process_video_core(
            input_video_path, 
            output_video_path, # This will be the initial output path, may be changed by minimap/bounce
            minimap_option, 
            bounce_option
        )
        
        if processed_video_returned_path and os.path.exists(processed_video_returned_path):
            print(f"Processing successful. Final output at: {processed_video_returned_path}")
            return processed_video_returned_path
        else:
            print(f"Processing failed or output video not found. Expected at {processed_video_returned_path}")
            # raise gr.Error("Processing failed or output video not found.") # Requires Gradio 3.9+
            return None
            
    except Exception as e:
        print(f"An error occurred during video processing: {e}")
        # raise gr.Error(f"Processing Error: {str(e)}") # Requires Gradio 3.9+
        return None


iface = gr.Interface(
    fn=process_video_interface,
    inputs=[
        gr.File(label="Upload Video", file_types=["mp4"]),
        gr.Checkbox(label="Enable Minimap", value=False),
        gr.Checkbox(label="Enable Bounce Detection", value=False)
    ],
    outputs=gr.Video(label="Processed Video"),
    title="Pikleball Tracker",
    description="Upload a video to track pickleball game, detect players, and bounces."
)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 7860))
    iface.launch(server_name="0.0.0.0", server_port=port, share=False)
