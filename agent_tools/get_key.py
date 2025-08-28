from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import Literal
from dotenv import load_dotenv

load_dotenv()

def get_key(state):

    print("[KEY] Starting key command generation...")

    task = state['current_task']
    task_number = state['task_number']

    print(f"[TASK] Task #{task_number + 1}: {task}")

    # Initialize the Groq model (use any model you prefer)
    llm = ChatGroq(model="gemma2-9b-it")

    # Create output schema using Pydantic
    class SendKeyOutput(BaseModel):
        command: Literal["KEYCODE_DPAD_UP", "KEYCODE_DPAD_DOWN", "KEYCODE_DPAD_LEFT", "KEYCODE_DPAD_RIGHT", "KEYCODE_DPAD_CENTER", "KEYCODE_MEDIA_PLAY_PAUSE", "KEYCODE_HOME", "KEYCODE_BACK", "KEYCODE_POWER", "KEYCODE_MUTE", "KEYCODE_VOLUME_UP", "KEYCODE_VOLUME_DOWN"] = Field(description="""Return key code depending on the task 
        here are the key codes
            "key up code": "KEYCODE_DPAD_UP",
            "key down code": "KEYCODE_DPAD_DOWN",
            "key left code": "KEYCODE_DPAD_LEFT",
            "key right code": "KEYCODE_DPAD_RIGHT",
            "key select code this is use for selection and work like tap on the screen or OK button": "KEYCODE_DPAD_CENTER",
            "key media play pause": "KEYCODE_MEDIA_PLAY_PAUSE",
            "key home": "KEYCODE_HOME",
            "key back": "KEYCODE_BACK",
            "key power": "KEYCODE_POWER",
            "key mute or volume 0 and also use for unmute": "KEYCODE_MUTE",
            "key volume up": "KEYCODE_VOLUME_UP",
            "key volume down": "KEYCODE_VOLUME_DOWN"
        """)
        repeat : int = Field(default=1,description="""The number of times to repeat the key code this only required if you want to send the key code multiple times example volume increasing and decreasing""")

    # Create output parser using PydanticOutputParser
    key_output_parser = PydanticOutputParser(pydantic_object=SendKeyOutput)

    # Create prompt template using PromptTemplate
    template = PromptTemplate(
        template="""You are a remote control agent. You are given a task to complete. Your task is to return a valid key code. 
        Your task is to send the key code to the device. 
        Here is the task:
        {task} \n {format_instructions}
        """,
        input_variables=["task", "format_instructions"],
        partial_variables={"format_instructions": key_output_parser.get_format_instructions()},
    )

    # Create prompt
    prompt = template.invoke({"task": task})

    # Get response from the llm
    response = llm.invoke(prompt)

    # Parse the response using the output parser
    final_result = key_output_parser.parse(response.content)

    print(f"[DONE] Task processed successfully. | current_task_command : {final_result.command} | repeat :  {final_result.repeat}\n" )

    return { 'current_task_command': final_result.command, 'repeat': final_result.repeat, 'task_number': task_number + 1 }

# if __name__ == "__main__":
#   r = get_key({"current_task": "make volume 0"})
#   print(r)