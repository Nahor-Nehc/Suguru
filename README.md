# Suguru Solver


## Puzzle Structure

Grid
    - a 2x2 list of the cells

Row
    - is returned when the Grid is indexed

Cell
    - is returned when the Row is indexed
    - contains a list of potential values

Group
    - stores the coordinates of the cells in its group
    - is the main area of processing for the solver

## Solver

The goal is to find the solution to a well defined suguru (a suguru with
exactly one possible solution without the need for trial and error)

We solve it by doing the following phases

Phase 1: cell value
    - For each cell that has a known value, we remove that value from the
    possible values of adjacent cells (these adjacent cells are said to be in
    its 'region of influence')
    - then remove that value from the possible values of cells in the same
    group

Phase 2: group exclusion
    - for each group in the suguru, we see if one cell contains the only
    possible location for a value, and so fill it with that value
    (now we run phase 1 on this cell)
    - then we check, for each possible value all the cells in the group can
    take, if every cell in the group which could contain that value has a cell
    in their regions of influence, remove that value from from that cell's
    possible values

to start we just run phase 1 on the initial values of the suguru, and when the 
recursion ends, we run the group exclusion phase. If the suguru is now solved
(all the cells are filled) then we are done. Otherwise, we run phase 1 on cells
that 



Optimisations?
    - have a buffer of changed cells (and groups) so we dont have to check
    every cell again individually


Baby solver ideas:
    - find largest group size, then fill every cell with a number smaller than
    that, then check the grid
    - get every permutation of values in each group and go through all of them
    then check the grid


## GUI
### GUI suguru input

User steps:
    - select size of grid
    - create groups
        - click and drag on a series of cells (use is mousedown thing on mousemove)
        - if you click on a cell already assigned a group, delete previous group
    - click on a cell to input cell values (use mouseup event only if not dragging)

    - hit 'solve'
        - show if there are some cells not in a group


### Things to display

- button to change size of grid
    - text input as well?

CHANGE SCREEN to editor
- show suguru grid
- THICK green lines to show currently selected cells
- thick black lines to show created groups
-  keep track of:
    - 


### Things to track

- size_selector

- editor
    