from probability import StatisticsAndProbability

population = StatisticsAndProbability("population.csv")

print(population)

sample1 = population.get_random_sample(n=55)

print(sample1)

t_score_interval = sample1.confidence_interval(T_score=2.01)
z_score_interval = sample1.confidence_interval(Z_score=1.96)

print("95% Confidence level with 55 sample participants")

print(f"T-score interval corrected:        {t_score_interval[1]}\n"
      f"T-score interval:                  {t_score_interval[0]}\n")
