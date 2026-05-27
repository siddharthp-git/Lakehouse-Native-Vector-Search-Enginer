import streamlit as st
import requests
import pandas as pd

# API endpoint
API_URL = "http://backend:5001"

st.set_page_config(layout="wide")
st.title("🌊 Lakehouse-Native Vector Search Engine")

st.sidebar.header("Controls")

# --- Search Modes ---
search_mode = st.sidebar.radio("Select Search Mode", ("Vector Search", "Hybrid Search", "Audio Transcription"))

# --- Vector Search ---
if search_mode == "Vector Search":
    st.header("Vector Search")
    st.write("Search for similar text using vector embeddings.")
    query = st.text_input("Enter your search query:", key="vector_query")
    if st.button("Search", key="vector_search_btn"):
        if query:
            response = requests.get(f"{API_URL}/search", params={"q": query})
            if response.status_code == 200:
                results = response.json()
                st.write(f"Found {len(results)} results:")
                st.dataframe(pd.DataFrame(results))
            else:
                st.error(f"Error: {response.json().get('error')}")
        else:
            st.warning("Please enter a query.")

# --- Hybrid Search ---
elif search_mode == "Hybrid Search":
    st.header("Hybrid Search")
    st.write("Combine vector search with metadata filtering.")
    query = st.text_input("Enter your search query:", key="hybrid_query")
    category = st.selectbox("Filter by Category:", ["science", "finance", "art"], key="category_filter")
    
    if st.button("Search", key="hybrid_search_btn"):
        if query:
            params = {"q": query, "category": category}
            response = requests.get(f"{API_URL}/hybrid-search", params=params)
            if response.status_code == 200:
                results = response.json()
                st.write(f"Found {len(results)} results:")
                st.dataframe(pd.DataFrame(results))
            else:
                st.error(f"Error: {response.json().get('error')}")
        else:
            st.warning("Please enter a query.")

# --- Audio Transcription ---
elif search_mode == "Audio Transcription":
    st.header("Audio Transcription")
    st.write("Upload an audio file to transcribe it using Whisper. The text can then be used for searching.")
    
    uploaded_file = st.file_uploader("Choose an audio file...", type=["wav", "mp3", "m4a"])
    
    if uploaded_file is not None:
        st.audio(uploaded_file, format='audio/wav')
        if st.button("Transcribe Audio", key="transcribe_btn"):
            files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            with st.spinner('Transcribing... this may take a moment.'):
                response = requests.post(f"{API_URL}/transcribe", files=files)
            
            if response.status_code == 200:
                transcript = response.json().get('transcript')
                st.success("Transcription complete!")
                st.text_area("Transcript:", transcript, height=200)
            else:
                st.error(f"Error: {response.json().get('error')}")