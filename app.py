import streamlit as st
from google import genai
from openai import OpenAI
from datetime import datetime


# app setup
st.set_page_config(
    page_title="Persona Multiplier AI",
    layout="wide"
)

openai_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
gemini_client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])


# page styling
st.markdown(
    """
    <style>
    /* global font */

html,
body,
[class*="css"],
[data-testid="stAppViewContainer"],
[data-testid="stMarkdownContainer"],
[data-testid="stText"],
[data-testid="stCode"],
textarea,
input,
button,
select,
p,
span,
div,
label {
    font-family: "Times New Roman", Times, serif !important;
}
    html, body, [class*="css"] {
        font-family: "Times New Roman", Times, serif !important;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: "Times New Roman", Times, serif !important;
    }

    .stApp {
        background: linear-gradient(
            -45deg,
            #FDF2F4,
            #F3E5F5,
            #F8E7F7,
            #E8F5E9,
            #4A3E4D
        );
        background-size: 400% 400%;
        animation: gradientMove 18s ease infinite;
    }

    @keyframes gradientMove {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .stTextArea label p,
    .stSelectbox label p {
        font-weight: 700 !important;
        font-size: 18px !important;
        color: #4A3E4D !important;
    }

    .stTextArea textarea {
        background: rgba(255,255,255,0.65) !important;
        border-radius: 16px !important;
        border: 1px solid rgba(255,255,255,0.4) !important;
        padding: 16px !important;
        color: #3D3340 !important;
        font-size: 15px !important;
    }

    .stSelectbox [data-baseweb="select"] > div {
        background: linear-gradient(
            -45deg,
            #FDF2F4,
            #F3E5F5,
            #F8E7F7,
            #E8F5E9
        ) !important;
        background-size: 300% 300% !important;
        animation: dropdownGradient 8s ease infinite !important;
        border-radius: 14px !important;
        border: 1px solid rgba(74, 62, 77, 0.25) !important;
    }

    .stSelectbox [data-baseweb="select"] span {
        color: #4A3E4D !important;
        font-weight: 600 !important;
    }

    @keyframes dropdownGradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .stButton > button {
        background: linear-gradient(
            -45deg,
            #B7D7B0,
            #9FA8DA,
            #C8A2C8,
            #A5D6A7
        ) !important;
        background-size: 300% 300% !important;
        animation: buttonGradient 6s ease infinite !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        width: 100%;
    }

    @keyframes buttonGradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .block-container {
        padding: 2rem 3rem 2rem 3rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# helper functions
def get_greeting():
    hour = datetime.now().hour

    if hour < 12:
        return "Good Morning"
    elif hour < 18:
        return "Good Afternoon"
    else:
        return "Good Evening"


def build_prompt(story, profile, greeting):
    return f"""
You are helping recruiters rewrite content into realistic LinkedIn communication styles.

Original content:
{story}

Target profile:
{profile}

Task:
Rewrite the content into 3 clearly different recruiter voices.

Important rules:
- Begin each version naturally with "{greeting}".
- Make the writing sound human, clear, and conversational.
- Do not sound like generic AI-generated LinkedIn content.
- Do not use excessive emojis, hype, motivational phrases, or buzzwords.
- Do not copy full sentences directly from the original content.
- Keep the original facts accurate.
- The metrics and technical wins belong to the recruiter's company, not the candidate.
- Naturally reference the target person's background once.

Persona styles:

Direct Headhunter:
- concise, sharp, confident
- maximum 120 words
- mention the strongest metric
- end with a simple call to action

Empathetic Coach:
- warm, thoughtful, people-focused
- focus on the human or career lesson
- end with an open-ended question

Industry Expert:
- knowledgeable and practical
- focus on lessons, trade-offs, and business impact
- avoid sounding like a report

Return only in this format:

[DIRECT_HEADHUNTER]
content here

[EMPATHETIC_COACH]
content here

[INDUSTRY_EXPERT]
content here
"""


def generate_with_openai(prompt):
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You create natural, professional recruiter-focused LinkedIn content."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7
    )

    return response.choices[0].message.content


def generate_with_gemini(prompt):
    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text


def generate_personas(prompt, model_choice):
    if model_choice == "OpenAI GPT-4o Mini":
        return generate_with_openai(prompt)

    if model_choice == "Google Gemini":
        return generate_with_gemini(prompt)


def split_outputs(output):
    direct = output.split("[DIRECT_HEADHUNTER]")[1].split("[EMPATHETIC_COACH]")[0].strip()
    coach = output.split("[EMPATHETIC_COACH]")[1].split("[INDUSTRY_EXPERT]")[0].strip()
    expert = output.split("[INDUSTRY_EXPERT]")[1].strip()

    return direct, coach, expert


def show_card(title, content):
    st.markdown(f"### {title}")

    with st.container(border=True):
        st.markdown(content)


def show_selected_output(persona_choice, direct, coach, expert):
    if persona_choice == "All Versions":
        show_card("Direct Headhunter", direct)
        show_card("Empathetic Coach", coach)
        show_card("Industry Expert", expert)

    elif persona_choice == "Direct Headhunter":
        show_card("Direct Headhunter", direct)

    elif persona_choice == "Empathetic Coach":
        show_card("Empathetic Coach", coach)

    elif persona_choice == "Industry Expert":
        show_card("Industry Expert", expert)


# title
st.markdown(
    """
    <h1 style='text-align: center;'>Persona Multiplier AI</h1>
    <p style='text-align: center; font-size:18px; color:#4A3E4D;'>
        Turn one story into multiple recruiter communication styles.
    </p>
    """,
    unsafe_allow_html=True
)


# keep generated output after dropdown changes
if "output" not in st.session_state:
    st.session_state["output"] = None


# main layout
left_col, right_col = st.columns([1, 1])

with left_col:
    story = st.text_area(
        "Original Content",
        placeholder="Paste a LinkedIn post, article snippet, or recruiter update...",
        height=220
    )

    profile = st.text_area(
        "Target Profile Information",
        placeholder="Paste career background, About section, or recent experience...",
        height=180
    )

    persona_choice = st.selectbox(
        "Choose which version to generate/view",
        [
            "All Versions",
            "Direct Headhunter",
            "Empathetic Coach",
            "Industry Expert"
        ]
    )

    model_choice = st.selectbox(
        "Choose AI Model",
        [
            "OpenAI GPT-4o Mini",
            "Google Gemini"
        ]
    )

    generate_button = st.button("Generate Persona Versions")


with right_col:
    if generate_button:

        if not story.strip() or not profile.strip():
            st.warning("Please complete both input sections.")

        elif len(story.strip().split()) < 15:
            st.warning("Please enter a more detailed original story or post.")

        elif len(profile.strip().split()) < 8:
            st.warning("Please enter more detailed target profile information.")

        else:
            with st.spinner("Generating personalised recruiter content..."):
                greeting = get_greeting()
                prompt = build_prompt(story, profile, greeting)

                st.session_state["output"] = generate_personas(
                    prompt,
                    model_choice
                )

    if st.session_state["output"]:
        st.subheader("Generated Output")

        direct_output, coach_output, expert_output = split_outputs(
            st.session_state["output"]
        )

        show_selected_output(
            persona_choice,
            direct_output,
            coach_output,
            expert_output
        )