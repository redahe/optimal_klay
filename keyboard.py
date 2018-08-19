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

TEXTLEN = 3000
POPULATION_SIZE = 100
MUTATION_FACTOR = 0.1


EPOCHS = 100

FOREIGNERS = POPULATION_SIZE/10


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
        if pos in stretch_keys:
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


def print_layout(perm):
    c = 0
    for i in range(len(fixed_keys)):
        row = []
        for j in range(len(fixed_keys[i])):
            key = fixed_keys[i][j]
            if key == '*':
                key = perm[c]
                c += 1
            row.append(key)
        print(row)



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


# Edge recombination operator
def crossover(perm1, perm2):
    seq = {}
    for perm in (perm1, perm2):
        for i in range(len(perm)-1):
            e = seq.get(perm[i], [])
            e.append(perm[i+1])
            seq[perm[i]] = e
    res = []
    unused = set(perm1).union(set(perm2))
    n = [perm1[0], perm2[0]][random.randint(0, 1)]
    while len(res) < len(perm1):
        res.append(n)
        if n in unused:
            unused.remove(n)
        for k,v in seq.items():
            if v and n in v:
                seq[k] = v.remove(n)
        v = seq.get(n)
        if v:
            n = v[random.randint(0, len(v))-1]
        else:
            if not unused:
                break
            n = list(unused)[random.randint(0, len(unused))-1]
    return res


def main():
    population = []
    with open('big.txt', 'r') as f:
        text = f.read()[:TEXTLEN].lower()
    gener = layout_random_generator()
    for i in range(POPULATION_SIZE):
        p = next(gener)
        index = build_index(p)
        penalty = fit(text, index)
        population.append((p, penalty))
    population.sort(key=lambda x: x[1])
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
        # Immigration
        for i in range(FOREIGNERS):
            p = next(gener)
            index = build_index(p)
            penalty = fit(text, index)
            population.append((p, penalty))
        # Crossover
        cur_size = len(population)
        for i in range(POPULATION_SIZE*2):
                first = population[random.randint(0, cur_size-1)][0]
                second = population[random.randint(0, cur_size-1)][0]
                individual = crossover(first, second)
                new_score = fit(text, build_index(individual))
                population.append((individual, new_score))
        population.sort(key=lambda x: x[1])
        population = population[: POPULATION_SIZE]
    print_epoch(epoch + 1, population)
    qwe=fit(text, build_index(QWERTY_perm))
    best = population[0][1]
    print('QWERTY: ' + str(qwe))
    print ('The best found layout is better in ' + str(int((qwe-best)*1.0/qwe*100))  + ' percents:')
    print_layout(population[0][0])



if __name__ == '__main__':
    main()
