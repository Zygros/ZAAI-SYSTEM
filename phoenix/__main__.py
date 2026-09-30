from .core.agent import PhoenixBot
import sys

def main():
    prompt = " ".join(sys.argv[1:]).strip()
    if not prompt:
        print("Phoenix Bot ready. Usage: python -m phoenix <request>")
        return
    print(PhoenixBot().run(prompt).to_json())

if __name__ == "__main__":
    main()
