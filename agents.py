# agents.py
import random
from mesa import Agent

class PitcherAgent(Agent):
    """Pitcher for a team."""
    def __init__(self, unique_id, model, team, skill=0.7):
        super().__init__(unique_id, model)
        self.team = team  # 'A' or 'B'
        self.skill = skill

    def step(self):
        # Pitchers don't act independently per step in this simplified model.
        pass

    def throw_pitch(self):
        # Skill influences likelihood of a strike
        return "strike" if random.random() < self.skill else "ball"


class PositionPlayerAgent(Agent):
    """Batter/Fielder for a team."""
    def __init__(self, unique_id, model, team, role="fielder", skill=0.5):
        super().__init__(unique_id, model)
        self.team = team  # 'A' or 'B'
        self.role = role  # 'batter' or 'fielder'
        self.skill = skill

    def step(self):
        # Position players don't have independent actions here.
        pass

    def attempt_hit(self):
        """Batter tries to hit a strike."""
        return random.random() < self.skill

    def attempt_catch(self):
        """Fielder tries to catch a hit ball."""
        return random.random() < self.skill