from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from models import BaseballGame

def run_server():
    grid = CanvasGrid(BaseballGame.agent_portrayal, 10, 10, 500, 500)
    server = ModularServer(BaseballGame, [grid], "Two-Team Baseball Simulation")
    server.port = 8521
    server.launch()

if __name__ == "__main__":
    # If you want to run the visualization server:
    run_server()

    # If you prefer running the simulation in CLI mode:
    model = BaseballGame()
    while model.running:
        model.step()