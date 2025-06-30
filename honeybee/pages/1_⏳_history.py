import time
import json
import streamlit as st
from pathlib import Path
from datetime import datetime, date, timedelta

from src.query_history import load_history

# Page configuration
st.set_page_config(
    page_title="History",
    page_icon=":bee:",
    layout="wide",
)

st.title(":hourglass_flowing_sand: Query History")

HISTORY_PATH = Path(".qhistory")

# Load history data
history_data = load_history()

# icon mapping per type
ICON_MAP = {
    "Dockerfile": "🐳",
    "Docker Compose": "📦",
    "Nuclei": "⚛️",
}
# reverse map for filter
TYPE_MAP = {f"{icon} {typ}": typ for typ, icon in ICON_MAP.items()}

# --- Filters ---
col1, col2, col3 = st.columns([2, 2, 2])
with col1:
    # multi-select via segmented_control with persistent state
    type_options = list(TYPE_MAP.keys())
    selected_labels = st.segmented_control(
        "Filter by type:",
        options=type_options,
        selection_mode="multi",
        key="history_type_filter",
        default=type_options
    ) or []
    # map back to qtype values
    selected_types = [TYPE_MAP[label] for label in selected_labels]
with col2:
    # search filter
    search_query = st.text_input(
        "Search history:",
        key="history_search",
    )
with col3:
    # default to last two days
    default_end = date.today()
    default_start = default_end - timedelta(days=2)
    date_values = st.date_input(
        "Date range:",
        value=(default_start, default_end),
        key="history_date_filter",
    )
    # handle single vs tuple return
    if isinstance(date_values, tuple):
        start_date, end_date = date_values
    else:
        start_date = date_values
        end_date = date_values
    # ensure ordering
    if start_date > end_date:
        start_date, end_date = end_date, start_date

if not history_data:
    st.info("No history entries found.")
else:
    # Sort entries by timestamp descending
    for ts_str, entry in sorted(history_data.items(), key=lambda x: float(x[0]), reverse=True):
        ts = float(ts_str)
        entry_date = datetime.fromtimestamp(ts).date()
        qtype = entry.get("type")
        # apply filters
        if selected_types and qtype not in selected_types:
            continue
        if not (start_date <= entry_date <= end_date):
            continue

        timestamp = time.ctime(ts)
        tech, misconfigs = entry.get("input_parameters", [None, None])
        # Build base label: include type, application, and misconfigs if present
        if tech:
            mis_label = f" ({', '.join(misconfigs)})" if isinstance(misconfigs, list) and misconfigs else ""
            base_label = f"{qtype} | {tech}{mis_label} — {timestamp}"
        else:
            base_label = f"{qtype} — {timestamp}"
        # prepend icon
        icon = ICON_MAP.get(qtype, "📄")
        label = f"{icon} {base_label}"
        # apply search filter
        if search_query and search_query.lower() not in label.lower():
            continue

        # Wrap each entry in an expander
        with st.expander(label=label, expanded=False):
            st.write(f"**Type:** {qtype}")
            if tech:
                st.write(f"**Application:** {tech}")
            if isinstance(misconfigs, list) and misconfigs:
                st.write(f"**Misconfigurations:** {misconfigs}")

            output = entry.get("output")
            # Dockerfile / Docker Compose entries
            if qtype in ("Dockerfile", "Docker Compose"):
                st.write(f"**Generated {qtype} files:**")
                cols = st.columns(2)
                for item in output:
                    file_type = item.get("file_type", "text").lower()
                    caption = f"{item.get('file_path','')}/{item.get('file_name','')}"
                    if file_type == "markdown":
                        cols[1].markdown(f"**{item.get('file_name')}**")
                        cols[1].markdown(item.get('file_content',''), unsafe_allow_html=False)
                    else:
                        cols[0].caption(caption)
                        lang = "yaml" if file_type == "yaml" else "docker"
                        cols[0].code(item.get('file_content',''), language=lang)

            # Nuclei entries: always render as YAML
            elif qtype == "Nuclei":
                st.write("**Generated Nuclei template:**")
                # If output is a list of files, iterate, else treat as raw YAML
                if isinstance(output, list):
                    cols = st.columns(2)
                    for item in output:
                        caption = f"{item.get('file_path','')}/{item.get('file_name','')}"
                        cols[0].caption(caption)
                        cols[0].code(item.get('file_content',''), language="yaml")
                else:
                    st.code(output, language="yaml")

            # Other output types
            else:
                st.write("**Output:**")
                st.json(output)

            st.markdown("<br>", unsafe_allow_html=True)
