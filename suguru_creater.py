# contains mainloop for pygame

import os
import pygame
pygame.init()

from components.constants import *
from components.state import State
from 

pygame.mixer.pre_init(44100, 16, 2, 4096)

def draw(win, state):
    


def handle_events(events:list[pygame.Event]):
    for event in events:
        if event.type == pygame.MOUSEMOTION:
            if pygame.mouse.get_pressed(3)[0]:
                
                


def main():
    # display window that is drawn to
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Suguru Solver")

    clock = pygame.time.Clock()
    
    state = State("size_selector")

    run = True
    while run:
        clock.tick(FPS)
        
        handle_events(pygame.event.get())

        draw(win, state)
        pygame.display.update()


if __name__ == "__main__":
    main()
