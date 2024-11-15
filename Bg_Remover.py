import streamlit as st
from rembg import remove
from PIL import Image, UnidentifiedImageError
import io
import time
import numpy as np

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_IMAGE_SIZE = (2000, 2000)  # Maximum dimensions

def remove_background(image):
    # Convert PIL Image to bytes
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    
    # Remove background
    output = remove(
        img_byte_arr,
        alpha_matting=True,
        alpha_matting_foreground_threshold=240,
        alpha_matting_background_threshold=10,
        alpha_matting_erode_size=10
    )
    return Image.open(io.BytesIO(output))

def process_image(image):
    # Check image size
    width, height = image.size
    if width > MAX_IMAGE_SIZE[0] or height > MAX_IMAGE_SIZE[1]:
        aspect_ratio = width / height
        if width > height:
            new_width = MAX_IMAGE_SIZE[0]
            new_height = int(new_width / aspect_ratio)
        else:
            new_height = MAX_IMAGE_SIZE[1]
            new_width = int(new_height * aspect_ratio)
        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    return image

def main():
    st.set_page_config(page_title="Background Remover", layout="wide")
    
    # Custom CSS with visible deploy button
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #1a1a2e 100%);
        }
        div[data-testid="stToolbar"] {
            visibility: visible !important;
        }
        .uploadedFile {
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            padding: 20px;
        }
        .stButton > button {
            background: linear-gradient(90deg, #4a90e2 0%, #67b26f 100%);
            border: none;
            border-radius: 10px;
            color: white;
            transition: all 0.3s ease;
            width: 100%;
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        }
        h1, p {
            color: white !important;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }
        </style>
    """, unsafe_allow_html=True)

    # Title and description
    st.markdown("<h1 style='text-align: center; padding-top: 2rem;'>🎨 Background Remover</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center'>Upload an image to remove its background</p>", unsafe_allow_html=True)

    
    # File uploader
    uploaded_file = st.file_uploader("Choose an image...", type=['png', 'jpg', 'jpeg'], label_visibility="collapsed")

    if uploaded_file is not None:
        file_size = uploaded_file.size
        
        if file_size > MAX_FILE_SIZE:
            st.error("File size is too large! Please upload an image less than 5MB.")
            return
            
        try:
            
            # Load and process image
            image = Image.open(uploaded_file)
            image = process_image(image)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("<p style='text-align: center'>Original Image</p>", unsafe_allow_html=True)
                st.image(image, use_column_width=True)

            # Add format selection for download
            output_format = st.selectbox(
                "Select output format:",
                options=["PNG", "JPEG", "WebP"],
                index=0
            )

            if st.button("Remove Background", use_container_width=True):
                with st.spinner('Processing image...'):
                    # Add progress bar
                    progress_bar = st.progress(0)
                    for i in range(100):
                        time.sleep(0.01)
                        progress_bar.progress(i + 1)
                    
                    try:
                        output_image = remove_background(image)
                        
                        with col2:
                            st.markdown("<p style='text-align: center'>Processed Image</p>", unsafe_allow_html=True)
                            st.image(output_image, use_column_width=True)
                        
                        # Convert to selected format
                        buf = io.BytesIO()
                        save_format = output_format.lower()
                        if save_format == 'jpeg':
                            # Convert to RGB if saving as JPEG
                            output_image = output_image.convert('RGB')
                        
                        output_image.save(buf, format=save_format)
                        byte_im = buf.getvalue()
                        
                        st.download_button(
                            label=f"Download Processed Image as {output_format}",
                            data=byte_im,
                            file_name=f"removed_bg.{save_format}",
                            mime=f"image/{save_format}",
                            use_container_width=True
                        )
                        
                    except Exception as e:
                        st.error(f"Error processing image: {str(e)}")
                    finally:
                        progress_bar.empty()
                        
        except UnidentifiedImageError:
            st.error("Invalid image file. Please upload a valid image.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()