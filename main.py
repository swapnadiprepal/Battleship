import json
import numpy as np
import random
import sys

class BattleshipBot:
    def __init__(self, state_file="battleship_state.json"):
        self.grid_size = 10
        self.ships = {
            "carrier": 5,
            "battleship": 4,
            "cruiser": 3,
            "submarine": 3,
            "destroyer": 2
        }
        self.state_file = state_file
        self.state = self.load_state()

    def load_state(self):
        try:
            with open(self.state_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            initial_state = {
                "hits": [],
                "misses": [],
                "targets": [],
                "sunk_ships": [],
                "possible_moves": [[x, y] for x in range(1, self.grid_size + 1) for y in range(1, self.grid_size + 1)],
                "last_move": None
            }
            self.save_state(initial_state)
            return initial_state

    def save_state(self, state=None):
        if state is None:
            state = self.state
        with open(self.state_file, "w") as f:
            json.dump(state, f)

    def update_state(self, hit_or_miss, sunk_ship):
        if self.state["last_move"] is not None:
            if hit_or_miss == "HIT":
                self.state["hits"].append(self.state["last_move"])
                self._add_adjacent_targets(self.state["last_move"])
            elif hit_or_miss == "MISS":
                self.state["misses"].append(self.state["last_move"])

        if sunk_ship != "NONE":
            self.state["sunk_ships"].append(int(sunk_ship))
            self._clear_targets()

    def _add_adjacent_targets(self, cell):
        x, y = cell
        adjacent = [
            [x-1, y], [x+1, y],
            [x, y-1], [x, y+1]
        ]
        for target in adjacent:
            if (1 <= target[0] <= self.grid_size and
                1 <= target[1] <= self.grid_size and
                target not in self.state["hits"] and
                target not in self.state["misses"] and
                target not in self.state["targets"]):
                self.state["targets"].append(target)

    def _clear_targets(self):
        self.state["targets"] = []

    def _calculate_probabilities(self):
        self.probability_grid = np.zeros((self.grid_size, self.grid_size))
        possible_moves_set = set(tuple(move) for move in self.state["possible_moves"])
        for ship, length in self.ships.items():
            if length in self.state["sunk_ships"]:
                continue
            # Horizontal placements
            for x in range(1, self.grid_size + 1):
                for y in range(1, self.grid_size - length + 2):
                    if all((x, y + i) in possible_moves_set for i in range(length)):
                        for i in range(length):
                            self.probability_grid[x - 1, y + i - 1] += 1
            # Vertical placements
            for x in range(1, self.grid_size - length + 2):
                for y in range(1, self.grid_size + 1):
                    if all((x + i, y) in possible_moves_set for i in range(length)):
                        for i in range(length):
                            self.probability_grid[x + i - 1, y - 1] += 1

    def next_move(self):
        if self.state["targets"]:
            self.state["last_move"] = self.state["targets"].pop(0)
        else:
            self._calculate_probabilities()
            max_prob = np.max(self.probability_grid)
            candidates = [(x, y) for x in range(1, self.grid_size + 1) for y in range(1, self.grid_size + 1) if self.probability_grid[x - 1, y - 1] == max_prob]
            self.state["last_move"] = random.choice(candidates)

        if list(self.state["last_move"]) in self.state["possible_moves"]:
            self.state["possible_moves"].remove(list(self.state["last_move"]))

        return self.state["last_move"]

    def play(self, hit_or_miss="NONE", sunk_ship="NONE"):
        self.update_state(hit_or_miss, sunk_ship)
        move = self.next_move()
        self.save_state()
        return move

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python battleship_bot.py <HIT/MISS/NONE> <sunk_ship_size/NONE>")
        sys.exit(1)
    
    hit_or_miss = sys.argv[1]
    sunk_ship = sys.argv[2]

    bot = BattleshipBot()
    move = bot.play(hit_or_miss, sunk_ship)
    print(f"{move[0]} {move[1]}")
