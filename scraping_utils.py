import time
import random

def random_sleep_wait(lower=5, upper=12):
    ''' Function for pauzing the program for a random number of seconds.
    Minimum is, as dictated by robots.txt, 5 seconds.
    '''
    time.sleep(random.randint(lower, upper))
