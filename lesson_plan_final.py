import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
from googletrans import Translator
import unicodedata
import re

# --- CONFIGURATION ---
genai.configure(api_key="AIzaSyDhm-4fh5kGXkXfHpBA3YLFe3ciNy8q8NY")  # Replace with your Gemini API Key
model = genai.GenerativeModel("gemini-1.5-flash")

# Translator
translator = Translator()

# --- Streamlit UI ---
st.set_page_config(page_title="Lesson Plan Generator", page_icon="📘")
st.title("📘 AI Lesson Plan Generator")

st.write("Generate detailed and structured lesson plans based on a topic, grade level, and subject.")

# --- Inputs ---
topic = st.text_input("🎯 Enter Topic or Objective (e.g., 'Photosynthesis')")
grade = st.selectbox("🎓 Select Grade Level", ["Kindergarten", "Grade 1", "Grade 2", "Grade 3", "Grade 4",
                                               "Grade 5", "Grade 6", "Grade 7", "Grade 8", "Grade 9", "Grade 10"])
subject = st.selectbox("📘 Select Subject", ["Science", "Mathematics", "English", "History", "Geography", "Computer Science", "Arts"])

language = st.selectbox("🌍 Select Output Language", ["English", "Hindi", "Spanish", "French", "German"])

# --- Cleaning Helpers ---
def clean_text(text):
    """Removes unsupported characters for PDF encoding."""
    return unicodedata.normalize('NFKD', text).encode('latin-1', 'ignore').decode('latin-1')

def clean_markdown(text):
    """Converts markdown symbols to plain text formatting."""
    text = re.sub(r'#+ ', '', text)  # Remove headings like ##, ###
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold
    text = re.sub(r'\*(.*?)\*', r'\1', text)      # Italics
    text = text.replace("* ", "• ")               # Bullet points
    text = text.replace("**", "")                 # Clean any stray asterisks
    return text

# --- Generate Lesson Plan ---
if st.button("Generate Lesson Plan"):
    if topic.strip() == "":
        st.warning("Please enter a topic or objective.")
    else:
        with st.spinner("Generating your lesson plan..."):
            prompt = f"""
            Create a detailed lesson plan for the topic: '{topic}'.
            Subject: {subject}
            Grade Level: {grade}

            Include:
            - Learning Objectives
            - Required Materials
            - Introduction
            - Instructional Activities
            - Assessment Ideas
            - Differentiation Strategies (for advanced and struggling students)
            - Conclusion / Wrap-Up
            """

            response = model.generate_content(prompt)
            lesson_plan = response.text

            # Translate if necessary
            if language != "English":
                lesson_plan = translator.translate(lesson_plan, dest=language.lower()).text

            st.success("Here’s your lesson plan:")
            st.markdown(lesson_plan)

            # Save to PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)

            for line in lesson_plan.split('\n'):
                plain_line = clean_markdown(line)
                safe_line = clean_text(plain_line)
                pdf.multi_cell(0, 10, txt=safe_line)

            pdf_path = "lesson_plan.pdf"
            pdf.output(pdf_path)

            with open(pdf_path, "rb") as file:
                st.download_button(label="📥 Download as PDF", data=file, file_name="lesson_plan.pdf", mime="application/pdf")
