from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import Literal, List
from dotenv import load_dotenv

load_dotenv()

def planner(state):

    task = state['current_task']

    # Initialize the Groq model (use any model you prefer)
    llm = ChatGroq(model="gemma2-9b-it")

    # Create output schema using Pydantic
    class PlannerState(BaseModel):
        edges: List[Literal["get_key", "send_code", "get_youtube_query", "get_youtube_link", "send_link", "get_platform", "get_recommendations", "set_show_name"]] = Field(description="""The list of edges in the graph this list is sequetion execution of the agent""")

    # Create output parser using PydanticOutputParser
    plan_output_parser = PydanticOutputParser(pydantic_object=PlannerState)

    # Create prompt template using PromptTemplate
    template = PromptTemplate(
        template="""You are a goal oriented remote control agent. Your task is to create a function plans that will help you to achieve your goal. you have access to the following tools:
        for getting key code to controll remote keys = "get_key" (volume up, volume down, volume 0, mute, play/pause, home, back, power)
        for sending key code to controll remote keys = "send_code" (send key code to the device)
        for getting youtube query for searching youtube videos = "get_youtube_query" (use this when user need to listen song, view specefic video, if movie they specific say view movie on youtube or any other video those not available on ott platforms then use this tool)
        for getting working youtube link form the youtube query = "get_youtube_link" (get youtube link from youtube query)
        for sending youtube link to the device = "send_link" (this use sending link to play video or tv show or movie on device this is only way to play any kind of media on device this is also use for tv show and movie and app launch)
        for getting platform info like wich movie or tv show available on perticular platform = "get_platform" (get platform info)
        for getting movie or tv show recommendations using one movie or tv show name = "get_recommendations" (get recommendations for the movie or tv show)
        for setting movie or tv show name = "set_show_name" (set movie or tv show name this is helpful for extracting movie name from user input)

        your task:
        using user provided goal you need to create a plan for achieving the goal this plan achive through the use of the above tools you need to return sequetionn list of this tools each tool should be a function name from the above list.

        example:
        user goal is to play romantic song = ["get_youtube_query", "get_youtube_link", "send_link"]
        user goal is to watch similer movie or tv show = ["set_show_name", "get_recommendations", "get_platform", "send_link"]
        user goal is increase volume = ["get_key", "send_code"]
        user goal is watch perticular movie or tv show = ["set_show_name", "get_platform", "send_link"]
        user goal is watch movie trailer = ["get_youtube_query", "get_youtube_link", "send_link"]

        {task} \n {format_instructions}
        """,
        input_variables=["task", "format_instructions"],
        partial_variables={"format_instructions": plan_output_parser.get_format_instructions()},
    )

    # Create prompt
    prompt = template.invoke({"task": task})

    # Get response from the llm
    response = llm.invoke(prompt)

    # Parse the response using the output parser
    final_result = plan_output_parser.parse(response.content)

    return { 'edges': final_result.edges }

# if __name__ == "__main__":
#   r = planner({"current_task": "i want to watch war 2 like movie"})
#   print(r)