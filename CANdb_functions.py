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

# ------------------------- NODES -------------------------
def addNodes(CANdb, node_csv="CSVs/NODES.csv"):
    existing_nodes = {node.name for node in CANdb.nodes}

    nodes = pd.read_csv(node_csv)
    node_ids = nodes["Node"].dropna().unique()
    for n in node_ids:
        n = n.replace(" ", "_").replace("-", "_")

        if n not in existing_nodes: 
            CANdb.nodes.append(Node(n))
            existing_nodes.add(n)
    return


# ------------------------- MESSAGES -------------------------
def addMessages(CANdb, message_csv="CSVs/MESSAGES.csv"):
    messages = pd.read_csv(message_csv)

    existing_messages = {msg.frame_id for msg in CANdb.messages}  
        
    for _, row in messages.iterrows():
        can_id = int(row["MSG ID"], 16) 
        message_name = row["Message Name"].replace(" ", "_").replace("-", "_")
        dlc = int(row["Length"])
        sender = row["Sender"]
        
        if can_id not in existing_messages:
            message = Message(
                frame_id=can_id,  
                name=message_name,
                length=dlc,  
                signals=[],  
                senders=[sender]
            )

            CANdb.messages.append(message)
            existing_messages.add(can_id)
    return




if __name__ == "__main__":
    CANdb = cantools.database.load_file(base_dbc)
    addNodes(CANdb, node_csv="CSVs/NODES.csv")
    
    # CANdb = cantools.database.load_file(dbc_file)


    addMessages(CANdb)
    with open(dbc_file, "w", encoding="utf-8") as f:
        f.write(CANdb.as_dbc_string())

    print("success")