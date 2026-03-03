import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency
import math

# Data: [Rank1, Not Rank1] for each access modifier
data = np.array([
    [576, 7123 - 576],         # public
    [662, 3856 - 662],         # private
    [105, 1429 - 105],         # protected
    [51, 464 - 51]             # package-private
])

# Create contingency table
access_modifiers = ['public', 'private', 'protected', 'package-private']
df = pd.DataFrame(data, index=access_modifiers, columns=['Rank1', 'Not Rank1'])

# Chi-Square Test
chi2, p, dof, expected = chi2_contingency(df)

print("Chi-Square Test Results")
print("------------------------")
print(f"Chi2 Statistic: {chi2:.4f}")
print(f"Degrees of Freedom: {dof}")
print(f"P-Value: {p:.4f}")
print()

# Cramér's V
n = df.to_numpy().sum()
min_dim = min(df.shape) - 1
cramers_v = math.sqrt(chi2 / (n * min_dim))

print("Cramér's V Effect Size")
print("-----------------------")
print(f"Cramér's V: {cramers_v:.4f}")
