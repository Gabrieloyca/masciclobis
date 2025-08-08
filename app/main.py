"""Entry point for the Streamlit app.

Running this module with `streamlit run app/main.py` will launch the
web application defined in :mod:`app.ui`. It simply delegates to the
`run` function to build the UI.
"""

from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import ui



def main() -> None:
    ui.run()


if __name__ == "__main__":
    main()
