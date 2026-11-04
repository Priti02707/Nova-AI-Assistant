import argparse

from assistant import start_assistant


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Nova AI Assistant.")
    parser.add_argument("--text", action="store_true", help="Use the terminal instead of audio.")
    start_assistant(text_only=parser.parse_args().text)
