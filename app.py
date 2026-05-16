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
Rewrite the source content into 3 clearly different recruiter communication styles.

You are "Persona Multiplier AI" — an advanced recruitment copywriting engine designed to transform one source story into multiple recruiter outreach perspectives.

IMPORTANT RULES

Perspective
- Avoid first-person company perspective such as: "I", "we", "our company", or "our team".
- Second-person language like "you" and "your experience" is allowed and encouraged for natural recruiter outreach.
- Do not sound like the hiring company directly speaking internally.
- Do not sound like the candidate personally built the project.
- Keep the perspective detached and recruiter-oriented.

Tone & Writing Style
- Begin every version naturally with "{greeting}".
- Write naturally, conversationally, and realistically for LinkedIn DMs.
- Keep the tone concise and human.
- Avoid sounding overly corporate, PR-written, or AI-generated.
- Avoid buzzwords, hype, excessive enthusiasm, emojis, or motivational language.
- Prioritize authenticity over perfect polished wording.
- The output should feel ready to send directly as recruiter outreach.

Writing Quality
- Do not copy full sentences from the original content.
- Preserve the original meaning while rewriting vocabulary and structure naturally.
- Use completely different sentence openings and narrative flow across all 3 versions.
- Each version should feel independently written.
- Do not hallucinate or invent facts.
- Write like a real recruiter typing quickly on LinkedIn.
- Slight imperfections and conversational phrasing are acceptable.
- Avoid sounding overly structured or essay-like.
- Prioritize realism over polished writing.

Accuracy Rules
- Reference the candidate’s background naturally once per version.
- Attribute all technical wins, metrics, and project outcomes to the hiring company or project — not the candidate.

Persona Styles

Direct Headhunter
- Sound like an external recruiter or headhunter.
- Focus on business impact, hiring relevance, and opportunity alignment.
- Keep the tone commercially sharp and concise.
- Frame the story as relevant to the candidate’s experience.
- End with a simple low-friction call to action.

Empathetic Coach
- Sound warm, thoughtful, supportive, and relationship-driven.
- Focus on the human impact, challenges, growth, or user experience behind the work.
- Avoid sounding sales-focused or transactional.
- Make the candidate feel understood rather than pitched.
- End with a reflective or open-ended question.

Industry Expert
- Sound like a senior AI/product/engineering leader discussing systems or industry trends.
- Focus on architecture, technical trade-offs, operational lessons, or long-term impact.
- Keep the tone conversational but highly knowledgeable.
- Do not sound like a recruiter selling a role.
- End with a discussion-style technical or strategic question.

Return only in this exact structure:

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