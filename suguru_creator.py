# contains mainloop for pygame

import os
import pygame
pygame.init()

from components.constants import *
from components.state import State
from components.suguru import Suguru
from components.solver import Solver
from components.suguru import Group

pygame.mixer.pre_init(44100, 16, 2, 4096)


def calc_side_length(state):
    max_n = max(state["n_rows"], state["n_cols"])
    
    return (HEIGHT - PADDING*2) // max_n


def suguru_location_helper(state:State, suguru:Suguru, side_length:int):
    width, height, left, right, top, bottom = get_suguru_grid_dimensions(state)
    cell_to_location = dict()
    for row in range(suguru.grid.rows):
        for col in range(suguru.grid.cols):
            rect = pygame.Rect(left+col*side_length, top+row*side_length,
                               side_length, side_length)
            cell_to_location.update({(row, col): rect})
    
    return cell_to_location


def get_suguru_grid_dimensions(state):
    side_length = calc_side_length(state)
    width = side_length * state["n_cols"]
    height = side_length * state["n_rows"]
    left = (GRID_SPACE_WIDTH - width)//2
    right = GRID_SPACE_WIDTH - (GRID_SPACE_WIDTH - width)//2
    top = (HEIGHT - height)//2
    bottom = HEIGHT - (HEIGHT - height)//2
    return width, height, left, right, top, bottom

def draw_suguru_grid(win, state, side_length):
    width, height, left, right, top, bottom = get_suguru_grid_dimensions(state)
        
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
    


def draw(win, state:State, suguru:Suguru):
    base = pygame.Surface((WIDTH, HEIGHT))
    base.fill(WHITE)
    win.blit(base)
    
    if state == "size_selector":
        # calculate size of squares
        
        side_length = calc_side_length(state)
        state["side_length"] = side_length
        
        # draw
        
        draw_suguru_grid(win, state, side_length)
        
        # dividing line
        
        pygame.draw.line(surface=win, color=GREY,
                         start_pos=(GRID_SPACE_WIDTH, 0),
                         end_pos=(GRID_SPACE_WIDTH, HEIGHT))
        
        # controls
        
        #! to do

    elif state == "editor":
        
        
        # dividing line
        
        pygame.draw.line(surface=win, color=GREY,
                         start_pos=(GRID_SPACE_WIDTH, 0),
                         end_pos=(GRID_SPACE_WIDTH, HEIGHT))
        
        # shade all the un-assigned cells
        unassigned = [(r, c) for r in range(suguru.grid.rows) for c in range(suguru.grid.cols)]
        for group in suguru.get_groups():
            for cell in group:
                unassigned.remove(cell)
        
        for cell in unassigned:
            pygame.draw.rect(surface=win, color=GREY,
                             rect = state["cell_locations"][cell])
        
        
        # for row in range(suguru.grid.rows):
        #     for col in range(suguru.grid.cols):
        #         if not suguru.grid[(row, col)].is_assigned():
        #             pygame.draw.rect(surface=win, color=GREY,
        #                              rect = state["cell_locations"][(row, col)])
        
        draw_suguru_grid(win, state, state["side_length"])
        
        # all groups
        
        for group in suguru.get_groups():
            for line in get_group_borders(state, cells=group.cells):
                pygame.draw.line(surface=win, color=BLACK,
                                 start_pos=line[0], end_pos=line[1],
                                 width=GROUP_LINE_THICKNESS)
        
        # current group
        
        if state["current_group"] is not None:
            for line in get_group_borders(state, cells = state["current_group"],
                                          include_edges=True):
                pygame.draw.line(surface=win, color=GREEN,
                                 start_pos=line[0], end_pos=line[1],
                                 width=THICK_GROUP_LINE_THICKNESS)
        

def get_group_borders(state, cells:list[tuple[int, int]], include_edges:bool=False):
    cell_to_location = state["cell_locations"]
    
    if cells is None:
        return []
    
    lines = []
    for cell in cells:
        adjacents = {
            "up":    (-1,  0),
            "down":  ( 1,  0),
            "left":  ( 0, -1),
            "right": ( 0,  1)
         }
        rect = cell_to_location[cell]
        for direction, offset in adjacents.items():
            adjacent = (cell[0]+offset[0], cell[1]+offset[1])

            if adjacent not in cells:
                start_location = None
                end_location = None
                if direction == "left":
                    if cell[1] != 0 or include_edges:
                        start_location = (rect.left, rect.top)
                        end_location = (rect.left, rect.bottom)

                elif direction == "right":
                    if cell[1] != state["n_cols"]-1  or include_edges:
                        start_location = (rect.right, rect.top)
                        end_location = (rect.right, rect.bottom)
                    
                elif direction == "up":
                    if cell[0] != 0  or include_edges:
                        start_location = (rect.left, rect.top)
                        end_location = (rect.right, rect.top)
                        
                elif direction == "down":
                    if cell[0] != state["n_rows"]-1  or include_edges:
                        start_location = (rect.left, rect.bottom)
                        end_location = (rect.right, rect.bottom)
                
                if start_location is not None and end_location is not None:
                    lines.append((start_location, end_location))
    
    return lines


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
                
                elif event.key == pygame.K_LEFTBRACKET:
                    state["n_cols"] = max(1, state["n_cols"]-1)
                
                elif event.key == pygame.K_SPACE:
                    suguru.init(state["n_rows"], state["n_cols"])
                    side_length = state["side_length"]
                    state.set("editor", keep_data=True)
                    state.create_data_keys(
                        "side_length", "cell_locations", "current_group",
                        "input_cell_value", "input_cell_location",
                        "initial_values")
                    state["side_length"] = side_length
                    state["cell_locations"] = suguru_location_helper(
                        state=state, suguru=suguru, side_length=side_length)
                    state["initial_values"] = dict()
                    
                elif event.key == pygame.K_r:
                    state["n_cols"] = 5
                    state["n_rows"] = 5

        elif state == "editor":
            
            if event.type == pygame.MOUSEMOTION and pygame.mouse.get_pressed(3)[0]:
                for cell, rect in state["cell_locations"].items():
                    if rect.collidepoint(*pygame.mouse.get_pos()):
                        if suguru.check_cell_in_group(cell):
                            group = suguru.get_cell_group(cell)
                            group.delete()
                            suguru.remove_group(group)
                        else:
                            if state["current_group"] is None:
                                state["current_group"] = [cell]
                            elif cell not in state["current_group"]:
                                state["current_group"] += [cell]
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if state["current_group"] is not None:
                    suguru.add_group(state["current_group"])
                    state["current_group"] = None
                    input_cell_value(suguru, state)
                
                else:
                    print(state["cell_locations"])
                    for cell, location in state["cell_locations"].items():
                        if location.collidepoint(*pygame.mouse.get_pos()):
                            state["input_cell_location"] = cell
                            break
                    state["input_cell_value"] = ""
            
            
            elif event.type == pygame.KEYDOWN:
                if event.key in range(pygame.K_0, pygame.K_9+1):
                    if state["input_cell_value"] is not None:
                        state["input_cell_value"] += str(event.key-48)
                
                elif event.key == pygame.K_RETURN:
                    if state["input_cell_value"] is not None:
                        iv = {state["input_cell_location"]:int(state["input_cell_value"])}
                        state["initial_values"].update(iv)
                        state["input_cell_value"] = None
                        state["input_cell_location"] = None
                        print(state["initial_values"])
                        input_cell_value(suguru, state)
                        print(suguru)


def input_cell_value(suguru, state):
    suguru.set_initial_values(state["initial_values"])


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
