from simulator import Simulator
from utils import load_csv

simulator = Simulator(load_csv('data.csv'), 100, 40)
simulator.market.execute()