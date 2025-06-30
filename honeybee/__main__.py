import os
import runpy
import sys

import honeybee


def main() -> None:
    streamlit_script_path = os.path.join(os.path.dirname(honeybee.__file__), "1_🐝_app.py")
    args = sys.argv[1:]
    sys.argv = ["streamlit", "run", streamlit_script_path, *args]
    runpy.run_module("streamlit", run_name="__main__")


if __name__ == "__main__":
    main()
