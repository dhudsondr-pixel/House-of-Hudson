"""ONE-CLICK LAUNCHER.

This is the only file you ever need to run. Double-click it (or open Terminal /
Command Prompt and type 'python run.py'). It will:
  1. Install the libraries it needs (one-time, takes 30 seconds).
  2. Generate all 36 ready-to-sell Etsy listings into the 'output' folder.

You don't need to know any code. Just run this file.
"""

import subprocess
import sys
from pathlib import Path


REQUIRED = ["reportlab", "Pillow"]


def ensure_deps() -> None:
    missing = []
    for pkg in REQUIRED:
        mod = "PIL" if pkg == "Pillow" else pkg
        try:
            __import__(mod)
        except ImportError:
            missing.append(pkg)
    if not missing:
        return
    print(f"First-time setup: installing {', '.join(missing)} ...")
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "--quiet", *missing]
    )
    print("  done.\n")


def main() -> int:
    ensure_deps()
    # Late import so deps are guaranteed
    from etsy_planner_factory.cli import main as cli_main
    return cli_main(sys.argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
