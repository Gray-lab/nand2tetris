

def main():
  cycle_lengths.append([cycle_length(a, m, 17), a, m])

  cycle_lengths = []
  for m in range(1, 256):
    for a in range(1, 256):
      cycle_lengths.append([cycle_length(a, m, 17), a, m])
  cycle_lengths.sort(key = lambda x: x[0])
  print(cycle_lengths)

# m = 251
# a = 43
# cycle = 250 items

def cycle_length(a : int, m : int, seed : int) -> int:
  cycle = []
  new_val = lehmerRNG(seed, a, m)
  while new_val not in cycle:
    cycle.append(new_val)
    new_val = lehmerRNG(new_val, a, m)
  results_dict = {'length' : len(cycle), 'cycle' : cycle}

  return len(cycle)

def lehmerRNG(prev_val, a, m):
  return a * prev_val % m


if __name__ == '__main__':
  main()