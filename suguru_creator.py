# contains mainloop for pygame

import os
import pygame
pygame.init()

from components.constants import *
from components.state import State
from components.suguru import Suguru
from components.solver import Solver

pygame.mixer.pre_init(44100, 16, 2, 4096)



def calc_side_length(state):
    max_n = max(state["n_rows"], state["n_cols"])
        
    return (HEIGHT - PADDING*2) // max_n


def suguru_location_helper(suguru:Suguru, side_length:int):
    cell_to_location = dict()
    for row in range(suguru.grid.rows):
        for col in range(suguru.grid.cols):
            cell_to_location.update(
                {suguru.grid[(row, col)]: (PADDING+row*side_length,
                                           PADDING+col*side_length)})


def draw(win, state, suguru):
    base = pygame.Surface((WIDTH, HEIGHT))
    base.fill(WHITE)
    win.blit(base)
    
    
    if state == "size_selector":
        # calculate size of squares
        
        side_length = calc_side_length(state)
        state["side_length"] = side_length
        
        # draw
        grid_space_width = HEIGHT
        
        width = side_length * state["n_cols"]
        height = side_length * state["n_rows"]
        left = (grid_space_width - width)//2
        right = grid_space_width - (grid_space_width - width)//2
        top = (HEIGHT - height)//2
        bottom = HEIGHT - (HEIGHT - height)//2
        
        pygame.draw.rect(surface=win, rect=pygame.Rect(
                            left-GROUP_LINE_THICKNESS, top-GROUP_LINE_THICKNESS,
                            width + 2*GROUP_LINE_THICKNESS, height + 2*GROUP_LINE_THICKNESS),
                        color=BLACK, width=GROUP_LINE_THICKNESS)
        
        for r in range(state["n_rows"]-1):
            pygame.draw.line(surface=win, color=BLACK,
                            start_pos=(left, top + side_length*(r+1)),
                            end_pos=(right, top + side_length*(r+1)))
        
        for c in range(state["n_cols"]-1):
            pygame.draw.line(surface=win, color=BLACK,
                            start_pos=(left + side_length*(c+1), top),
                            end_pos=(left + side_length*(c+1), bottom))
        
        # dividing line
        
        pygame.draw.line(surface=win, color=GREY,
                         start_pos=(grid_space_width, 0),
                         end_pos=(grid_space_width, HEIGHT))
        
        # controls
        
        #! to do
        
        
        
        
    elif state == "editor":
        pass
    
    


def handle_events(state:State, suguru:Suguru, events:list[pygame.Event]):
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            
            import sys
            sys.exit()
        
        
        if state == "size_selector":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_EQUALS:
                    state["n_rows"] += 1

                elif event.key == pygame.K_MINUS:
                    state["n_rows"] = max(1, state["n_rows"]-1)
                
                elif event.key == pygame.K_RIGHTBRACKET:
                    state["n_cols"] += 1
                    print(state["n_cols"])
                
                elif event.key == pygame.K_LEFTBRACKET:
                    state["n_cols"] = max(1, state["n_cols"]-1)
                    print(state["n_cols"])
                
                elif event.key == pygame.K_SPACE:
                    suguru.init(state["n_rows"], state["n_cols"])
                    state.set("editor")
                    
                elif event.key == pygame.K_r:
                    state["n_cols"] = 5
                    state["n_rows"] = 5

        elif state == "editor":
            
            if event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed(3)[0]:
                    pass
                    


def main():
    # display window that is drawn to
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Suguru Solver")

    clock = pygame.time.Clock()
    
    state = State("size_selector")
    state.create_data_keys("n_rows", "n_cols", "side_length")
    state["n_rows"] = 5
    state["n_cols"] = 5
    state["side_length"] = calc_side_length(state)
    
    suguru = Suguru()

    run = True
    while run:
        clock.tick(FPS)
        
        handle_events(state, suguru, pygame.event.get())

        draw(win, state, suguru)
        pygame.display.update()


if __name__ == "__main__":
    main()
