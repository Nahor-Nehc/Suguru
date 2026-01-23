
if __name__ == "__main__":
    from suguru import Suguru, Group
    from constants import MAX_CELL_VALUE
else:
    from components.suguru import Suguru, Group
    from components.constants import MAX_CELL_VALUE

cell_to_check = (8, 1)


class Solver:
    def __init__(self, suguru:Suguru, initial_values:dict[tuple[int, int]:int]):
        self.suguru = suguru
        self.initial_values = initial_values
        self.solved_cells = set()
    
    
    def __str__(self):
        return self.suguru.__str__()
    
    
    def ensure_filled(self):
        for row in self.suguru.grid:
            for cell in row:
                if cell.is_empty():
                    return False
        
        return True

    def ensure_neighbours(self):
        for cell in self.suguru.grid.get_cell_coordinates():
            for c in self.suguru.grid.get_cell_roi(cell):
                if self.suguru.grid[cell].get_value() == self.suguru.grid[c].get_value():
                    return False
        return True

    def ensure_groups(self):
        for group in self.suguru.get_groups():
            contains = [self.suguru.grid[cell].get_value() for cell in group.cells]
            for value in range(1, len(group.cells)+1):
                if value not in contains:
                    return False
                else:
                    contains.remove(value)
                    
            if contains:
                return False
    
    def ensure_solved(self):
        filled = self.ensure_filled()
        neighbours = self.ensure_neighbours()
        groups = self.ensure_groups()
        return filled and neighbours and groups
    
    def solve(self):
        checking = True
        
        all_cells = set(self.suguru.grid.get_cell_coordinates())
        
        to_check = self.initial_values.keys()

        while checking:
            updated_suguru = False
            print(self.suguru)
            for cell in to_check:
                updated_suguru = self.solve_cell(cell) or updated_suguru

            print(updated_suguru)
            print(self.suguru)
            to_check = all_cells.difference(self.solved_cells)
                
            for group in self.suguru.get_groups():
                updated_suguru = self.check_group(group) or updated_suguru
                if updated_suguru == True:
                    print(group, "was updated")
            print(updated_suguru)
            
            if not updated_suguru:
                checking = False
                
        if self.ensure_solved():
            print("Solve successful")
        else:
            print(self.suguru)
            print("Solve incomplete: not enough information")

            
    
    def solve_cell(self, cell:tuple[int, int]):
        # print("solving cell", cell, self.solved_cells, cell in self.solved_cells)
        print("solving cell", cell)
        
        self.solved_cells.add(cell)
        updated1 = self.exclude_adjacent_cells(cell)
        updated2 = self.exclude_same_group_cells(cell)

        updated_suguru = updated1 or updated2
        
        return updated_suguru
        
    
    def exclude_adjacent_cells(self, cell):
        print(cell, "adj")
        updated_suguru = False
        if self.suguru.grid[cell].is_empty():
            return updated_suguru
        
        influenced_cells = self.suguru.grid.get_cell_roi(cell=cell)
        for ic in influenced_cells:
            print("\t", ic, self.suguru.grid[cell].get_value())
            if self.suguru.grid[ic].is_empty():
                before = self.suguru.grid[ic].get_possible_values()[:]
                print("\t\t", before, end = "")
                self.suguru.grid[ic].remove_possible_values(
                    self.suguru.grid[cell].get_value())
                after = self.suguru.grid[ic].get_possible_values()
                if before != after:
                    updated_suguru = True
                
                print(after, before ==after, "="*60 if ic==cell_to_check else "")
                if not self.suguru.grid[ic].is_empty():
                    print("adjacency:", ic, "with value", self.suguru.grid[ic])
                    self.solve_cell(ic)
        
        return updated_suguru
    
    def exclude_same_group_cells(self, cell):
        print(cell, "group", self.suguru.grid[cell].is_empty(), self.suguru.grid[cell].get_possible_values())
        updated_suguru = False
        if self.suguru.grid[cell].is_empty():
            return updated_suguru
        
        group = self.suguru.get_cell_group(cell)
        empty_cells = group.get_empty_cells()
        print("solving", empty_cells)
        for ec in empty_cells:
            print("\t", ec, self.suguru.grid[cell].get_value())
            before = self.suguru.grid[ec].get_possible_values()[:]
            self.suguru.grid[ec].remove_possible_values(self.suguru.grid[cell].get_value())
            after = self.suguru.grid[ec].get_possible_values()
            if before != after:
                updated_suguru = True
            print("\t\t", before, after, "="*60 if ec==cell_to_check else "")
            if not self.suguru.grid[ec].is_empty():
                self.solve_cell(ec)
                print("group:", ec, "with value", self.suguru.grid[ec])
        
        return updated_suguru
    
    
    def check_group(self, group:Group):
        """
        Checks if one of the cells contains the only possible location for a value
        Checks for multi-cell exclusion
        
        :param self: Description
        :param group: Description
        :type group: Group
        """
        updated_suguru = False
        
        # print("checking group", group)
        # for cell in group.cells:
        #     print(cell, self.suguru.grid[cell].get_possible_values())
        
        possible_values = group.get_possible_values_of_empty_cells()
        empty_cells = group.get_empty_cells()
        
        print("checking group", group.cells, possible_values, empty_cells)
        
        for value in possible_values:
            empty_cells_with_value = set()
            for ec in empty_cells:
                if self.suguru.grid[ec].could_be(value):
                    empty_cells_with_value.add(ec)
            
            # Only apply multicell exclusion if multiple cells could contain this value
            if len(empty_cells_with_value) > 1:
                print("\tmult", empty_cells_with_value, value)
                influenced_cells = group.get_overlapping_roi_cells(list(empty_cells_with_value))
                for ic in influenced_cells:
                    if self.suguru.grid[ic].is_empty() and ic not in group.cells:
                        before = self.suguru.grid[ic].get_possible_values()[:]
                        self.suguru.grid[ic].remove_possible_values(value)
                        after = self.suguru.grid[ic].get_possible_values()
                        if before != after:
                            updated_suguru = True
                        

                        if not self.suguru.grid[ic].is_empty():
                            self.solve_cell(ic)
            
            # If only one cell can have value 'value'
            elif len(empty_cells_with_value) == 1:
                cell = empty_cells_with_value.pop()
                print("\tsing", cell, possible_values)
                self.suguru.grid[cell].set_value(value)
                self.solve_cell(cell)
                updated_suguru = True

        return updated_suguru
    
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
    
    # 6 | 1 | 5 | 2
    # 2 | 4 | 3 | 6
    # 1 | 5 | 2 | 1
    # 3 | 4 | 3 | 4
    # 2 | 1 | 2 | 1
    

