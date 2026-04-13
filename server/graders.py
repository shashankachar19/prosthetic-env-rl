# server/graders.py

def _evaluate_final_state(trajectory, task_type: int) -> float:
    """
    Vanilla OpenEnv Grader. 
    Safely reads the final observation to see if the agent completed the task.
    """
    try:
        # Safely extract the list of steps
        steps = trajectory if isinstance(trajectory, list) else getattr(trajectory, 'steps', [])
        
        if not steps:
            return 0.01  # Bot did nothing
            
        # Grab the very last step the agent took
        last_step = steps[-1]
        
        # Safely extract the observation 
        if hasattr(last_step, 'observation'):
            obs = last_step.observation
            grip = getattr(obs, 'current_grip', 0)
        else:
            obs = last_step.get('observation', {})
            grip = obs.get('current_grip', 0)

        # Check if the final state matches your YAML task descriptions
        success = False
        if task_type == 1 and (3 <= grip <= 7): success = True
        elif task_type == 2 and grip >= 9: success = True
        elif task_type == 3 and grip <= 1: success = True
        elif task_type == 4 and grip == 2: success = True
        elif task_type == 5 and grip == 8: success = True

        return 0.99 if success else 0.01
        
    except Exception:
        # Safe fallback so the validator never crashes
        return 0.01

# The explicit, static functions the YAML parser looks for
def grade_task_1(trajectory, **kwargs) -> float: return _evaluate_final_state(trajectory, 1)
def grade_task_2(trajectory, **kwargs) -> float: return _evaluate_final_state(trajectory, 2)
def grade_task_3(trajectory, **kwargs) -> float: return _evaluate_final_state(trajectory, 3)
def grade_task_4(trajectory, **kwargs) -> float: return _evaluate_final_state(trajectory, 4)
def grade_task_5(trajectory, **kwargs) -> float: return _evaluate_final_state(trajectory, 5)