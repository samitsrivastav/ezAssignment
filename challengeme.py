import streamlit as st
import google.generativeai as genai
import json
import time

def run_challenge():
    api_key = st.text_input("Enter your Gemini API Key", type="password", key="challenge_api_key")
    if not api_key:
        st.stop()

    genai.configure(api_key=api_key)

    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'current_stage' not in st.session_state:
        st.session_state.current_stage = "field"
    if 'field' not in st.session_state:
        st.session_state.field = None
    if 'self_reported_level' not in st.session_state:
        st.session_state.self_reported_level = None
    if 'current_level' not in st.session_state:
        st.session_state.current_level = None
    if 'questions_asked' not in st.session_state:
        st.session_state.questions_asked = 0
    if 'correct_answers' not in st.session_state:
        st.session_state.correct_answers = 0
    if 'assessment_complete' not in st.session_state:
        st.session_state.assessment_complete = False

    st.title("Skill Assessment: Challenge Me")

    with st.sidebar:
        st.header("Assessment Results")
        if st.session_state.assessment_complete:
            st.write(f"Field: **{st.session_state.field}**")
            st.write(f"Self-reported level: **{st.session_state.self_reported_level}**")
            st.write(f"Assessed level: **{st.session_state.current_level}**")
            st.write(f"Correct answers: **{st.session_state.correct_answers}/{st.session_state.questions_asked}**")

    def generate_question(field, level):
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        prompt = f"""
        Generate an MCQ to assess knowledge in {field} at a {level} level.
        Respond only in this JSON format:
        {{
            "question": "...",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "...",
            "explanation": "..."
        }}
        """
        response = model.generate_content(prompt)
        try:
            return json.loads(response.text)
        except:
            return {
                "question": "Error generating question. Please try again.",
                "options": ["Retry", "Retry", "Retry", "Retry"],
                "correct_answer": "Retry",
                "explanation": "AI failed to generate a valid question."
            }

    def generate_assessment(field, self_level, actual_level, correct_ratio):
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        prompt = f"""
        Summarize this skill assessment:
        - Field: {field}
        - Self-reported level: {self_level}
        - Actual level: {actual_level}
        - Correct answers ratio: {correct_ratio}
        Respond only in this JSON format:
        {{
            "assessment": "...",
            "strengths": "...",
            "areas_for_improvement": "...",
            "next_steps": "..."
        }}
        """
        response = model.generate_content(prompt)
        try:
            return json.loads(response.text)
        except:
            return {
                "assessment": "Error generating assessment.",
                "strengths": "N/A",
                "areas_for_improvement": "N/A",
                "next_steps": "N/A"
            }

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if not st.session_state.messages:
        msg = "What field are you interested in?"
        with st.chat_message("assistant"):
            st.write(msg)
        st.session_state.messages.append({"role": "assistant", "content": msg})

    if not st.session_state.assessment_complete:
        user_input = st.chat_input("Your response", key="challenge_input")
        if user_input:
            with st.chat_message("user"):
                st.write(user_input)
            st.session_state.messages.append({"role": "user", "content": user_input})

            if st.session_state.current_stage == "field":
                st.session_state.field = user_input
                st.session_state.current_stage = "level"
                msg = "What level do you think you are? (Beginner, Intermediate, Advanced, Expert)"
                with st.chat_message("assistant"):
                    st.write(msg)
                st.session_state.messages.append({"role": "assistant", "content": msg})

            elif st.session_state.current_stage == "level":
                st.session_state.self_reported_level = user_input.title()
                st.session_state.current_level = st.session_state.self_reported_level
                st.session_state.current_stage = "questioning"

                with st.spinner("Generating question..."):
                    q = generate_question(st.session_state.field, st.session_state.current_level)
                with st.chat_message("assistant"):
                    st.write(q["question"])
                    for i, opt in enumerate(q["options"]):
                        st.write(f"{chr(65+i)}. {opt}")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": q["question"] + "\n" + "\n".join([f"{chr(65+i)}. {o}" for i,o in enumerate(q["options"])])
                })
                st.session_state.current_question = q

            elif st.session_state.current_stage == "questioning":
                q = st.session_state.current_question
                user_ans = user_input.strip()
                correct = q["correct_answer"]

                is_correct = (
                    user_ans.upper() == correct.upper() or
                    user_ans.strip().lower() in correct.lower()
                )

                st.session_state.questions_asked += 1
                if is_correct:
                    st.session_state.correct_answers += 1

                with st.chat_message("assistant"):
                    if is_correct:
                        st.write("✓ Correct!")
                    else:
                        st.write(f"✗ Incorrect. The correct answer is: {correct}")
                    st.write(f"**Explanation:** {q['explanation']}")

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": (
                        "✓ Correct!" if is_correct else f"✗ Incorrect. Correct: {correct}"
                    ) + f"\n\nExplanation: {q['explanation']}"
                })

                if st.session_state.questions_asked >= 5:
                    st.session_state.assessment_complete = True
                    correct_ratio = f"{st.session_state.correct_answers}/{st.session_state.questions_asked}"

                    with st.spinner("Generating assessment..."):
                        assessment = generate_assessment(
                            st.session_state.field,
                            st.session_state.self_reported_level,
                            st.session_state.current_level,
                            correct_ratio
                        )

                    with st.chat_message("assistant"):
                        st.write("### Assessment Results")
                        st.write(assessment["assessment"])
                        st.write("**Strengths:**")
                        st.write(assessment["strengths"])
                        st.write("**Areas for Improvement:**")
                        st.write(assessment["areas_for_improvement"])
                        st.write("**Next Steps:**")
                        st.write(assessment["next_steps"])

                    summary_msg = f"### Results\n\n{assessment['assessment']}\n\n**Strengths:** {assessment['strengths']}\n\n**Areas for Improvement:** {assessment['areas_for_improvement']}\n\n**Next Steps:** {assessment['next_steps']}"
                    st.session_state.messages.append({"role": "assistant", "content": summary_msg})

                else:
                    with st.spinner("Generating next question..."):
                        q = generate_question(st.session_state.field, st.session_state.current_level)
                    with st.chat_message("assistant"):
                        st.write(q["question"])
                        for i, opt in enumerate(q["options"]):
                            st.write(f"{chr(65+i)}. {opt}")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": q["question"] + "\n" + "\n".join([f"{chr(65+i)}. {o}" for i,o in enumerate(q["options"])])
                    })
                    st.session_state.current_question = q

    else:
        if st.button("Start New Assessment"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.experimental_rerun()

if __name__ == "__main__":
    run_challenge()
