import signal
import shutil
import subprocess


import streamlit as st
from pathlib import Path
from tempfile import mkdtemp


def check_docker_compose_installed():
    try:
        process = subprocess.run(
            ["docker", "compose", "ls"], stdout=subprocess.PIPE, check=False
        )
    except Exception:
        return False
    # Check normal output of docker compose to make sure it is properly installed.
    return process.returncode == 0 and process.stdout.startswith(b"NAME")


def stop_current_local_deploy(process, tmpdir):
    process.send_signal(signal.SIGINT)
    full_output = st.session_state.get("deploy_process_output", [])
    if full_output is None:
        full_output = []
    # Get the final lines of output...
    for line in iter(process.stdout.readline, ""):
        if not line:
            break
        if line != b"\n":
            full_output.append(line.decode("utf-8").rstrip("\n"))

    process = subprocess.Popen(
        [
            "docker",
            "compose",
            "down",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=tmpdir,
    )
    # Get the output from `docker compose down`
    for line in iter(process.stdout.readline, ""):
        if not line:
            break
        if line != b"\n":
            full_output.append(line.decode("utf-8").rstrip("\n"))

    st.session_state["deploy_process_output"] = full_output
    shutil.rmtree(tmpdir)


def local_deploy_compose(docker_compose):
    ## TODO: Add a cleanup function that cleans-up stray honeybee- folders in-case the server crashed.
    tmpdir = Path(mkdtemp(prefix="honeybee-"))
    tmpdir.joinpath("docker-compose.yaml").write_text(docker_compose)
    full_output = []
    process = subprocess.Popen(
        [
            "docker",
            "compose",
            "up",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=tmpdir,
    )

    code_container = st.container()
    st.button(
        "🛑 Stop Local Deploy",
        on_click=stop_current_local_deploy,
        args=(process, tmpdir),
        use_container_width=True,
        type="secondary",
    )
    with code_container.empty():
        for line in iter(process.stdout.readline, ""):
            if not line:
                break
            if line != b"\n":
                full_output.append(line.decode("utf-8").rstrip("\n"))
                st.code(
                    "\n".join(full_output),
                    height=400,
                    line_numbers=True,
                    wrap_lines=True,
                )
            st.session_state["deploy_process_output"] = full_output

    # If we leave this loop it means the local deploy failed or existed.
    st.session_state.pop("deploy_process_output")
