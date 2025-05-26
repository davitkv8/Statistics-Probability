from probability import Population

CL = 0.95
N = 550

population = Population("population.csv")

print(population)

sample1 = population.get_random_sample(n=N)

print(sample1)

t_score_interval = sample1.confidence_interval(cl=CL, score="T_Score")
z_score_interval = sample1.confidence_interval(cl=CL, score="Z_Score")

print(f"{CL}% Confidence level with {N} sample participants")

print(f"T-score interval corrected:        {t_score_interval[1]}\n"
      f"T-score interval:                  {t_score_interval[0]}\n"
      f"Z-score interval:                  {z_score_interval[0]}\n")
