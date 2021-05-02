from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Set, Tuple, Union

import yaml


class TapeDirection(Enum):
    LEFT = "L"
    RIGHT = "R"


@dataclass
class TransitionFunction:
    destination: str
    write_alpha: str
    direction: TapeDirection


def verify_yaml_dictionary(
    input: Dict,
) -> Tuple[
    Set[str],
    str,
    Set[str],
    Set[str],
    Set[str],
    Dict[str, Dict[str, TransitionFunction]],
]:
    states = input.get("states")
    if states is None:
        raise ValueError("`states` cannot be empty")
    if not isinstance(states, List[str]):
        raise TypeError("`states` is not a list of strings")

    initial_state = input.get("initial state")
    if initial_state is None or initial_state not in states:
        raise ValueError(
            "`initial state` is invalid: invalid value or not present in `states`"
        )

    final_states = input.get("final states")
    if final_states is None or not set(final_states).issubset(states):
        raise ValueError(
            "`final states` is invalid: invalid value or not subset of `states`"
        )

    input_alpha = input.get("input alphabet")
    tape_alpha = input.get("tape alphabet")
    if input_alpha is None or tape_alpha is None:
        raise ValueError("`input alphabet` and `tape alphabet` cannot be empty")

    if not set(input_alpha).issubset(tape_alpha):
        raise ValueError("`input alphabet` not a subset of `tape_alpha`")

    if "_" in input_alpha:
        raise ValueError(
            "`input alphabet` contains `_`, which is the special blank character.\n"
            "It should only be present in your transitions."
        )
    tape_alpha += "_"

    transitions = input.get("transitions")
    if transitions is None:
        raise ValueError("`transitions` cannot be empty")

    if not isinstance(transitions, Dict[str, Any]):
        raise ValueError("`transitions` should be key/value pairs")

    new_trans = {}
    for state, alpha_transitions in transitions.items():
        if state not in states:
            raise ValueError(f"State `{state}` not in `states`")

        if not isinstance(alpha_transitions, Dict[str, Any]):
            raise ValueError(f"Value for state `{state}` should be a dictionary")

        for alpha, func in alpha_transitions.items():
            if alpha not in tape_alpha:
                raise ValueError(
                    f"Input transition character `{alpha}`"
                    " not in given tape alphabet"
                )

            dest_state = func.get("state")
            write_alpha = func.get("write")
            move_dir_str = func.get("move")

            function = [dest_state, write_alpha, move_dir_str]
            valids = [
                dest_state in states,
                write_alpha in tape_alpha,
                move_dir_str in ["L", "R", "l", "r"],
            ]

            if (
                False in list(map(lambda val: isinstance(val, str), function))
                or False in valids
            ):
                raise ValueError(f"Invalid transition function for ({state}, {alpha})")

            built_func = TransitionFunction(
                dest_state, write_alpha, TapeDirection(move_dir_str.upper())
            )

            new_trans[state][alpha] = built_func

    return (
        set(states),
        initial_state,
        set(final_states),
        set(input_alpha),
        set(tape_alpha),
        new_trans,
    )


class TuringMachine:
    def __init__(
        self,
        states: Set[str],
        initial_state: str,
        final_states: Set[str],
        input_alpha: Set[str],
        tape_alpha: Set[str],
        transitions: Dict[str, Dict[str, TransitionFunction]],
        # TODO: convert to False by default
        debug: bool = True,
    ):
        self.__states = states
        self.__initial_state = initial_state
        self.__final_states = final_states
        self.__input_alpha = input_alpha
        self.__tape_alpha = tape_alpha
        self.__transitions = transitions
        self.__debug = debug

    def run(self, input: str) -> str:
        if not set(input).issubset(self.__input_alpha):
            raise ValueError(f"`{input}` not subset of input alphabet")

        tape = list(input)
        tape_index = 0
        state = self.__initial_state

        while state not in self.__final_states:
            try:
                transition = self.__transitions[state][tape[tape_index]]
            except KeyError:
                raise ValueError(
                    f"Transition not defined for ({state}, {tape[tape_index]})."
                )

            tape[tape_index] = transition.write_alpha
            state = transition.destination
            if transition.direction is TapeDirection.LEFT:
                if tape_index == 0:
                    tape.insert(0, "_")
                else:
                    tape_index -= 1
            else:
                if tape_index == len(tape) - 1:
                    tape.append("_")

                tape_index += 1

        print(f"Final state reached: `{state}`\nTape Result: `{''.join(tape)}`")

        return "Pass"
