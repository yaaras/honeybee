import os
import time
import json
import streamlit as st
from pathlib import Path


HISTORY_PATH = Path(".qhistory")


def save_query(type, input_parameters, output):
    query_time = time.time()
    data = {"type": type, "input_parameters": input_parameters, "output": output}
    HISTORY_PATH.joinpath(f"{query_time}.json").write_text(json.dumps(data))
