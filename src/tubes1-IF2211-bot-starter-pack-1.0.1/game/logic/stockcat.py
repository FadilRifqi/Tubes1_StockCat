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

        self.teleporters: Dict[str, GameObject] = {}
        self.reset_button_position = None
        self.target_after_teleport: Optional[Position] = None

    """Fungsi Mengambil Himpunan Kandidat"""

    def get_diamonds(self, board: Board) -> List[GameObject]:
        """Mengambil daftar diamond biru dan merah dari papan permainan."""
        return [d for d in board.game_objects if d.type == "DiamondGameObject"]

    def get_teleporters(self, board: Board) -> List[GameObject]:
        """Mengambil daftar teleporter dari papan permainan."""
        return [d for d in board.game_objects if d.type == "TeleportGameObject"]

    def get_reset_button(self, board: Board) -> GameObject:
        """Mengambil tombol reset dari papan permainan."""
        return [d for d in board.game_objects if d.type == "DiamondButtonGameObject"]

    """Akhir dari Fungsi Mengambil Himpunan Kandidat"""

    def next_move(self, board_bot: GameObject, board: Board) -> Tuple[int, int]:
        props = board_bot.properties
        current_position = board_bot.position

        #Jika Kantong Penuh Kembali ke Base
        if props.diamonds == 5 or self.goal_position is None:
            base = board_bot.properties.base
            # Hitung jarak ke base langsung dan via teleport
            jarak_langsung = self.get_distance_without_teleport(current_position, base)
            jarak_teleport = self.get_distance_with_teleport(current_position, base, board)
            if jarak_teleport < jarak_langsung:
                # Temukan teleporter terdekat untuk digunakan
                min_distance = float('inf')
                best_tele = None
                for pair in self.teleporters.values():
                    if len(pair) == 2:
                        for tele in pair:
                            distance = self.get_distance_without_teleport(current_position, tele.position)
                            if distance < min_distance:
                                min_distance = distance
                                best_tele = tele
                if best_tele:
                    self.goal_position = best_tele.position
                else:
                    self.goal_position = base
            else:
                self.goal_position = base
        else:
            if self.target_after_teleport:
                if current_position == self.goal_position:
                    # Sudah sampai di teleporter, sekarang arahkan ke tujuan akhir
                    self.goal_position = self.target_after_teleport
                    self.target_after_teleport = None
            # Inisialisasi Himpunan Kandidat
            diamonds = self.get_diamonds(board)
            teleporters = self.get_teleporters(board)

            self.teleporters = {}
            for tele in teleporters:
                pair_id = tele.properties.pair_id
                if pair_id not in self.teleporters:
                    self.teleporters[pair_id] = []
                self.teleporters[pair_id].append(tele)

            reset_button = self.get_reset_button(board)

            # Hitung Jarak tanpa Teleporter dan Dengan Teleporter Setiap kandidat
            candidates = []

            for diamond in diamonds:
                distance = self.get_distance_with_teleport(current_position, diamond.position,board)
                candidates.append((diamond, distance))
            for button in reset_button:
                distance = self.get_distance_with_teleport(current_position, button.position,board)
                candidates.append((button, distance))

            # Cari Kandidat dengan nilai p/w terbaik
            # p = points, w = distance
            best_candidate = None
            best_p = -1
            best_w = float('inf')
            best_density = -1
            for candidate, distance in candidates:
                if candidate.type == "DiamondGameObject":
                    p = 4 if candidate.properties.points == 1 else 6
                    if props.diamonds + candidate.properties.points > 5:
                        p = -10000
                elif candidate.type == "DiamondButtonGameObject":
                    p = 1

                w = distance
                density = p/w
                if density > best_density or (density == best_density and w < best_w):
                    best_candidate = candidate
                    best_p = p
                    best_w = w
                    best_density = density

            #  Arahkan ke kandidat terbaik
            if best_candidate is None:
                # Tidak ada kandidat yang ditemukan, tetap diam
                return 0, 0
            else:
                #TODO: Perbaiki logika teleportasi dan tanpa teleportasi
                # Tentukan apakah jarak terbaik melibatkan teleport
                direct_distance = self.get_distance_without_teleport(current_position, best_candidate.position)
                teleport_distance = self.get_distance_with_teleport(current_position, best_candidate.position, board)

                if teleport_distance < direct_distance:
                    # Temukan jalur teleportasi terbaik ke kandidat
                    min_total = float('inf')
                    for pair in self.teleporters.values():
                        if len(pair) != 2:
                            continue
                        t1, t2 = pair

                        d1 = self.get_distance_without_teleport(current_position, t1.position) + \
                            self.get_distance_without_teleport(t2.position, best_candidate.position) + 1

                        d2 = self.get_distance_without_teleport(current_position, t2.position) + \
                            self.get_distance_without_teleport(t1.position, best_candidate.position) + 1

                        if d1 < min_total:
                            self.goal_position = t1.position
                            self.target_after_teleport = best_candidate.position
                            min_total = d1
                        if d2 < min_total:
                            self.goal_position = t2.position
                            self.target_after_teleport = best_candidate.position
                            min_total = d2
                else:
                    self.goal_position = best_candidate.position
                    self.target_after_teleport = None

        delta_x, delta_y = get_direction(
            current_position.x,
            current_position.y,
            self.goal_position.x,
            self.goal_position.y,
        )

        return delta_x, delta_y



    def get_distance_without_teleport(self, pos1: Position, pos2: Position) -> int:
        """Menghitung jarak Manhattan antara dua posisi tanpa mempertimbangkan teleporter"""
        return abs(pos1.x - pos2.x) + abs(pos1.y - pos2.y)

    def get_distance_with_teleport(self, pos1: Position, pos2: Position, board: Board) -> int:
        """Menghitung jarak antara dua posisi dengan mempertimbangkan teleporter"""
        direct_distance = self.get_distance_without_teleport(pos1, pos2)

        # Jika tidak ada teleport, langsung return jarak tanpa teleport
        if not self.teleporters:
            return direct_distance

        # Inisialisasi jarak terbaik dengan jarak langsung
        best_distance = direct_distance

        # Evaluasi semua pasangan teleporter
        for pair in self.teleporters.values():
            if len(pair) != 2:
                continue  # pasangan tidak lengkap

            tele1, tele2 = pair

            # Kasus: masuk tele1, keluar di tele2
            to_tele1 = self.get_distance_without_teleport(pos1, tele1.position)
            from_tele2 = self.get_distance_without_teleport(tele2.position, pos2)
            total1 = to_tele1 + 1 + from_tele2  # "+1" adalah aksi teleport

            # Kasus: masuk tele2, keluar di tele1
            to_tele2 = self.get_distance_without_teleport(pos1, tele2.position)
            from_tele1 = self.get_distance_without_teleport(tele1.position, pos2)
            total2 = to_tele2 + 1 + from_tele1

            # Bandingkan dan simpan jarak terbaik
            best_distance = min(best_distance,total1, total2)

        return best_distance
