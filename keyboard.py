#!/usr/bin/env python

import random

fingers = [
    ['4', '3', '3', '2/3', '2/3', '12/13', '12/13', '13', '13', '14'],
    ['4', '4/3', '3/2', '2', '2', '12', '12', '13/12', '14/13'],
    ['4/3', '3', '2', '2', '2', '12', '13']
]

wrist_moving_keys = {(0, 4), (0, 5)}

stretch_keys = {(0, 0), (0, 3), (0, 6), (0, 9),
                (1, 4), (1, 5),
                (2, 3), (2, 4), (2, 5)}

fixed_keys = [
    ['q', 'w', '*', '*', '*', '*', '*', '*', '*', '*'],
    ['*', '*', '*', '*', '*', 'h', 'j', 'k', 'l'],
    ['z', 'x', 'c', 'v', '*', '*', '*']
]


QWERTY_perm = list('ertyuiopasdfgbnm')

alpahbet = 'abcdefghijklmnopqrstuvwxyz'
unset_keys = set(alpahbet)
for row in fixed_keys:
    for key in row:
        unset_keys.discard(key)

TEXTLEN = 10000
POPULATION_SIZE = 2000
MUTATION_FACTOR = 0.15


EPOCHS = 100


def fit(text, keys_index):
    penalty = 0
    prev_finger = ''
    prev_pos = None
    for c in text:
        pos = keys_index.get(c, None)
        if not pos:
            prev_finger = ''
            prev_pos = None
            continue
        if pos in wrist_moving_keys:
            penalty += 4
        if pos in wrist_moving_keys:
            penalty += 3
        if pos[0] == 2:
            penalty += 2
        if pos[0] == 0:
            penalty += 1
        finger = fingers[pos[0]][pos[1]]
        fings = finger.split('/')
        prev_fings = prev_finger.split('/')
        all_fingers = set(fings).union(set(prev_fings))

        # Moving 1 finger
        if (len(all_fingers) == 1) and (pos != prev_pos):
            penalty += 1

        # Using one hand
        right = False
        left = False
        for f in all_fingers:
            if len(f) == 2:
                right = True
            else:
                left = True
        if not(right and left):
            penalty += 0.5
        prev_finger = finger
        prev_pos = pos
    return penalty


def build_index(permutation):
    index = {}
    perm_index = 0
    for i in range(len(fixed_keys)):
        for j in range(len(fixed_keys[i])):
            key = fixed_keys[i][j]
            if key == '*':
                key = permutation[perm_index]
                perm_index += 1
            index[key] = (i, j)
    return index


def layout_random_generator():
    letters = list(unset_keys)
    while True:
        yield random.sample(letters, k=len(letters))


def print_epoch(epoch, population):
    print('EPOCH: ' + str(epoch))
    for i in range(5):
        print(population[i])
    print('....')
    for i in range(4, 0, -1):
        print(population[-i])


def main():
    population = []
    with open('big.txt', 'r') as f:
        text = f.read()[:TEXTLEN].lower()
    print('QWERTY SCORE: ' + str(fit(text, build_index(QWERTY_perm))))
    gener = layout_random_generator()
    for i in range(POPULATION_SIZE):
        p = next(gener)
        index = build_index(p)
        penalty = fit(text, index)
        population.append((p, penalty))
    population.sort(key=lambda x: x[1])
    half = len(population[0])/2
    for epoch in range(EPOCHS):
        print_epoch(epoch, population)
        # Mutation
        for i in range(len(population)):
            if random.random() <= MUTATION_FACTOR:
                individual = population[i][0]
                fr = random.randint(0, len(individual)-1)
                to = random.randint(0, len(individual)-1)
                individual[fr], individual[to] = individual[to], individual[fr]
                new_score = fit(text, build_index(individual))
                population[i] = (individual, new_score)
        # Crossover
        for i in range(POPULATION_SIZE):
                first = population[random.randint(0, len(population)-1)][0]
                second = population[random.randint(0, len(population)-1)][0]
                unused = set(unset_keys)
                individual = []
                for i in range(half):
                    unused.remove(first[i])
                    individual.append(first[i])
                for i in range(half, len(first)):
                    if (second[i] not in unused) and (first[i] in unused):
                        individual.append(first[i])
                        unused.remove(first[i])
                    elif (second[i] in unused):
                        individual.append(second[i])
                        unused.remove(second[i])
                    else:
                        char = list(unused)[random.randint(0, len(unused)-1)]
                        individual.append(char)
                        unused.remove(char)
                new_score = fit(text, build_index(individual))
                population.append((individual, new_score))
        population.sort(key=lambda x: x[1])
        population = population[: POPULATION_SIZE]
    print_epoch(epoch + 1, population)


if __name__ == '__main__':
    main()
