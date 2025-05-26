import random
from typing import Optional, Tuple, Dict, List

from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position
from ..util import get_direction


class StockCat(BaseLogic):
    def __init__(self):
        self.directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        self.goal_position: Optional[Position] = None
        self.current_direction = 0
        self.teleport_pairs: Dict[str, List[GameObject]] = {}

    def next_move(self, board_bot: GameObject, board: Board) -> Tuple[int, int]:
        """ TODO: Implementasi logika greedy dengan spesifikasi
        tombol_merah:p=1,w=absolute(posisi_x_robot - posisi_x_tombol_merah) + absolute(posisi_y_robot - posisi_y_tombol_merah)
        robot_lain:p=2,w=absolute(posisi_x_robot - posisi_x_robot_lain) + absolute(posisi_y_robot - posisi_y_robot_lain)
        diamond_biru:p=3,w=absolute(posisi_x_robot - posisi_x_diamond_biru) + absolute(posisi_y_robot - posisi_y_diamond_biru)
        diamond_merah:p=4,w=absolute(posisi_x_robot - posisi_x_diamond_merah) + absolute(posisi_y_robot - posisi_y_diamond_merah)
        Jika kantong/inventori penuh, maka robot akan menuju base
        robot bisa teleport jika ada teleport yang tersedia, jika ada teleport yang tersedia maka jarak yang ditempuh menuju diamond bisa lebih pendek
        Jika robot lain berada di posisi yang sama, maka robot akan tackle robot lain tersebut
        """
        return None
