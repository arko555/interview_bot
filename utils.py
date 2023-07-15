from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
import os
from langchain.chains import create_tagging_chain_pydantic
from langchain.chat_models import ChatOpenAI
from pydantic import BaseModel, Field, conlist
from typing import Optional
from dotenv import load_dotenv

load_dotenv('config.env')

llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613")

def ask_for_info(ask_for):

    prompt = ChatPromptTemplate.from_template(
        """You are a job recruter who only ask questions.
        What you asking for are all and should only be in the list of "ask_for" list. 
        After you pickup a item in "ask for" list, you should extend it with 20 more words in your questions with more thoughts and guide.
        You should only ask one question at a time even if you don't get all according to the ask_for list. 
        Don't ask as a list!
        Wait for user's answers after each question. Don't make up answers.
        If the ask_for list is empty then thank them and ask how you can help them.
        Don't greet or say hi.
        ### ask_for list: {ask_for}

        """
    )

    chain = LLMChain(llm=llm, prompt=prompt)
    question = chain.run(ask_for=ask_for)

    return question

class PersonalDetails(BaseModel):
    full_name: Optional[str] = Field(
        None,
        description="Is the full name of the user.",
    )
    
    school_background: Optional[conlist(int, min_items=3, max_items=3)] = Field(
        None,
        description="""Qualification level of education background. Range is 1 to 10, the bigger number the higher qualified.
        The first element indicates the level of degree, 10 means master degree or higher, 1 means high school.
        The second element indicates the major relevance, 10 means computer science and its releated major.
        The third element indicates the college ranking, 10 means the Top 50 college of world, 1 means community college.
        0 means indeterminated.
        """,
    )
    working_experience: Optional[conlist(int, min_items=3, max_items=3)] = Field(
        None,
        description="""Qualification status of career background.Range is 1 to 10, the bigger number the higher qualified.
        The first element indicates job level, 10 means senior manager or above, 1 means intern.
        The second element indicates position relevance, 10 means software development positions.
        The third element indicates the company Ranking, 10 means the Top 500 companies of world, 1 means small local company.
        0 means indeterminated.
        """,

    )
    interview_motivation: Optional[int] = Field(
        None,
        description="""The candidate's motivation level to join the interview.
        10 means very interested and enthusiastic about the interview and new role opening. 1 means not interested.
        """,
    )

tagging_chain = create_tagging_chain_pydantic(PersonalDetails, llm)

#user_init_bio = PersonalDetails(full_name="",
#                                school_background=None,
#                                working_experience=None,
#                                interview_motivation=0)


def check_what_is_empty(user_peronal_details):
    " checks if any field is empty in ask_for list to be filled later"
    ask_for = []
    for field, value in user_peronal_details.dict().items():
        if value in [None, "", 0]:  
            print(f"Field '{field}' is empty.")
            ask_for.append(f'{field}')
    return ask_for

def add_non_empty_details(current_details: PersonalDetails, new_details: PersonalDetails):
    "stores details already received from user"
    non_empty_details = {k: v for k, v in new_details.dict().items() if v not in [None, "", 0]}
    updated_details = current_details.copy(update=non_empty_details)
    return updated_details


def filter_response(text_input, user_details):

    res = tagging_chain.run(text_input)
    user_details = add_non_empty_details(user_details,res)
    ask_for = check_what_is_empty(user_details)
    return user_details, ask_for