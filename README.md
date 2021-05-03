# YAML-defined Turing Machine

A basic multi-tape turing machine runner with interactive input and a YAML
machine definition schema.

## Dependencies

This program requires python 3.7+ and `pyaml`, which you can install using the included
`requirements.txt`. You can either install system-wide (which is not
recommended), or you can use a virtual environment of your choice.

## Running

To run the program, use `python[3] main.py ARGS`. Here is the help text, which
can be printed by using `-h/--help`.

```
usage: main.py [-h] -f, --yaml INPUT [-d, --debug]

A basic YAML-defined pushdown automata

optional arguments:
  -h, --help        show this help message and exit
  -f, --yaml INPUT  The YAML file to use as the turing machine definition
  -d, --debug       Print debug messages, which includes transitions (default: False)
```

## Included Examples

This comes with six example machines:

- `1b-wwR.yaml`
- `acceptor.yaml`
- `binary-addition.yaml`
- `unary-addition.yaml`
- `unary-multiplication.yaml`
- `unary-division.yaml.yaml`

Each one comes with a description that the program prints when the REPL starts
to read the tape(s).

### More Details

- `1b-wwR.yaml`: This one is fairly simple. We know we need at least one `w` and
  an even total length for the alphabet. By "flip-flopping" after passing the
  initial `w`, we can make sure we have an even number when we finish the
  string.
- `acceptor.yaml`: Replace the first one of each set, then reset and do it until
  you have replaced the same number of each. If the original value is part of
  the language, then the same number of `a`s, `b`s, and `c`s will have been
  replaced with `x`, `y`, and `z` respectively.
- `binary-addition.yaml`: There are effectively two states we are in when we are
  adding the binary numbers: We either do or do not have a carry. Realizing this
  makes it mostly trivial -- the written value is put down based on what was
  there and if we had a carry, then we change state if we gained or lost the
  carry bit.
- `unary-addition.yaml`: Scroll to the end of one number, then scroll through
  the second while writing to the end of the first. Zzzzzz...
- `unary-multiplication.yaml.yaml`: This one and the next, unary division, have
  a lot in common. Multiplication is just repeated additions, so we effectively
  are doing the unary addition above, but repeating it until we have done every
  combination of "its" (get it? 'cause it's an "it" instead of a "bit").
- `unary-division.yaml`: We are doing multiplication, but backwards, and we have
  to watch out for errors. Go to the end of our dividend, subtracting sets of
  the divisor and adding to the quotient until we either:
  - Hit the end of both at the same time (dividing evenly) and ending with a
    remainder of zero.
  - Hit the end of the dividend, but not he divisor. We re-add what we have
    already taken from the divisor so that our remainder is correct.

## Schema

The schema is as follows:

- `description`: A string with a description of the machine. Can include the
  language or the tape inputs.
- `tapes`: A positive integer, the number of tapes to use.
- `initial state`: The starting state for the machine. Must be present in
  `states`
- `final state`: The final state for the machine. Also must be present in
  `states`
- `states`: A list of strings defining the state names.
- `input alphabet`: A string which defines the alphabet of the initial tapes.
  Note that `_` (underscore) cannot be used, as it is the specialty **_blank_**
  character. Repeats are technically allowed, but are discarded.
- `tape alphabet`: The alphabet of the tapes. This will often be the same as
  `input alphabet`, but can have others. `_` (underscore) is automatically added
  so it should not be present.
- `transitions`: A deep dictionary where there are two keys to access a
  transition function. The first key is the state name, and the second is the
  tape(s) value(s).

  If using more than one tape, the tape value should be a comma separated
  (without spaces) list of the symbols in the tape alphabet. So if we had three
  tapes and wanted tape zero to be "a", tape one to be blank (`_`), and tape two
  to be "b", we would use `a,_,b`. Note that a number alone as a tape value
  should be wrapped in quotes so that YAML parses it as a string.

  The transition function is three key value pairs: 
    - `state`, which is the destination state
    - `write`, the same format as the second key which will be written in the
      same order to the tapes.
    - `move`, which is the values to write to the tapes in the same format as
      the tape value above, using `L` to move left, `N` to stay in place, and
      `R` to move the tape right.

## Process

Now, I know this wasn't as prompted, but I had thought about this a lot and
liked the format of my YAML pushdown automaton, so I opted to do something
similar and not write specific machines first. Thankfully, this YAML format is
much easier to validate and has fewer conditional things.

So, I started first by doing my YAML parsing while also writing the
`TuringMachine` class in parallel. This is mostly boring, so I'll gloss over it,
but I took our $a^nb^nc^n$ acceptor/transducer and used that to verify I had it
*mostly* working. This went fairly smoothly, but I only had single tapes
working. I also had user input working as expected along with command line
arguments.

At this point, I moved to binary addition and started working on using any
number of tapes. This effectively turned a transition function from a
three-tuple of state, some alpha in the alphabet, and the movement direction
into a three-tuple of state, an n-tuple of alphas, and an n-tuple of movement
directions, where each member of the inner tuples corresponded to the tape of
the corresponding index. This was more finicky since I had to split on `,`
(comma), but once I had it done it was smooth sailing from there. The number of
tapes could now be defined in the schema, making input from the user easy.
