from agentverse.agentverse import AgentVerse
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("--task", type=str, default="db_diag")

args = parser.parse_args()
agentverse = AgentVerse.from_task(args.task)
agentverse.run()
