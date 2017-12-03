"""
Controls the user-facing API.
"""

# All the objects for the user API.
from mmSolver._api.camera import Camera
from mmSolver._api.bundle import Bundle
from mmSolver._api.marker import Marker
from mmSolver._api.attribute import Attribute
from mmSolver._api.collection import Collection
from mmSolver._api.frame import Frame
from mmSolver._api.solver import (
    Solver,
    SOLVER_TYPE_LEVMAR,
    SOLVER_TYPE_SPLM
)
from mmSolver._api.solveresult import SolveResult

# Utility functions that the user is allowed to use.
from mmSolver._api.utils import (
    detect_object_type,
    undo_chunk
)

__all__ = [
    'Camera',
    'Bundle',
    'Marker',
    'Attribute',
    'Collection',
    'Frame',
    'Solver',
    'SOLVER_TYPE_LEVMAR',
    'SOLVER_TYPE_SPLM',
    'SolveResult',
    'detect_object_type',
    'undo_chunk',
]
