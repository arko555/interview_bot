import plotly.express as px
import pandas as pd
import streamlit as st
from streamlit_chat import message
import time
from utils import PersonalDetails, ask_for_info, filter_response

user_init_bio = PersonalDetails(full_name="",
                                school_background=None,
                                working_experience=None,
                                interview_motivation=0)

ask_init = ['full_name', 'school_background', 'working_experience', 'interview_motivation']

def radar_chart(motivation, education, career):  
    df = pd.DataFrame(dict(
    r=[motivation,
       education[0],
       education[1],
       education[2],
       career[0],
       career[1],
       career[2]
       ],
    theta=['Motivation', 'Highest Degree','Academic Major','College Ranking',
           'Job Level', 'Job Position', 'Company Ranking']))

    fig = px.line_polar(df, r='r', theta='theta',  line_close=True,
                    color_discrete_sequence=px.colors.sequential.Plasma_r,
                    template="plotly_dark", title="Candidate's Job Match", range_r=[0,10])
    st.sidebar.header('For Recruiter Only:')
    st.sidebar.write(fig)

if "messages" not in st.session_state:
    question = ask_for_info(ask_init)
    st.session_state.messages = [{"role":"assistant", "content":question}]
if "details" not in st.session_state:
    st.session_state.details = user_init_bio
if "ask_for" not in st.session_state:
    st.session_state.ask_for = ask_init

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if answer := st.chat_input("Please answer the question. "):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": answer})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(answer)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        st.session_state.details, st.session_state.ask_for = filter_response(answer, st.session_state.details)
        if st.session_state.ask_for != []:
            assistant_response = ask_for_info(st.session_state.ask_for)
            
        else:
            assistant_response = """Thank you for participating in this interview. 
                                    We will notify you of the next steps once we have reached a conclusion.
                                 """

            final_details = st.session_state.details.dict()
            radar_chart(final_details['interview_motivation'], final_details['school_background'], final_details['working_experience'])

        for chunk in assistant_response.split():
            full_response += chunk + " "
            time.sleep(0.05)
            # Add a blinking cursor to simulate typing
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
        
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})