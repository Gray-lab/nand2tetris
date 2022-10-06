import matplotlib.pyplot as plt
import numpy as np

def main():
  # cycle_lengths.append([cycle_length(a, m, 17), a, m])
    plot_points(41, 29)
#   cycle_lengths = []
#   for m in range(1000, 1500):
#     for a in range(1, 51):
#       if a * m < 32767:
#         cycle_lengths.append([cycle_length(a, m, 1), a, m])
#   cycle_lengths.sort(key = lambda x: x[0])
#   print(cycle_lengths[-105:])

# m = 251
# a = 43
# cycle = 250 items
def plot_points(x_dim : int, y_dim : int) -> None:
  a = 19
  m = 1499
  length = 50
  xpoints1 = get_rand_list(a, m, 64, length, x_dim)
  ypoints1 = get_rand_list(a, m, 64, length, y_dim)
  xpoints3 = get_rand_list(a, m, 63, length, x_dim)
  ypoints3 = get_rand_list(a, m, 63, length, y_dim)
  xpoints2 = get_rand_list(a, m, 120, length, x_dim)
  ypoints2 = get_rand_list(a, m, 120, length, y_dim)
  plt.plot(xpoints1, ypoints1, "s", alpha=0.5, color='red')
  plt.plot(xpoints2, ypoints2, "s", alpha=0.5, color='blue')
  plt.plot(xpoints3, ypoints3, "s", alpha=0.5, color='green')
  plt.show()


def cycle_length(a : int, m : int, seed : int) -> int:
  cycle = []
  new_val = lehmerRNG(seed, a, m)
  while new_val not in cycle:
    cycle.append(new_val)
    new_val = lehmerRNG(new_val, a, m)
  results_dict = {'length' : len(cycle), 'cycle' : cycle}

  return len(cycle)

def get_rand_list(a: int, m: int, seed: int, length: int, max: int) -> int:
    values = []
    new_val = lehmerRNG(seed, a, m)
    for i in range(length-1):
        values.append(new_val % max)
        new_val = lehmerRNG(new_val, a, m)
    return values

def lehmerRNG(prev_val, a, m):
  return (a * prev_val) % m


if __name__ == '__main__':
  main()