def test2():
    s = Suguru()
    s.init(9, 7)
    # lvl 158
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
    
    # 1 | 2 | 4 | 3 | 1 | 4 | 3
    # 4 | 3 | 5 | 6 | 5 | 2 | 1
    # 2 | 1 | 2 | 1 | 7 | 3 | 6
    # 6 | 5 | 4 | 3 | 2 | 1 | 2
    # 7 | 3 | 7 | 5 | 6 | 3 | 4
    # 1 | 4 | 1 | 4 | 1 | 5 | 2
    # 7 | 3 | 2 | 6 | 2 | 3 | 1
    # 2 | 1 | 5 | 3 | 1 | 4 | 2
    # 4 | 3 | 4 | 2 | 5 | 3 | 1
    
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
    
    # filled.update({(5,1):4}) # from a hint which makes the rest solvable
    
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
    

def test5():
    # lvl 140
    groups = [
        [(0, 0), (0, 1), (0, 2), (1, 2), (1, 1)],
        [(2, 0), (3, 0), (3, 1), (2, 1), (1, 0)],
        [(0, 4), (0, 3), (1, 3), (2, 3), (2, 2)],
        [(1, 5), (0, 5), (0, 6), (1, 6), (2, 6)],
        [(1, 4), (2, 4), (2, 5), (3, 5)],
        [(3, 6), (4, 6), (5, 6), (6, 6), (7, 6)],
        [(8, 6), (8, 5)],
        [(7, 5), (6, 5), (5, 5), (5, 4), (6, 4)],
        [(7, 4)],
        [(8, 4), (8, 3), (7, 3), (8, 2), (8, 1)],
        [(8, 0)],
        [(7, 0), (6, 0), (5, 0), (5, 1), (6, 1)],
        [(7, 1), (7, 2), (6, 2), (6, 3), (5, 3)],
        [(4, 0), (4, 1), (4, 2), (3, 2), (5, 2)],
        [(3, 4), (3, 3), (4, 3), (4, 4), (4, 5)],
        ]
    pre_filled = {(3, 4): 1, (4, 5): 4, (0, 6): 3, (5, 6): 5, (8, 3): 3, (6, 0): 1, (4, 1): 3, (5, 2): 4, (2, 1): 2, (0, 0): 3, (0, 3): 3}
    
    s = Suguru()
    s.init(9, 7)
    
    s.set_groups(groups)
    s.set_initial_values(pre_filled)
    print(s.check_valid_grouping())
    solver = Solver(s, pre_filled)
    print(solver)
    solver.solve()
    print()
    print(solver)
    
    # 3 | 2 | 1 | 3 | 4 | 2 | 3
    # 1 | 5 | 4 | 5 | 1 | 5 | 1
    # 3 | 2 | 1 | 2 | 4 | 2 | 4
    # 5 | 4 | 5 | 3 | 1 | 3 | 1
    # 2 | 3 | 1 | 2 | 5 | 4 | 2
    # 4 | 5 | 4 | 3 | 1 | 3 | 5
    # 1 | 2 | 1 | 2 | 4 | 2 | 4
    # 3 | 5 | 4 | 5 | 1 | 5 | 3
    # 1 | 2 | 1 | 3 | 4 | 2 | 1

test5()

