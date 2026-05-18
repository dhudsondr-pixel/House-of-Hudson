"""ONE-CLICK LAUNCHER.

This is the only file you ever need to run. Double-click it (or open Terminal /
Command Prompt and type 'python run.py'). It will:
  1. Install the libraries it needs (one-time, takes 30 seconds).
  2. Ask you which factory you want to run (planners or wedding stationery).
  3. Generate ready-to-sell Etsy listings into a folder.

You don't need to know any code. Just run this file.

Skip the menu with:   python run.py planners       (or)   python run.py wedding
"""

import subprocess
import sys


REQUIRED = ["reportlab", "Pillow", "pypdfium2"]
MODULE_NAMES = {"Pillow": "PIL"}


def ensure_deps() -> None:
    missing = []
    for pkg in REQUIRED:
        mod = MODULE_NAMES.get(pkg, pkg)
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


def choose_factory() -> str:
    print()
    print("Which would you like to generate?")
    print("  1. Etsy printable planners  (daily / weekly / habit tracker / etc.)")
    print("  2. Etsy wedding stationery  (save the date / invite / RSVP / etc.)")
    print()
    while True:
        raw = input("Enter 1 or 2: ").strip().lower()
        if raw in ("1", "planner", "planners"):
            return "planners"
        if raw in ("2", "wedding", "stationery"):
            return "wedding"
        print("  (please type 1 or 2)")


def main() -> int:
    ensure_deps()

    # Sub-CLI override: python run.py planners --count 10
    forwarded = sys.argv[1:]
    choice = None
    if forwarded and forwarded[0] in ("planners", "wedding"):
        choice = forwarded[0]
        forwarded = forwarded[1:]
    else:
        choice = choose_factory()

    if choice == "planners":
        from etsy_planner_factory.cli import main as cli_main
    else:
        from wedding_stationery_factory.cli import main as cli_main
    return cli_main(forwarded)


if __name__ == "__main__":
    raise SystemExit(main())
