
from collections.abc import MutableSequence

class Cell:
    def __init__(self):
        """
        Docstring for __init__
        """

        self.reset()
    
    
    def reset(self):
        # Minus one means is hasnt been assigned a group yet
        self.possible_values = [-1]
        self.empty = True
    
    def __str__(self):
        simple = True
        e = " "
        if not simple:
            e = str(list(self.get_possible_values()))
        return str(self.get_value()) if not self.is_empty() else e
    
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
            
    
    def could_be(self, value):
        return True if value in self.possible_values else False
        
    
    def set_value(self, value):
        self.possible_values = [value]
        self.empty = False
    
    
    def get_value(self):
        if self.empty or self.possible_values == [-1]:
            return None
        return self.possible_values[0]
    
    
    def is_empty(self):
        return self.empty


class Row(MutableSequence):
    def __init__(self, row=None):
        
        if row is not None:
            self.row = list(row)
        else:
            self.row = []
    
    def __str__(self):
         return " | ".join([cell.__str__() for cell in self.row])
    
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
            [Cell() for c in range(columns)]
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
    
    def __getitem__(self, i)->Cell|Row:
        if isinstance(i, tuple) and len(i) == 2:
            if isinstance(i[0], int) and isinstance(i[1], int):
                return self.grid[i[0]][i[1]]
        else:
            # if i >= self.rows:
            #     raise ValueError(i, "is out of range")
            return self.grid[i]
        
        
class Group:
    def __init__(self, cells:list[tuple], grid:Grid):
        self.cells = cells
        self.grid = grid
        for cell in cells:
            grid[cell].set_possible_values(len(cells))
    
    def __iter__(self):
        return self.cells.__iter__()
    
    def __str__(self):
        return str([self.grid[cell] .__str__() for cell in self.cells])
    
    def __contains__(self, value):
        return self.cells.__contains__(value)
    
    def get_empty_cells(self)->list[tuple[int, int]]:
        empty_cells = []
        for cell in self.cells:
            if self.grid[cell].is_empty():
                empty_cells.append(cell)
        
        return empty_cells
    
    def get_filled_cells_values(self)->set[int]:
        # print("getting filled cells values")
        filled_cells_values = set()
        for cell in self.cells:
            if not self.grid[cell].is_empty():
                filled_cells_values.add(self.grid[cell].get_value())
            
        return filled_cells_values

    
    def get_possible_values_of_empty_cells(self)->set[int]:
        possible_values = set()
        for cell in self.cells:
            if self.grid[cell].is_empty():
                possible_values = possible_values.union(
                    set(self.grid[cell].get_possible_values()))
        
        return possible_values
        

    def get_overlapping_roi_cells(self, cells:list[tuple[int, int]]):
        if not cells:
            return set()
        overlap = set(self.grid.get_cell_roi(cells[0]))
        for cell in cells[1:]:
            overlap = overlap.intersection(set(self.grid.get_cell_roi(cell)))
        return overlap

    def delete(self):
        for cell in self.cells:
            self.grid[cell].reset()
        self.cells = None
        self.grid = None


class Suguru:
    def __init__(self):
        self.initialised = False
    
    def init(self, rows, columns):
        self.initialised = True
        self.grid = Grid(rows=rows, columns=columns)
        self.groups:list[Group] = []
    
    def __str__(self):
        if not self.initialised:
            raise RuntimeError("This suguru is not yet initialised")
        
        string = ""
        for row in self.grid:
            string += row.__str__() + "\n"
        
        return string
    
    
    def set_groups(self, groups:list[Group]|list[list[tuple[int, int]]]):
        if not self.initialised:
            raise RuntimeError("This suguru is not yet initialised")
        
        if isinstance(groups, list):
            if isinstance(groups[0], Group):
                self.groups = groups
            elif isinstance(groups[0], list):
                self.groups = [Group(group, grid=self.grid) for group in groups]
    
    
    def get_groups(self):
        if not self.initialised:
            raise RuntimeError("This suguru is not yet initialised")
        
        return self.groups


    def add_group(self, group:Group):
        if not self.initialised:
            raise RuntimeError("This suguru is not yet initialised")
        
        if isinstance(group, Group):
            self.groups.append(group)
        elif isinstance(group, list):
            if sum([1-int(isinstance(x, int)) for x in range(0, len(group))])==0:
                self.groups.append(Group(group))
        else:
            raise ValueError("group should be type Group not " + type(group))
        
        
    def check_valid_grouping(self):
        if not self.initialised:
            raise RuntimeError("This suguru is not yet initialised")
        
        g = set([(r,c) for c in range(self.grid.cols) for r in range(self.grid.rows)])
        
        s = set()
        for group in self.groups:
            s = s.union(set(group))
        
        if g == s:
            return True
        
        return False
    
    def set_initial_values(self, initial_values):
        if not self.initialised:
            raise RuntimeError("This suguru is not yet initialised")
        
        for key, value in initial_values.items():
            self.grid[key].set_value(value)
    
    
