import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import google.generativeai as genai
import re
import io

from io import BytesIO
from docx import Document
from fpdf import FPDF

# --- CONFIGURATION ---
genai.configure(api_key="AIzaSyDhm-4fh5kGXkXfHpBA3YLFe3ciNy8q8NY")
model = genai.GenerativeModel("gemini-1.5-flash")

# --- UTILS ---
def extract_video_id(url):
    regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(regex, url)
    return match.group(1) if match else None

def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join([entry['text'] for entry in transcript])
        return text
    except (TranscriptsDisabled, NoTranscriptFound):
        return None

def generate_guiding_questions(transcript_text, num_questions):
    prompt = (
        f"Given this explanation from a video, generate {num_questions} thoughtful guiding or reflective questions "
        f"that encourage critical thinking about the content:\n\n"
        f"{transcript_text[:10000]}\n\nQuestions:"
    )
    response = model.generate_content(prompt)
    return response.text.strip()

def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in text.split('\n'):
        pdf.multi_cell(0, 10, line)
    pdf_output = BytesIO()
    pdf_bytes = pdf.output(dest='S').encode('latin1')  # IMPORTANT: use latin1 encoding
    pdf_output.write(pdf_bytes)
    pdf_output.seek(0)
    return pdf_output



def create_word(text):
    doc = Document()
    for line in text.split('\n'):
        doc.add_paragraph(line)
    doc_output = BytesIO()
    doc.save(doc_output)
    doc_output.seek(0)
    return doc_output

# --- STREAMLIT UI ---
st.set_page_config(page_title="YouTube Video Guiding Questions", layout="centered")

st.title("🎥 YouTube Video → 🧠 Guiding Questions Generator")

st.markdown(
    """
    Enter a YouTube video URL below, and the app will extract its transcript (if available), 
    then generate guiding questions to help you think critically about the content.
    """
)

video_url = st.text_input("Enter YouTube video URL:")

num_questions = st.slider("How many guiding questions to generate?", min_value=3, max_value=15, value=7, step=1)

if st.button("Generate Guiding Questions"):
    if not video_url:
        st.warning("Please enter a valid YouTube video URL.")
    else:
        with st.spinner("Extracting transcript and generating questions..."):
            video_id = extract_video_id(video_url)
            if not video_id:
                st.error("Invalid YouTube URL.")
            else:
                transcript = get_transcript(video_id)
                if not transcript:
                    st.error("Transcript not available for this video.")
                else:
                    questions = generate_guiding_questions(transcript, num_questions)
                    st.success("Guiding questions generated successfully!")
                    st.markdown("### Here are your guiding questions:")
                    st.write(questions)

                    # Download buttons
                    col1, col2 = st.columns(2)
                    with col1:
                        pdf_file = create_pdf(questions)
                        st.download_button(
                            label="📄 Download as PDF",
                            data=pdf_file,
                            file_name="guiding_questions.pdf",
                            mime="application/pdf"
                        )
                    with col2:
                        word_file = create_word(questions)
                        st.download_button(
                            label="📝 Download as Word",
                            data=word_file,
                            file_name="guiding_questions.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
