
if __name__ == "__main__":
    from suguru import Suguru
    from constants import MAX_CELL_VALUE
else:
    from components.suguru import Suguru
    from components.constants import MAX_CELL_VALUE


class Solver:
    def __init__(self, suguru:Suguru, initial_values:dict[tuple[int, int]:int]):
        self.suguru = suguru
        self.initial_values = initial_values
    
    
    def __str__(self):
        return self.suguru.__str__()
    
    
    def check_filled(self):
        for row in self.suguru.grid:
            for cell in row:
                if cell.is_empty():
                    return False
        
        return True

    
    def check_solved(self):
        filled = self.check_filled()
        return filled
    
    
    def solve(self):
        newly_filled_cells = set(self.initial_values.keys())
        checking = True
        while checking:
            while newly_filled_cells:
                newly_filled_cells = self.solve_step(newly_filled_cells)
            
            newly_filled_cells = self.solve_step(
                [(r, c) for r in range(self.suguru.grid.rows) \
                    for c in range(self.suguru.grid.cols)])
            
            if not newly_filled_cells:
                checking = False
        
        if self.check_solved():
            print("Solve successful")
        else:
            print("Solve incomplete: not enough information")
    
    
    def adjacent_cell_exclusion(self, cells_to_check):
        newly_filled_cells = set()
        for cell in cells_to_check:
            if self.suguru.grid[cell].get_value():
                influenced_cells = self.suguru.grid.get_cell_roi(cell=cell)
                for ic in influenced_cells:
                    if self.suguru.grid[ic].is_empty():
                        self.suguru.grid[ic].remove_possible_values(
                            self.suguru.grid[cell].get_value())
                        if not self.suguru.grid[ic].is_empty():
                            newly_filled_cells.add(ic)
                            print("phase1", ic, "with value", self.suguru.grid[ic])
        return newly_filled_cells
    
    def group_exclusion(self):
        newly_filled_cells = set()
        for group in self.suguru.get_groups():
            values_in_group = group.get_filled_cells_values()
            empty_cells = group.get_empty_cells()
            for ec in empty_cells:
                self.suguru.grid[ec].remove_possible_values(*values_in_group)
                if not self.suguru.grid[ec].is_empty():
                    
                    newly_filled_cells.add(ec)
                    print("phase2", ec, "with value", self.suguru.grid[ec])
        
        return newly_filled_cells
    
    def group_single(self):
        newly_filled_cells = set()
        for group in self.suguru.get_groups():
            empty_cells = group.get_empty_cells()
            possible_values = {} # value : cell
            
            for i in range(MAX_CELL_VALUE+1):
                possible_values.update({i:[]})
                for ec in empty_cells:
                    if i in self.suguru.grid[ec].get_possible_values():
                        possible_values[i].append(ec)
            
            for value, cells in possible_values.items():
                if len(cells) == 1:
                    cell_to_fill = cells[0]
                    
                    # Safety check: Don't try to fill cells that are already filled
                    # This can happen if Phase 1 filled the cell after we captured empty_cells
                    if not self.suguru.grid[cell_to_fill].is_empty():
                        continue
                    
                    # Safety check: Don't fill a cell if the value already exists in the group
                    # This can happen if another phase filled a cell with this value
                    value_exists_in_group = False
                    for cell in group.cells:
                        if not self.suguru.grid[cell].is_empty() and self.suguru.grid[cell].get_value() == value:
                            value_exists_in_group = True
                            break
                    
                    if value_exists_in_group:
                        continue
                    
                    self.suguru.grid[cell_to_fill].set_value(value)
                    self.group_exclusion()
                    newly_filled_cells.add(cell_to_fill)
                    print("phase2.5", cell_to_fill, "with value", self.suguru.grid[cell_to_fill])

        return newly_filled_cells
    
    def group_multi_cell_exclusion(self):
        newly_filled_cells = set()
        for group in self.suguru.get_groups():
            possible_values = group.get_possible_values_of_empty_cells()
            empty_cells = group.get_empty_cells()
            
            for value in possible_values:
                e_cells_with_value = set()
                for ec in empty_cells:
                    if self.suguru.grid[ec].could_be(value):
                        e_cells_with_value.add(ec)
                
                # Only apply phase 3 if multiple cells could contain this value
                if len(e_cells_with_value) > 1:
                    influenced_cells = group.get_overlapping_roi_cells(list(e_cells_with_value))
                    for ic in influenced_cells:
                        if self.suguru.grid[ic].is_empty() and ic not in group.cells:
                            self.suguru.grid[ic].remove_possible_values(value)
                            if not self.suguru.grid[ic].is_empty():
                                newly_filled_cells.add(ic)
                                print("phase3", ic, "with value", self.suguru.grid[ic])
        return newly_filled_cells        
    
    
    def solve_step(self, cells_to_check:list[tuple[int, int]]):
        newly_filled_cells = set()
        
        # Phase 1
        newly_filled_cells = newly_filled_cells.union(self.adjacent_cell_exclusion(cells_to_check))
                
        # Phase 2
        newly_filled_cells_phase2 = self.group_exclusion()
        
        newly_filled_cells_phase2 = newly_filled_cells_phase2.union(
            self.group_single())
        
        # Run Phase 1 again on newly filled cells from Phase 2
        newly_filled_cells = newly_filled_cells.union(self.adjacent_cell_exclusion(
            cells_to_check=newly_filled_cells_phase2))
        
        newly_filled_cells.union(newly_filled_cells_phase2)
            
        # Phase 3
        newly_filled_cells = newly_filled_cells.union(self.group_multi_cell_exclusion())

        return newly_filled_cells


