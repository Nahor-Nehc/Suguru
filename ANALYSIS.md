# Over-Constraint Analysis for test4()

## Problem Summary
Cell (2, 6) becomes over-constrained during `group_exclusion()` phase with the following state:
- **Cell position**: (2, 6)
- **Possible values before removal**: {3, 5}
- **Values already in group**: {1, 3, 4, 5}
- **Group**: [(2, 6), (3, 6), (4, 6), (4, 5), (3, 5)] - size 5, so valid values are 1-5

## Root Cause Analysis

When `group_exclusion()` tries to remove all values {1, 3, 4, 5} from cell (2,6)'s possible values {3, 5}, it would leave the cell with no valid values.

### Why does cell (2,6) only have {3, 5} as possibilities?

This happens through **Phase 1 (adjacent_cell_exclusion)** which removes values based on row/column ROI (Region of Influence):
- Adjacent filled cells have constrained (2,6) to only {3, 5}
- But the group that (2,6) belongs to already contains values {1, 3, 4, 5}
- This creates an impossible situation

## Possible Explanations

1. **Invalid Puzzle**: The test case puzzle might be genuinely unsolvable
2. **Over-aggressive Adjacency Constraint**: Phase 1 might be removing too many possibilities
3. **Wrong ROI Calculation**: The region of influence might be incorrectly identifying which cells affect each other
4. **Phase Ordering Issue**: Phase 1 fills cells before Phase 2 can properly constrain them

## Current Fix

Modified `group_exclusion()` to:
- Detect when a cell would become over-constrained
- Skip the removal for that cell instead of crashing
- Print a warning
- Continue with the solve

This prevents crashes but the resulting solution may be invalid.

## Recommended Next Steps

1. **Verify the puzzle is valid** - check if test4() grouping and initial values are correct
2. **Add puzzle validation** - ensure no contradictions exist before solving
3. **Trace adjacency logic** - verify Phase 1 is correctly identifying constraint cells
4. **Consider using constraint backtracking** - if a cell becomes impossible, backtrack to try different values
