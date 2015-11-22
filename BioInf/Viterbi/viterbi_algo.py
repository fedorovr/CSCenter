TAIL = "0"
HEAD = "1"
WRONG_COIN = "Wrong coin"
RIGHT_COIN = "Right coin"

states = (RIGHT_COIN, WRONG_COIN)
start_probability = {RIGHT_COIN: 0.5, WRONG_COIN: 0.5}
observations = (HEAD, TAIL)
transition_probability = {
    RIGHT_COIN: {RIGHT_COIN: 0.8, WRONG_COIN: 0.2},
    WRONG_COIN: {RIGHT_COIN: 0.3, WRONG_COIN: 0.7},
}
emission_probability = {
   RIGHT_COIN: {TAIL: 0.5, HEAD: 0.5},
   WRONG_COIN: {TAIL: 0.9, HEAD: 0.1}
}


def viterbi_algo(observed_seq):
    viterbi = [{} for _ in range(len(observed_seq))]
    previous_state = [{} for _ in range(len(observed_seq))]

    # Base, pos == 0
    for state in states:
        viterbi[0][state] = start_probability[state] * emission_probability[state][observed_seq[0]]
        previous_state[0][state] = None

    # Run Viterbi for pos > 0
    for pos in range(1, len(observed_seq)):
        for state in states:
            state_probability, prev_state = max((transition_probability[prev][state] *
                                                 viterbi[pos-1][prev],
                                                 prev)
                                                for prev in states)
            state_probability *= emission_probability[state][observed_seq[pos]]
            previous_state[pos][state] = prev_state
            viterbi[pos][state] = state_probability

    # Find Viterbi path
    predicted_value, predicted_state = max((viterbi[len(observed_seq) - 1][state], state) for state in states)
    path = [predicted_state]

    for pos in range(len(observed_seq) - 1, 0, -1):
        predicted_state = previous_state[pos][predicted_state]
        path.append(predicted_state)
    return reversed(path)


def print_path(path):
    for p in path:
        print("+" if p == RIGHT_COIN else "-", end="")

print_path(viterbi_algo("000101010100000000111010111"))
