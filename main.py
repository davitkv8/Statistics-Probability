from probability import Population

CL = 0.95
N = 550

population = Population("population.csv")

print(population)

sample1 = population.get_random_sample(n=N)

print(sample1)
