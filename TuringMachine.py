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
    write_alpha: Tuple[str]
    direction: TapeDirection


def verify_yaml_dictionary(
    input: Dict,
) -> Tuple[
    int,
    Set[str],
    str,
    Set[str],
    Set[str],
    Set[str],
    Dict[str, Dict[str, TransitionFunction]],
]:
    number_tapes = input.get("tapes", 1)
    if not isinstance(number_tapes, int):
        raise TypeError("`tapes` should be undefined or a positive integer")

    states = input.get("states")
    if states is None:
        raise ValueError("`states` cannot be empty")
    if not isinstance(states, list):
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

    if not isinstance(transitions, dict):
        raise ValueError("`transitions` should be key/value pairs")

    new_trans = {}
    for state, alpha_transitions in transitions.items():
        if state not in states:
            raise ValueError(f"State `{state}` not in `states`")

        if new_trans.get(state) is None:
            new_trans[state] = {}

        if not isinstance(alpha_transitions, dict):
            raise ValueError(f"Value for state `{state}` should be a dictionary")

        for alpha, func in alpha_transitions.items():
            alphas = tuple(alpha.split(","))
            for alpha in alphas:
                if alpha not in tape_alpha:
                    raise ValueError(
                        f"Input transition character `{alpha}`"
                        " not in given tape alphabet"
                    )

            move_dir_str = func.get("move")
            write_alpha_str = func.get("write")
            if False in [
                isinstance(val, str) for val in [write_alpha_str, move_dir_str]
            ]:
                raise TypeError(
                    f"`write` and/or `move` for transition ({state}, {alpha}) is non-string"
                )

            move_dirs = tuple(move_dir_str.split(","))
            write_alphas: Tuple[str, ...] = tuple(write_alpha_str.split(","))
            for al in write_alphas:
                if al not in tape_alpha:
                    raise ValueError(f"State ({state}, {alpha}) has invalid write")

            dest_state = func.get("state")
            if not isinstance(dest_state, str) or dest_state not in states:
                raise ValueError(f"Destination state for ({state}, {alpha}) is invalid")

            built_func = TransitionFunction(
                dest_state, write_alphas, TapeDirection(move_dir_str.upper())
            )

            new_trans[state][alpha] = built_func

    return (
        number_tapes,
        set(states),
        initial_state,
        set(final_states),
        set(input_alpha),
        set(tape_alpha),
        new_trans,
    )


class TuringMachine:
    @property
    def number_tapes(self) -> int:
        return self.__number_tapes

    def __init__(
        self,
        number_tapes: int,
        states: Set[str],
        initial_state: str,
        final_states: Set[str],
        input_alpha: Set[str],
        tape_alpha: Set[str],
        transitions: Dict[str, Dict[str, TransitionFunction]],
        debug: bool = False,
    ):
        self.__number_tapes = number_tapes
        self.__states = states
        self.__initial_state = initial_state
        self.__final_states = final_states
        self.__input_alpha = input_alpha
        self.__tape_alpha = tape_alpha
        self.__transitions = transitions
        self.__debug = debug

    def run(self, input_strs: List[str]) -> Tuple[str, List[str]]:
        for input_str in input_strs:
            if not set(input_str).issubset(self.__input_alpha):
                raise ValueError(f"`{input_strs}` not subset of input alphabet")

        if not len(input_strs) == self.__number_tapes:
            raise ValueError("Passed number of strings does not match number of tapes")
        tapes = list(map(lambda in_str: list(in_str), input_strs))
        tape_indices = [0 for _str in input_strs]

        state = self.__initial_state
        while state not in self.__final_states:
            tape_alpha_status = [tape[idx] for idx in tape_indices for tape in tapes]
            tape_key = ",".join(tape_alpha_status)
            try:
                transition = self.__transitions[state][tape_key]
            except KeyError:
                raise ValueError(f"Transition not defined for ({state}, {tape_key}).")
            if self.__debug:
                print(
                    f"({state}, {tape_key} (ind {tape_indices})) => "
                    f"({transition.destination}, {transition.write_alpha}, {transition.direction})"
                )

            state = transition.destination
            for idx, tape in enumerate(tapes):
                tape[tape_indices[idx]] = transition.write_alpha[idx]
                if transition.direction is TapeDirection.LEFT:
                    if tape_indices[idx] == 0:
                        tape.insert(0, "_")
                    else:
                        tape_indices[idx] -= 1
                else:
                    if tape_indices[idx] == len(tape) - 1:
                        tape.append("_")

                    tape_indices[idx] += 1

            if self.__debug:
                for idx, tape in enumerate(tapes):
                    print(f"Tape {idx + 1}: {tape}")

        return (state, ["".join(tape).strip("_") for tape in tapes])
