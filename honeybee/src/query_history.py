import os
import time
import json
import streamlit as st
from pathlib import Path


HISTORY_PATH = Path(__file__).parent.joinpath(".qhistory")

# check if the history directory exists, if not create it
if not HISTORY_PATH.exists():
    HISTORY_PATH.mkdir(parents=True, exist_ok=True)


def save_query(type, input_parameters, output):
    query_time = time.time()
    data = {"type": type, "input_parameters": input_parameters, "output": output}
    HISTORY_PATH.joinpath(f"{query_time}.json").write_text(json.dumps(data))


def load_history():
    query_files = HISTORY_PATH.glob("*.json")
    return {q.with_suffix("").name: json.loads(q.read_text()) for q in query_files}
