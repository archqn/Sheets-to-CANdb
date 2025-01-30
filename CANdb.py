import pandas as pd
import os
import cantools
from cantools.database import Database
from cantools.database.can import Node, Message, Signal



# Directories
base_dir = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(base_dir, "DBCs"), exist_ok=True)
dbc_file = os.path.join(base_dir, "DBCs", "GR25_CAN.dbc")
base_dbc = "DBCs/Base.dbc"

CANdb = cantools.database.load_file(base_dbc)

# messages = pd.read_csv("CSVs/MESSAGE_ID_TEMP.csv")

# read nodes and add to CANdb
existing_nodes = {node.name for node in CANdb.nodes}

nodes = pd.read_csv("CSVs/NODE_ID_TEMP.csv")
node_ids = nodes["Node"].dropna().unique()
for n in node_ids:
    n = n.replace(" ", "_").replace("-", "_")

    if n not in existing_nodes: 
        CANdb.nodes.append(Node(n))
        existing_nodes.add(n)

# create dbc file
with open(dbc_file, "w", encoding="utf-8") as f:
    f.write(CANdb.as_dbc_string())

print("success")