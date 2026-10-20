from pathlib import Path

from src.pipeline import run_pipeline


def main() -> None:
    root = Path(__file__).resolve().parent
    report = run_pipeline(project_root=root)
    print("CP1 pipeline finished.")
    print(f"Quality report: {report}")


if __name__ == "__main__":
    main()
