import streamlit as st
from rembg import remove
from PIL import Image
import io
import time

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
        # Display original image
        image = Image.open(uploaded_file)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<p style='text-align: center'>Original Image</p>", unsafe_allow_html=True)
            st.image(image, use_column_width=True)

        # Process button
        if st.button("Remove Background", use_container_width=True):
            with st.spinner('Processing image...'):
                # Add slight delay for better UX
                time.sleep(0.5)
                
                # Remove background
                output_image = remove_background(image)
                
                # Display result
                with col2:
                    st.markdown("<p style='text-align: center'>Processed Image</p>", unsafe_allow_html=True)
                    st.image(output_image, use_column_width=True)
                
                # Convert to bytes for download
                buf = io.BytesIO()
                output_image.save(buf, format='PNG')
                byte_im = buf.getvalue()
                
                # Download button
                st.download_button(
                    label="Download Processed Image",
                    data=byte_im,
                    file_name="removed_bg.png",
                    mime="image/png",
                    use_container_width=True
                )

if __name__ == "__main__":
    main()