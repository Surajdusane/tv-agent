from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import Literal
from dotenv import load_dotenv

load_dotenv()

def get_youtube_query(state):

    task = state['current_task']
    task_number = state['task_number']

    # Initialize the Groq model (use any model you prefer)
    llm = ChatGroq(model="gemma2-9b-it")

    # Create output schema using Pydantic
    class YoutubeQueryOutput(BaseModel):
        query: str = Field(description="""Return query for youtube search for getting desired youtube video.""")

    # Create output parser using PydanticOutputParser
    query_output_parser = PydanticOutputParser(pydantic_object=YoutubeQueryOutput)

    # Create prompt template using PromptTemplate
    template = PromptTemplate(
        template="""You are a remote control agent. You are given a task to complete. Your task is to return a valid youtube query. this query will be used to search for the desired youtube video. dont use any other words in the query just simple search for getting desire youtube video. if there is any mention of movie then add full movie text in the query.
        Here is the task:
        {task} \n {format_instructions}
        """,
        input_variables=["task", "format_instructions"],
        partial_variables={"format_instructions": query_output_parser.get_format_instructions()},
    )

    # Create prompt
    prompt = template.invoke({"task": task})

    # Get response from the llm
    response = llm.invoke(prompt)

    # Parse the response using the output parser
    final_result = query_output_parser.parse(response.content)

    return { 'youtube_query': final_result.query, 'task_number': task_number + 1 }

# if __name__ == "__main__":
#   r = get_key({"current_task": "make volume 0"})
#   print(r)