def test1():
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

    suguru = Suguru()
    suguru.init(5, 4)
    suguru.set_groups(gs)

    for key, value in pre_filled.items():
        suguru.grid[key].set_value(value)

    s = Solver(suguru, pre_filled)

    print(s)

    s.solve()

    print(s)
    pass

def test2():
    s = Suguru()
    s.init(9, 7)

    # list of groups (each group = list of (row, col) cells)
    groups = [
        [(0, 0), (1, 0), (1, 1), (2, 0), (3, 0), (3, 1), (4, 0)],
        [(0, 1), (0, 2), (0, 3), (0, 4)],
        [(0, 5), (0, 6), (1, 4), (1, 5), (1, 6), (2, 4), (2, 6)],
        [(1, 2), (1, 3), (2, 1), (2, 2), (3, 2), (4, 1), (4, 2)],
        [(2, 3), (3, 3), (3, 4), (4, 3), (4, 4), (5, 3)],
        [(2, 5), (3, 5), (3, 6)],
        [(4, 5), (4, 6), (5, 6), (6, 6)],
        [(5, 0)],
        [(5, 1), (5, 2), (6, 0), (6, 1), (6, 2), (6, 3), (7, 2)],
        [(5, 4), (5, 5), (6, 4), (6, 5), (7, 5)],
        [(7, 0), (7, 1), (8, 0), (8, 1)],
        [(7, 3), (7, 4), (8, 2), (8, 3), (8, 4)],
        [(7, 6), (8, 5), (8, 6)],
    ]


    # dictionary of given (pre-filled) numbers: key = (row, col), value = integer
    filled = {
        (0, 1): 2,
        (0, 3): 3,
        (0, 5): 4,
        (1, 4): 5,
        (2, 0): 2,
        (2, 2): 2,
        (2, 6): 6,
        (3, 0): 6,
        (3, 3): 3,
        (3, 4): 2,
        (4, 3): 5,
        (4, 6): 4,
        (5, 1): 4,
        (5, 4): 1,
        (6, 0): 7,
        (7, 0): 2,
        (7, 2): 5,
        (7, 6): 2,
        (8, 2): 4,
        (8, 4): 5,
    }

    s.set_groups(groups)
    s.set_initial_values(filled)
    print(s.check_valid_grouping())
    solver = Solver(s, filled)
    print(solver)
    solver.solve()
    print()
    print(solver)
    
def test3():
    groups = [
        [(0, 0), (0, 1), (0, 2), (1, 1), (2, 1)],
        [(1, 0), (2, 0)],
        [(0, 4), (0, 5), (0, 6)],
        [(1, 6), (1, 5), (2, 5), (3, 5), (2, 6)],
        [(1, 2), (1, 3), (0, 3), (1, 4), (2, 4)],
        [(2, 2), (2, 3), (3, 3), (4, 3), (3, 4)],
        [(4, 4)],
        [(3, 6), (4, 6), (5, 6), (5, 5), (4, 5)],
        [(6, 4), (6, 5), (6, 6), (7, 6), (7, 5)],
        [(5, 4), (5, 3), (6, 2), (5, 2), (6, 1)],
        [(6, 3), (7, 3), (7, 4), (7, 2), (7, 1)],
        [(7, 0), (6, 0), (5, 0), (4, 0), (5, 1)],
        [(3, 0), (3, 1), (3, 2), (4, 2), (4, 1)]
        ]
    filled = {(4, 0): 3, (7, 0): 5, (7, 1): 2, (7, 5): 4, (0, 5): 2, (1, 5): 4, (1, 2): 3}
    
    filled.update({(5,1):4}) # from a hint which makes the rest solvable
    
    s = Suguru()
    s.init(8, 7)
    
    s.set_groups(groups)
    s.set_initial_values(filled)
    print(s.check_valid_grouping())
    solver = Solver(s, filled)
    print(solver)
    solver.solve()
    print()
    print(solver)

def test4():
    groups = [
        [(1, 0), (0, 0), (0, 1), (0, 2), (0, 3)],
        [(0, 6), (0, 5), (1, 5), (1, 4), (0, 4)],
        [(1, 6)],
        [(2, 6), (3, 6), (4, 6), (4, 5), (3, 5)],
        [(2, 4), (2, 3), (3, 3), (3, 4), (2, 5)],
        [(1, 3), (1, 2), (1, 1), (2, 2)],
        [(2, 1), (2, 0), (3, 0), (3, 1)],
        [(3, 2), (4, 2)],
        [(4, 0)],
        [(5, 1), (6, 1), (6, 2), (5, 2), (4, 1)],
        [(5, 0), (6, 0), (7, 0)],
        [(8, 0), (8, 1), (8, 2), (7, 2), (7, 1)],
        [(6, 3), (7, 3), (8, 3), (8, 4), (7, 4)],
        [(8, 5), (8, 6), (7, 6)],
        [(5, 6), (6, 6), (6, 5), (6, 4), (7, 5)],
        [(5, 5), (5, 4), (4, 4), (4, 3), (5, 3)],
    ]
    
    filled = {(1, 0): 5, (0, 6): 4, (1, 6): 1, (3, 6): 4, (8, 6): 1, (8, 3): 4, (8, 1): 5, (7, 1): 4, (5, 0): 3}
    
    s = Suguru()
    s.init(9, 7)
    
    s.set_groups(groups)
    s.set_initial_values(filled)
    print(s.check_valid_grouping())
    solver = Solver(s, filled)
    print(solver)
    solver.solve()
    print()
    print(solver)
    
    

