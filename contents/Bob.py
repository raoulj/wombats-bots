import time

def wombat(state, time_left):
    # Note that the function name MUST be wombat

    start = time.time()
    end = start + time_left

    return {
        'command': {
            'action': 'turn',
            'metadata': {
                'direction': 'forward'
            }
        },
        'state': {
            'hello': 'world'
        }
    }
