import pandas as pd
import os
import re
import cantools
from cantools.database import Database
from cantools.database.can import Node, Message, Signal


# Directories
base_dir = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(base_dir, "DBCs"), exist_ok=True)
dbc_file = os.path.join(base_dir, "DBCs", "SIGNALS_GR25_CAN.dbc")
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




# ------------------------- SIGNALS -------------------------
def addSignals(CANdb, signal_csv="CSVs/SIGNALS.csv"):
    signals = pd.read_csv(signal_csv)
    
    existing_signals = {
        (msg.name, signal.name): signal for msg in CANdb.messages for signal in msg.signals
    }

    for _, row in signals.iterrows():
        # Normalize and replace spaces/dashes in the signal name
        signal_name = re.sub(r'[^a-zA-Z0-9]', '_', row["Signal Name"])
        message_name = row["Message Name"].replace(" ", "_").replace("-", "_")

        # Signal parameters
        bit_start = int(row["Bit Start"])
        signal_length = int(row["Signal Length"])
        byte_order = row["Byte Order"].lower()
        # print(byte_order)
        is_signed = bool(row["Signed"])

        # Optional parameters
        minimum = row["Min"] if not pd.isna(row["Min"]) else None
        maximum = row["Max"] if not pd.isna(row["Max"]) else None
        unit = row["Unit"] if not pd.isna(row["Unit"]) else ""
        comment = row["Comment"] if not pd.isna(row["Comment"]) else ""

        # Find the message to which this signal belongs
        target_message = next((msg for msg in CANdb.messages if msg.name == message_name), None)

        if target_message and (message_name, signal_name) not in existing_signals:
            # Create a new Signal object
            signal = Signal(
                name=signal_name,
                start=bit_start,
                length=signal_length,
                byte_order=byte_order,
                is_signed=is_signed,
                minimum=minimum,
                maximum=maximum,
                unit=unit,
                comment=comment,
            )

            # Add the signal to the target message
            target_message.signals.append(signal)
            existing_signals[(message_name, signal_name)] = signal

    return





if __name__ == "__main__":
    CANdb = cantools.database.load_file(base_dbc)
    addNodes(CANdb)
    addMessages(CANdb)
    addSignals(CANdb)

    # CANdb = cantools.database.load_file(dbc_file)


    with open(dbc_file, "w", encoding="utf-8") as f:
        f.write(CANdb.as_dbc_string())


    # MUST MANUALLY CONVERT LINES 215, 217, 1300, 1302 (SIGNALS CANT BEGIN WITH NUMBERS)

    print("success")