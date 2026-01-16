
from collections.abc import MutableSequence

class Cell:
    def __init__(self, row, column):
        """
        Docstring for __init__
        
        :param row: the row location of the cell
        :param column: the column location of the cell
        """
        self.row = row
        self.col = column
        # Minus one means is hasnt been assigned a group yet
        self.possible_values = [-1]
        self.empty = False
    
    def set_possible_values(self, n:int):
        """
        Docstring for set_possible_values
        Use when assigning this cell to a group
        
        :param n: The number of cells in the group its been assigned to
        """
        self.possible_values = list(range(1, n+1))
        if n == 1:
            self.set_value(n)
    
    def get_possible_values(self):
        return self.possible_values

    def remove_possible_values(self, *values):
        for value in values:
            if isinstance(value, int):
                if value in self.possible_values:
                    self.possible_values.remove(value)
            else:
                raise ValueError("values must be integers")
        
        if not self.possible_values:
            raise ValueError("Tried to remove all possible values")
        
        if len(self.possible_values) == 1 and self.possible_values[0] != -1:
            self.set_value(self.possible_values[0])
        
    
    def set_value(self, value):
        self.possible_values = [value]
        self.empty = False
    
    
    def is_empty(self):
        return self.empty


class Row(MutableSequence):
    def __init__(self, row=None):
        
        if row is not None:
            self.row = list(row)
        else:
            self.row = []
    
    def __iter__(self):
        return self.row.__iter__()
        
    def __repr__(self):
        return repr(self.row)

    def __contains__(self, item):
        return item in self.row

    def __len__(self):
        return len(self.row)

    def __getitem__(self, i):
        if isinstance(i, slice):
            return self.__class__(self.row[i])
        else:
            return self.row[i]

    def __setitem__(self, i, item):
        self.row[i] = item

    def __delitem__(self, i):
        del self.row[i]

    def __copy__(self):
        inst = self.__class__.__new__(self.__class__)
        inst.__dict__.update(self.__dict__)
        # Create a copy and avoid triggering descriptors
        inst.__dict__["data"] = self.__dict__["data"][:]
        return inst

    def append(self, item):
        self.row.append(item)

    def insert(self, i, item):
        self.row.insert(i, item)

    def pop(self, i=-1):
        return self.row.pop(i)

    def remove(self, item):
        self.row.remove(item)

    def clear(self):
        self.row.clear()

    def copy(self):
        return self.__class__(self)

    def count(self, item):
        return self.row.count(item)

    def index(self, item, *args):
        return self.row.index(item, *args)


class Grid:
    def __init__(self, rows, columns):
        """
        Docstring for __init__
        Creates the Grid for the Suguru
        Always use a cell's coordinates to refer to it, not the object Cell
        
        :param rows: the number of rows
        :param columns: the number of columns
        """
        self.grid = [Row(
            [Cell(r, c) for c in range(columns)]
            ) for r in range(rows)]
        self.rows = rows
        self.cols = columns
        
    
    def __str__(self):
        s = ""
        for row in self.grid:
            s+= row.__str__() + "\n"
        
        return s[:-1]

    
    def get_cell_roi(self, cell:tuple[int, int]):
        three_by_three = [
            (r, c) for r in range(
                max(0, cell[0]-1), min(self.rows, cell[0]+2)
            ) for c in range(
                max(0, cell[1]-1), min(self.cols, cell[1]+2)
            )
        ]
        
        three_by_three.remove((cell[0], cell[1]))
        
        return three_by_three
    
    def __getitem__(self, i):
        if isinstance(i, tuple) and len(i) == 2:
            if isinstance(i[0], int) and isinstance(i[1], int):
                return self.grid[i[0]][i[1]]
        else:
            return self.grid[i]
        
        
class Group:
    def __init__(self, cells:list[tuple]):
        self.cells = cells
    
    def __iter__(self):
        return self.cells.__iter__()
    
    def get_empty_cells(self, grid:Grid)->list[tuple[int, int]]:
        empty_cells = []
        for cell in self.cells:
            if grid[cell].is_empty():
                empty_cells.append(cell)
        
        return empty_cells

    def get_overlapping_roi_cells(self, grid:Grid, cells:list[tuple[int, int]]):
        overlap = set(grid.get_cell_roi(cells[0]))
        print(overlap)
        for cell in cells[1:]:
            print(set(grid.get_cell_roi(cell)))
            overlap = overlap.intersection(set(grid.get_cell_roi(cell)))
            print(overlap)
        return overlap


class Suguru:
    def __init__(self, rows, columns):
        self.grid = Grid(rows=rows, columns=columns)
        self.groups = []
    
    def set_groups(self, groups:list[Group]|list[list[tuple[int, int]]]):
        if isinstance(groups, list):
            if isinstance(groups[0], Group):
                self.groups = groups
            elif isinstance(groups[0], list):
                self.groups = [Group(group) for group in groups]
    
    
    def get_groups(self):
        return self.groups


    def add_group(self, group:Group):
        if isinstance(group, Group):
            self.groups.append(group)
        elif isinstance(group, list):
            if sum([1-int(isinstance(x, int)) for x in range(0, len(group))])==0:
                self.groups.append(Group(group))
        else:
            raise ValueError("group should be type Group not " + type(group))
        
        
    def check_valid_grouping(self):
        g = set([(r,c) for c in range(self.grid.cols) for r in range(self.grid.rows)])
        
        s = set()
        for group in self.groups:
            s = s.union(set(group))
        
        if g == s:
            return True
        
        return False
    


# check groups
# groups = [Group([2, 4, 6]), Group([1, 8, 6])]
# s = set()
# for group in groups:
#     s = s.union(set(group))



# # check 'check_valid_grouping'
# s = Suguru(3, 3)
# gs = [Group([(0, 0), (0, 1), (0, 2)]), Group([(1, 1), (1, 2), (2, 0), (2, 1), (2, 2)])]

# s.set_groups(gs)
# print(s.check_valid_grouping())

# g = Grid(4, 2)
# print(g)
# print(g[(2, 1)])


# Example suguru


gs = [
    Group([(0, 0), (0, 1), (1, 1), (1, 2), (2, 1), (2, 2)]),
    Group([(1, 0), (2, 0)]),
    Group([(0, 2), (0, 3), (1, 3), (2, 3), (3, 3), (3, 2)]),
    Group([(3, 0), (3, 1), (4, 0), (4, 1)]),
    Group([(4, 2), (4, 3)])
]

# (0, 1) = 1
# (1, 1) = 4
# (2, 1) = 5
# (1, 2) = 3
# (0, 3) = 2
# (1, 3) = 6
# (3, 0) = 3
# (4, 1) = 1
# (3, 2) = 3


suguru = Suguru(5, 4)
suguru.set_groups(gs)
print("=", gs[1].get_overlapping_roi_cells(suguru.grid, gs[1].cells))

print(suguru.check_valid_grouping())