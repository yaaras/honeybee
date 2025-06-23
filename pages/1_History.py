import time
import json
import streamlit as st
from pathlib import Path

# adjust import path if needed
from src.query_history import load_history

# Page configuration
st.set_page_config(
    page_title="History",
    page_icon=":bookmark_tabs:",
    layout="wide",
)

st.title("🕘 HoneyBee – Query History")

HISTORY_PATH = Path(".qhistory")

# Load history data
history_data = load_history()

# icon mapping per type
ICON_MAP = {
    "Dockerfile": "🐳",
    "Docker Compose": "📦",
    "Nuclei": "⚛️",
}

if not history_data:
    st.info("No history entries found.")
else:
    # Sort entries by timestamp descending
    for ts_str, entry in sorted(history_data.items(), key=lambda x: float(x[0]), reverse=True):
        timestamp = time.ctime(float(ts_str))
        qtype = entry.get("type")
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
