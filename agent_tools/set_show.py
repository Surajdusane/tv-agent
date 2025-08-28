from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import Literal
from dotenv import load_dotenv

load_dotenv()

def setShowName(state):

    print("🧠 Extracting show/movie name from user task...")

    task = state['current_task']
    task_number = state['task_number']

    print(f"📌 Current task: {task}")

    # Initialize the Groq model (use any model you prefer)
    llm = ChatGroq(model="gemma2-9b-it")

    # Create output schema using Pydantic
    class ShowNameOutput(BaseModel):
        showName: str = Field(description="""Movie or TV show name to be set.""")

    # Create output parser using PydanticOutputParser
    show_name_parser = PydanticOutputParser(pydantic_object=ShowNameOutput)

    # Create prompt template using PromptTemplate
    template = PromptTemplate(
        template="""You are a remote control agent. You are given a task to complete. Your task is to extrat movie or tv show name from user task and return a valid movie or tv show name.
        Here is the task:
        {task} \n {format_instructions}
        """,
        input_variables=["task", "format_instructions"],
        partial_variables={"format_instructions": show_name_parser.get_format_instructions()},
    )

    # Create prompt
    prompt = template.invoke({"task": task})

    # Get response from the llm
    response = llm.invoke(prompt)

    # Parse the response using the output parser
    final_result = show_name_parser.parse(response.content)

    print(f"🎯 Extracted show name: {final_result.showName}")
    print("✅ Extraction complete.\n")

    return { 'target_show_name': final_result.showName, 'show_name': final_result.showName, 'task_number': task_number + 1 }

# if __name__ == "__main__":
#   r = setShowName({"current_task": "show me war 2 movie"})
#   print(r)