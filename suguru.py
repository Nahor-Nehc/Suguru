
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
    
    def set_possible_values(self, n):
        """
        Docstring for assign_group
        
        :param n: The number of cells in the group its been assigned to
        """
        self.possible_values = list(range(1, n+1))
    
    def get_possible_values(self):
        return self.possible_values
    
    def is_empty(self):
        if len(self.possible_values) == 1 and self.possible_values[0] != -1:
            return True
        return False


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

    
    def get_cell_roi(self, cell:tuple):
        return [
            (r, c) for r in range(
                max(0, cell[0]-1), min(self.rows, cell[0]+1)
            ) for c in range(
                max(0, cell[1]-1), min(self.cols, cell[1]+1)
            )
        ]
    
    def __getitem__(self, i):
        if isinstance(i, slice):
            pass
        else:
            return self.grid[i]
        
        
class Group:
    def __init__(self, cells:list[tuple]):
        
        self.cells = cells
    
    def __iter__(self):
        return self.cells.__iter__()
    
    def get_empty_cells(self):
        pass

    def get_overlapping_roi_cells(self):
        pass


class Suguru:
    def __init__(self, rows, columns):
        self.grid = Grid(rows=rows, columns=columns)
        self.groups = []
    
    def set_groups(self, groups:list[Group]):
        self.groups = groups
    
    
    def get_groups(self):
        return self.groups


    def add_groups(self, group:Group):
        if isinstance(group, Group):
            self.groups.append(group)
        elif isinstance(group, list):
            if sum([1-int(isinstance(x, int)) for x in range(0, len(group))])==0:
                self.groups.append(Group(group))
        
        
    def check_valid_grouping(self):
        g = set([(r,c) for c in range(self.grid.cols) for r in range(self.grid.rows)])
        
        s = set()
        for group in self.groups:
            s = s.union(set(group))
        
        if g == s:
            return True
        
        return False


# groups = [Group([2, 4, 6]), Group([1, 8, 6])]
# s = set()
# for group in groups:
#     s = s.union(set(group))

# # check 'check_valid_grouping'
# s = Suguru(3, 3)
# gs = [Group([(0, 0), (0, 1), (0, 2)]), Group([(1, 1), (1, 2), (2, 0), (2, 1), (2, 2)])]

# s.set_groups(gs)
# print(s.check_valid_grouping())

