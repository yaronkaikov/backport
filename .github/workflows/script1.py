# script1.py
import os


def generate_value():
    value = "Hello from script1"
    with open(os.getenv('GITHUB_OUTPUT'), 'a') as output_file:
        print(f"my_value={value}", file=output_file)


if __name__ == "__main__":
    generate_value()
