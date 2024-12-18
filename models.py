import random
from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from calculate_pitch_outcome import calculate_pitch_outcome as cpo
from agents import PitcherAgent, PositionPlayerAgent

class BaseballGame(Model):
    """
    Two-team simplified baseball model.
    """

    def __init__(self, width=10, height=10, n_fielders_per_team=8, innings=9):
        super().__init__()
        self.width = width
        self.height = height
        self.grid = MultiGrid(width, height, torus=False)
        self.schedule = RandomActivation(self)
        self.innings_to_play = innings
        self.current_pitch_count = 0

        # Team A
        self.pitcher_A = PitcherAgent(self.next_id(), self, team="A", skill=0.75)
        self.schedule.add(self.pitcher_A)
        self.grid.place_agent(self.pitcher_A, (width // 2, height // 2))

        self.fielders_A = []
        for _ in range(n_fielders_per_team):
            fielder = PositionPlayerAgent(self.next_id(), self, team="A", role="fielder", skill=0.5)
            self.fielders_A.append(fielder)
            self.schedule.add(fielder)
            x = random.randint(0, width-1)
            y = random.randint(0, height-1)
            self.grid.place_agent(fielder, (x, y))

        # Team B
        self.pitcher_B = PitcherAgent(self.next_id(), self, team="B", skill=0.75)
        self.schedule.add(self.pitcher_B)
        self.grid.place_agent(self.pitcher_B, (width // 2, height // 2 - 1))

        self.fielders_B = []
        for _ in range(n_fielders_per_team):
            fielder = PositionPlayerAgent(self.next_id(), self, team="B", role="fielder", skill=0.5)
            self.fielders_B.append(fielder)
            self.schedule.add(fielder)
            x = random.randint(0, width-1)
            y = random.randint(0, height-1)
            self.grid.place_agent(fielder, (x, y))

        # Lineups
        self.lineup_A = [PositionPlayerAgent(self.next_id(), self, team="A", role="batter", skill=0.5)
                          for _ in range(4)]
        for batter in self.lineup_A:
            self.schedule.add(batter)
            self.grid.place_agent(batter, (width // 2, height - 1))

        self.lineup_B = [PositionPlayerAgent(self.next_id(), self, team="B", role="batter", skill=0.5)
                          for _ in range(4)]
        for batter in self.lineup_B:
            self.schedule.add(batter)
            self.grid.place_agent(batter, (width // 2, 0))

        # Game state
        self.current_inning = 1
        self.half = "top"  # "top" = Team A batting, Team B fielding
        self.outs = 0
        self.bases = [False, False, False]
        self.score = {"A": 0, "B": 0}

        self.balls = 0
        self.strikes = 0

        # Current batter indices
        self.current_batter_idx_A = 0
        self.current_batter_idx_B = 0

        self.running = True

    def step(self):
        if self.current_inning > self.innings_to_play:
            print("Game over!")
            print("Final Score:", self.score)
            self.running = False
            return

        print(f"\n=== Inning {self.current_inning} {self.half.upper()} | Score: A {self.score['A']} - B {self.score['B']} | Outs: {self.outs} ===")

        self.play_half_inning_pitch()
        self.schedule.step()

        if self.outs >= 3:
            self.change_sides()

    def play_half_inning_pitch(self):
        """Simulates a single pitch in the current half inning."""
        if self.half == "top":
            batting_team = "A"
            pitching_team = "B"
            batter = self.lineup_A[self.current_batter_idx_A]
            pitcher = self.pitcher_B
        else:
            batting_team = "B"
            pitching_team = "A"
            batter = self.lineup_B[self.current_batter_idx_B]
            pitcher = self.pitcher_A

        # Simulate the outcome of a pitch
        edge_pos = "Pitcher" if random.random() > 0.5 else "Batter"  # Simplified logic for edge
        margin = 20  # Example margin for redo pitch
        redo_pitch_loops = 0

        pitch_result = cpo(
            self.current_pitch_count + 1, False, edge_pos, margin, redo_pitch_loops
        )

        print(f"Pitch outcome: {pitch_result}")

        if pitch_result == "Ball":
            self.balls += 1
            if self.balls >= 4:
                print("Walk! Batter advances to first.")
                self.advance_runners(walk=True)
                self.reset_at_bat(batting_team)
        elif pitch_result == "Strike" or pitch_result == "Swinging Strike":
            self.strikes += 1
            if self.strikes >= 3:
                print("Strikeout! Batter is out.")
                self.outs += 1
                self.reset_at_bat(batting_team)
        elif pitch_result == "Foul":
            if self.strikes < 2:
                self.strikes += 1
        elif pitch_result == "Ball_in_play":
            self.ball_in_play(pitching_team, batting_team)
        else:
            print("Unknown pitch outcome. Skipping...")

    def ball_in_play(self, pitching_team, batting_team):
        """Handle the ball being put into play."""
        # Simplified handling for hits and outs
        if random.random() < 0.3:  # 30% chance of a fielding out
            print("Ball caught! Out recorded.")
            self.outs += 1
        else:
            print("Base hit! Runners advance.")
            self.advance_runners(hit=True)

    def advance_runners(self, walk=False, hit=False):
        if walk:
            if self.bases[2]:
                self.score[self.batting_team()] += 1
            self.bases[2] = self.bases[1]
            self.bases[1] = self.bases[0]
            self.bases[0] = True
        elif hit:
            if self.bases[2]:
                self.score[self.batting_team()] += 1
            self.bases[2] = self.bases[1]
            self.bases[1] = self.bases[0]
            self.bases[0] = True

        print(f"Bases: {self.bases}, Score: A {self.score['A']} - B {self.score['B']}")

    def reset_at_bat(self, batting_team):
        self.balls = 0
        self.strikes = 0
        if batting_team == "A":
            self.current_batter_idx_A = (self.current_batter_idx_A + 1) % len(self.lineup_A)
        else:
            self.current_batter_idx_B = (self.current_batter_idx_B + 1) % len(self.lineup_B)

    def change_sides(self):
        print(f"3 Outs! End of the {self.half} half of Inning {self.current_inning}.")
        self.outs = 0
        self.bases = [False, False, False]
        self.balls = 0
        self.strikes = 0

        if self.half == "top":
            self.half = "bottom"
        else:
            self.half = "top"
            self.current_inning += 1

    def batting_team(self):
        return "A" if self.half == "top" else "B"

    @staticmethod
    def agent_portrayal(agent):
        if isinstance(agent, PitcherAgent):
            color = "red" if agent.team == "A" else "blue"
            return {"Shape": "circle", "Color": color, "Layer": 1, "r": 0.5}
        elif isinstance(agent, PositionPlayerAgent):
            if agent.role == "batter":
                color = "orange" if agent.team == "A" else "purple"
            else:
                color = "green" if agent.team == "A" else "yellow"
            return {"Shape": "circle", "Color": color, "Layer": 1, "r": 0.5}