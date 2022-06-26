import os
from dotenv import dotenv_values


root = os.path.abspath(".")
config = dotenv_values(os.path.join(root, ".env"))
