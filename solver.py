from suguru import Suguru, Grid, Group, Row, Cell


class Solver:
    def __init__(self, rows, columns):
        self.suguru = Suguru(rows=rows, columns=columns)
    
    
    def __str__(self):
        return self.suguru.__str__()
    
    
    def solve(self):
        newly_filled_cells = []
    
    
    def solve_step(self, cells_to_check:list[tuple[int, int]]):
        newly_filled_cells = set()
        
        # Phase 1
        for cell in cells_to_check:
            influenced_cells = self.suguru.grid.get_cell_roi(cell=cell)
            for ic in influenced_cells:
                if self.suguru.grid[ic].is_empty():
                    self.suguru.grid[ic].remove_possible_values(
                        self.suguru.grid[cell].get_value())
                    if not self.suguru.grid[ic].is_empty():
                        newly_filled_cells.add(ic)
                
        
        # Phase 2
        for group in self.suguru.get_groups():
            values_in_group = group.get_filled_cells_values()
            empty_cells = group.get_empty_cells()
            for ec in empty_cells:
                self.suguru.grid[ec].remove_possible_values(*values_in_group)
                if not self.suguru.grid[ec].is_empty():
                    newly_filled_cells.add(ic)
            
            # Phase 3
            influenced_cells = group.get_overlapping_roi_cells(empty_cells)
            print("ic", influenced_cells)
            for ic in influenced_cells:
                if self.suguru.grid[ic].is_empty():
                    self.suguru.grid[ic].remove_possible_values(*values_in_group)
                    if not self.suguru.grid[ic].is_empty():
                        newly_filled_cells.add(ic)
        

        return newly_filled_cells

gs = [
    [(0, 0), (0, 1), (1, 1), (1, 2), (2, 1), (2, 2)],
    [(1, 0), (2, 0)],
    [(0, 2), (0, 3), (1, 3), (2, 3), (3, 3), (3, 2)],
    [(3, 0), (3, 1), (4, 0), (4, 1)],
    [(4, 2), (4, 3)],
]

pre_filled = {
    (0, 1): 1,
    (1, 1): 4,
    (2, 1): 5,
    (1, 2): 3,
    (0, 3): 2,
    (1, 3): 6,
    (3, 0): 3,
    (4, 1): 1,
    (3, 2): 3,
}

suguru = Suguru(5, 4)
suguru.set_groups(gs)

for key, value in pre_filled.items():
    suguru.grid[key].set_value(value)

s = Solver(5, 4)
s.suguru = suguru

print(s)
newly_filled_cells = list(pre_filled.keys())
while newly_filled_cells:
    newly_filled_cells = s.solve_step(newly_filled_cells)

print()
print(s)
