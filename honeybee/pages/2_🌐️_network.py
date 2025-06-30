import streamlit as st
import pandas as pd
from scapy.all import rdpcap, Raw
from scapy.layers.inet import IP, TCP, UDP
from io import BytesIO
from datetime import datetime, timezone
import boto3

st.set_page_config(
    page_title="HoneyBee",
    layout="wide",
    initial_sidebar_state="expanded",
)

def load_pcap_from_s3(bucket, key, aws_access_key_id=None, aws_secret_access_key=None, region_name=None):
    """Download the object and return its bytes."""
    client_kwargs = {}
    if aws_access_key_id and aws_secret_access_key:
        client_kwargs.update({
            "aws_access_key_id": aws_access_key_id,
            "aws_secret_access_key": aws_secret_access_key,
        })
    if region_name:
        client_kwargs["region_name"] = region_name

    s3 = boto3.client("s3", **client_kwargs)
    obj = s3.get_object(Bucket=bucket, Key=key)
    return obj["Body"].read()


def render_network_tab():
    st.header("Network Traffic Viewer")

    # choose between upload or S3 fetch
    TYPE_MAP = {
        ":material/upload: Upload file": "upload",
        ":material/cloud_download: Load from S3": "s3"
    }
    type_options = list(TYPE_MAP.keys())
    selected_label = st.segmented_control(
        "Load PCAP via:",
        options=type_options,
        selection_mode="single",
        key="pcap_load_type",
        default=type_options[0]
    )
    flow = TYPE_MAP.get(selected_label, "upload")


    # Upload File
    if flow == "upload":
        uploaded = st.file_uploader("Upload a PCAP file", type=["pcap", "pcapng"])
        if not uploaded:
            st.info("Please upload a PCAP to proceed.")
            return
        try:
            raw     = uploaded.read()
            packets = rdpcap(BytesIO(raw))
        except Exception as e:
            st.error(f"Could not parse uploaded PCAP: {e}")
            return

    # S3 Fetch
    else:
        with st.expander("S3 Configuration", expanded=False):
            # Try to load defaults from ~/.aws/credentials or environment
            sess = boto3.Session()
            creds = sess.get_credentials() or {}
            aws_id_def = creds.access_key or ""
            aws_secret_def = creds.secret_key or ""
            region_def = sess.region_name or ""

            bucket = st.text_input(
                "Bucket name",
                key="s3_bucket"
            )
            key = st.text_input(
                "Object key (e.g. folder/file.pcap)",
                key="s3_key"
            )
            aws_id = st.text_input(
                "AWS Access Key ID",
                type="password",
                value=aws_id_def,
                key="s3_id"
            )
            aws_secret = st.text_input(
                "AWS Secret Access Key",
                type="password",
                value=aws_secret_def,
                key="s3_secret"
            )
            region = st.text_input(
                "AWS Region (optional)",
                value=region_def,
                key="s3_region"
            )

        # only attempt load when user clicks:
        if not st.button("Load PCAP from S3", key="load_pcap_s3", use_container_width=True, icon="📥", type="primary"):
            return

        try:
            data = load_pcap_from_s3(
                bucket,
                key,
                aws_access_key_id=aws_id,
                aws_secret_access_key=aws_secret,
                region_name=region or None,
            )
            packets = rdpcap(BytesIO(data))
        except Exception as e:
            st.error(f"Failed to get PCAP from S3: {e}")
            return

    # Build records with full date and time
    records = []
    for pkt in packets:
        pkt_time = datetime.fromtimestamp(float(pkt.time), tz=timezone.utc)
        http_info = ""
        # determine protocol / HTTP first line
        if Raw in pkt:
            try:
                payload    = pkt[Raw].load.decode("utf-8", errors="ignore")
                first_line = payload.split("\r\n")[0]
                method     = first_line.split(" ")[0]
                if method in ("GET","POST","PUT","DELETE","HEAD","OPTIONS"):
                    protocol  = "http"
                    http_info = first_line
                else:
                    protocol  = "tcp" if TCP in pkt else "udp" if UDP in pkt else "ip"
            except:
                protocol = "tcp" if TCP in pkt else "udp" if UDP in pkt else "ip"
        else:
            protocol = (
                "tcp" if TCP in pkt else
                "udp" if UDP in pkt else
                "ip"  if IP  in pkt else
                "ether"
            )

        src     = pkt[IP].src if IP in pkt else "N/A"
        dst     = pkt[IP].dst if IP in pkt else "N/A"
        details = pkt.summary()

        # raw hex / ascii
        raw_bytes  = bytes(pkt)
        hex_lines   = []
        ascii_lines = []
        for i in range(0, len(raw_bytes), 32):
            chunk      = raw_bytes[i : i + 32]
            hex_lines.append(" ".join(f"{b:02x}" for b in chunk))
            ascii_lines.append("".join(chr(b) if 32 <= b <= 126 else "." for b in chunk))

        records.append({
            "time":      pkt_time,
            "protocol":  protocol,
            "src":       src,
            "dst":       dst,
            "details":   details,
            "http_info": http_info,
            "raw_hex":   "\n".join(hex_lines),
            "raw_ascii": "\n".join(ascii_lines),
        })

    df = pd.DataFrame(records)
    df["date"] = df["time"].dt.date

    # --- Filters & Pagination (unchanged) ---
    min_date, max_date = df["date"].min(), df["date"].max()
    start_date, end_date = st.date_input(
        "Date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    if isinstance(start_date, tuple):
        start_date, end_date = start_date

    filtered = df[(df["date"] >= start_date) & (df["date"] <= end_date)]

    protocols = st.multiselect(
        "Protocol filter",
        options=["ether","ip","tcp","udp","http","dns"],
        default=["ether","ip","tcp","udp","http","dns"],
    )
    filtered = filtered[filtered["protocol"].isin(protocols)]

    search = st.text_input("Search details / ASCII / Hex")
    if search:
        m1 = filtered["details"].str.contains(search, case=False, na=False)
        m2 = filtered["raw_ascii"].str.contains(search, case=False, na=False)
        m3 = filtered["raw_hex"].str.contains(search, case=False, na=False)
        filtered = filtered[m1 | m2 | m3]

    # pagination
    total    = len(filtered)
    per_page = 100
    pages    = (total // per_page) + (1 if total % per_page else 0)
    st.session_state.page = st.session_state.get("page", 1)
    if st.session_state.page > pages:
        st.session_state.page = 1

    def prev_page(): st.session_state.__setitem__("page", st.session_state.page - 1)
    def next_page(): st.session_state.__setitem__("page", st.session_state.page + 1)

    start = (st.session_state.page - 1) * per_page
    end   = min(start + per_page, total)
    st.markdown(f"Showing packets **{start+1}–{end}** of **{total}** (Page {st.session_state.page}/{pages})")

    c1, _, c3 = st.columns([1, 2, 1])
    with c1:
        st.button("← Previous", on_click=prev_page, disabled=st.session_state.page <= 1)
    with c3:
        st.button("Next →", on_click=next_page, disabled=st.session_state.page >= pages)

    local_ip = next((p[IP].src for p in packets if IP in p), None)
    for idx, row in filtered.iloc[start:end].iterrows():
        icon      = "🔵" if row["src"] == local_ip else "🟢" if row["dst"] == local_ip else ""
        time_str  = row["time"].strftime("%Y-%m-%d %H:%M:%S")
        http_label = f" | {row['http_info']}" if row["http_info"] else ""
        label     = f"[{idx}] {time_str} {icon} {row['protocol'].upper()} {row['src']} → {row['dst']}{http_label}"

        with st.expander(label):
            st.text(row["details"])
            hx, ax = st.columns(2)
            with hx:
                st.subheader("Hex")
                st.code(row["raw_hex"], language="text")
            with ax:
                st.subheader("ASCII")
                st.code(row["raw_ascii"], language="text")


if __name__ == "__main__":
    render_network_tab()
