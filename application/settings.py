import os
from dotenv import dotenv_values


root = os.path.realpath(".")
config_file = os.path.join(root, ".env")
config = dotenv_values(config_file)
