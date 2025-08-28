from agent_tools.planner import planner
from agent_tools.get_key import get_key
from agent_tools.send_key import sendCodeTest
import asyncio

async def test_volume_command():
    print("Testing volume command...")
    
    # Test the planner
    plan = planner({'current_task': 'increase volume 2 times'})
    print(f'Plan: {plan}')
    
    # Test get_key
    state1 = {'current_task': 'increase volume 2 times', 'task_number': 0}
    result1 = get_key(state1)
    print(f'Get key result: {result1}')
    
    # Test send_code
    state2 = {
        'current_task_command': result1['current_task_command'], 
        'repeat': result1['repeat'], 
        'task_number': result1['task_number']
    }
    result2 = await sendCodeTest(state2)
    print(f'Send code result: {result2}')
    
    return result2

if __name__ == "__main__":
    asyncio.run(test_volume_command())