import streamlit as st
import cv2
import numpy as np
from PIL import Image
from streamlit_drawable_canvas import st_canvas
import io

# --- CONFIGURATION DU SITE ---
st.set_page_config(
    page_title="Magic Eraser - Nettoyeur d'Image",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STYLE CSS (Pour ressembler à la maquette Canva) ---
st.markdown("""
<style>
    .main {
        background-color: #f4f6f8;
    }
    h1 {
        color: #2c3e50;
        text-align: center;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        width: 100%;
        border-radius: 10px;
        height: 50px;
        font-weight: bold;
    }
    .stDownloadButton>button {
        background-color: #008CBA;
        color: white;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.title("✨ Effaceur Magique")
st.markdown("### Supprimez les éléments indésirables de vos photos en quelques secondes.")
st.markdown("---")

# --- SIDEBAR (Barre latérale) ---
with st.sidebar:
    st.header("🛠️ Outils")
    st.info("1. Chargez une image.\n2. Dessinez sur l'élément à effacer.\n3. L'IA fait le reste !")
    
    stroke_width = st.slider("Taille du pinceau", 5, 50, 20)
    
    st.write("---")
    st.caption("Propulsé par Python & OpenCV")

# --- CORPS DE L'APPLICATION ---
uploaded_file = st.file_uploader("📂 Glissez-déposez votre image ici (JPG, PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    # Redimensionner pour l'affichage si l'image est trop grande (pour éviter de casser le site)
    max_width = 800
    if image.width > max_width:
        ratio = max_width / image.width
        new_height = int(image.height * ratio)
        image = image.resize((max_width, new_height))

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.subheader("1. Dessinez la zone à effacer")
        # Le Canvas
        canvas_result = st_canvas(
            fill_color="rgba(255, 0, 0, 0.3)",
            stroke_width=stroke_width,
            stroke_color="#ff0000", # Pinceau rouge comme sur la maquette
            background_image=image,
            update_streamlit=True,
            height=image.height,
            width=image.width,
            drawing_mode="freedraw",
            key="canvas",
        )

    with col2:
        st.subheader("2. Résultat")
        
        # Logique de traitement
        if canvas_result.image_data is not None:
            mask_data = canvas_result.image_data
            mask = mask_data[:, :, 3] # Canal Alpha

            if np.sum(mask) > 0:
                with st.spinner('L\'IA nettoie votre image...'):
                    # Conversion pour OpenCV
                    img_cv = np.array(image.convert('RGB'))
                    # Nettoyage du masque
                    _, mask = cv2.threshold(mask, 10, 255, cv2.THRESH_BINARY)
                    
                    # Inpainting
                    res = cv2.inpaint(img_cv, mask, 3, cv2.INPAINT_TELEA)
                    
                    # Affichage du résultat
                    st.image(res, caption="Image Nettoyée", use_container_width=True)
                    
                    # Bouton Télécharger
                    result_pil = Image.fromarray(res)
                    buf = io.BytesIO()
                    result_pil.save(buf, format="PNG")
                    byte_im = buf.getvalue()
                    
                    st.download_button(
                        label="⬇️ Télécharger le résultat",
                        data=byte_im,
                        file_name="image_propre.png",
                        mime="image/png"
                    )
            else:
                st.info("Utilisez le pinceau à gauche pour commencer.")
else:
    # État vide (quand aucune image n'est chargée)
    st.markdown("""
    <div style='text-align: center; padding: 50px; color: #888;'>
        Waiting for upload...
    </div>
    """, unsafe_allow_html=True)