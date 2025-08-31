import random

def create_random_string(size: int, chars):

    return ''.join(random.choice(chars) for _ in range(size))