# script2.py
import sys


def use_value(value):
    print(f"Received value from script1: {value}")


if __name__ == "__main__":
    value_from_script1 = sys.argv[1]  # Get the passed argument
    use_value(value_from_script1)
