import argparse

import yaml

from TuringMachine import TuringMachine, verify_yaml_dictionary


def parse_args():
    parser = argparse.ArgumentParser(
        description="A basic YAML-defined pushdown automata"
    )

    parser.add_argument(
        "-f, --yaml",
        required=True,
        type=str,
        dest="input",
        help="The YAML file to use as the turing machine definition",
    )

    parser.add_argument(
        "-d, --debug",
        default=False,
        action=argparse.BooleanOptionalAction,
        dest="debug",
        help="Print debug messages, which includes transitions",
    )

    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    with open(args.input) as file:
        try:
            tm_def = yaml.full_load(file)
        except Exception as e:
            print(e)
            exit(1)

    try:
        machine_tuple = verify_yaml_dictionary(tm_def)
    except Exception as e:
        print(f"Error parsing YAML definition: {e}")
        exit(1)

    machine = TuringMachine(*machine_tuple, args.debug)

    # input loop on machine
    print("Use Ctrl+d or Ctrl+c to exit")
    print("Machine description: ", machine.description)
    while True:
        try:
            tapes = []
            for tape in range(machine.number_tapes):
                tapes.append(input(f"Enter Tape {tape + 1} start value: "))
            final_state, tapes = machine.run(tapes)

            print(f"Final State: `{final_state}`")
            for idx, tape in enumerate(tapes):
                print(f"Tape {idx + 1}: `{tape}`")

        except EOFError:
            print("Exiting...")
            exit(0)
        except KeyboardInterrupt:
            print("Exiting...")
            exit(0)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()
