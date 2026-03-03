# import pandas as pd
# import numpy as np
# from scipy.stats import chi2_contingency

# # Construct contingency table
# data = {
#     "public": [576, 7123 - 576],
#     "private": [662, 3856 - 662],
#     "protected": [105, 1429 - 105],
#     "package-private": [51, 464 - 51]
# }
# df = pd.DataFrame(data, index=["Rank1", "Not Rank1"])

# # Perform chi-square test
# chi2, p, dof, expected = chi2_contingency(df)

# # Compute standardized residuals
# observed = df.values
# std_residuals = (observed - expected) / np.sqrt(expected)

# # Convert to DataFrame for clarity
# residuals_df = pd.DataFrame(std_residuals, index=df.index, columns=df.columns)
# print("Standardized Residuals (z-scores):")
# print(residuals_df.round(3))

import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency

def cramers_v(chi2, n, df):
    return np.sqrt(chi2 / (n * min(df.shape[0] - 1, df.shape[1] - 1)))

# The DataFrame for Access Modifier
access_modifier_data = {
    'Access Modifier': ['public', 'private', 'protected', 'package-private'],
    'All': [7123, 3856, 1429, 464],
    'Rank1': [576, 662, 105, 51],
    'Rank2': [1155, 918, 157, 90],
    'Rank3': [1560, 1050, 204, 114],
    'Rank4': [1902, 1138, 241, 132],
    'Rank5': [2148, 1189, 261, 142],
}

# The DataFrame for method type
method_type_data = {
    'Method Type': ['non-void', 'void', 'constructor'],
    'All': [9553, 2842, 477],
    'Rank1': [833, 494, 67],
    'Rank2': [1487, 723, 110],
    'Rank3': [1969, 823, 136],
    'Rank4': [2393, 876, 144],
    'Rank5': [2666, 922, 152],
}

# The DataFrame for mutation operator
mutation_operator_data = {
    'Mutation Operator': ['NegateConditionalsMutator', 'MathMutator', 'ConditionalsBoundaryMutator', 'NullReturnValsMutator',
                          'VoidMethodCallMutator', 'PrimitiveReturnsMutator', 'EmptyObjectReturnValsMutator', 
                          'BooleanTrueReturnValsMutator', 'IncrementsMutator', 'BooleanFalseReturnValsMutator', 'InvertNegsMutator'],
    'All': [4279, 3491, 1530, 970, 854, 522, 386, 352, 197, 169, 122],
    'Rank1': [366, 490, 119, 56, 164, 52, 32, 35, 42, 16, 22],
    'Rank2': [625, 796, 188, 122, 230, 85, 102, 58, 54, 34, 26],
    'Rank3': [843, 954, 224, 163, 274, 123, 128, 79, 59, 47, 34],
    'Rank4': [1038, 1070, 258, 185, 307, 145, 141, 102, 64, 62, 41],
    'Rank5': [1204, 1131, 282, 198, 324, 156, 160, 106, 70, 68, 41],
}

# The DataFrame for Nesting level
nesting_level_data = {
    'Nesting Level': ['0', '1', '2', '3', '4', '5', '6'],
    'All': [6347, 3461, 1559, 797, 402, 157, 67],
    'Rank1': [524, 375, 220, 140, 79, 32, 12],
    'Rank2': [844, 696, 379, 190, 121, 46, 20],
    'Rank3': [1115, 892, 452, 236, 133, 52, 22],
    'Rank4': [1333, 1024, 505, 281, 147, 59, 26],
    'Rank5': [1500, 1103, 548, 298, 157, 65, 30],
}

# The DataFrame for mutation operator
node_type_data = {
    'Node Type': ['BinaryOperation', 'IfStatement', 'ReturnStatement', 'ForStatement',
                          'MethodInvocation', 'TernaryExpression', 'StatementExpression', 
                          'WhileStatement', 'VariableDeclaration'],
    'All': [4308, 4195, 2427, 868, 866, 114, 58, 19, 14],
    'Rank1': [587, 336, 191, 70, 179, 20, 2, 5, 4],
    'Rank2': [950, 563, 402, 120, 245, 25, 4, 7, 4],
    'Rank3': [1140, 750, 545, 150, 290, 34, 6, 8, 5],
    'Rank4': [1277, 938, 643, 168, 323, 41, 10, 8, 5],
    'Rank5': [1386, 1061, 696, 186, 340, 48, 10, 8, 5],
}

# variable_name = 'Access Modifier'
# variable_name = 'Method Type'
# variable_name = 'Mutation Operator'
# variable_name = 'Nesting Level'
variable_name = 'Node Type'

if variable_name == 'Access Modifier':
    data = access_modifier_data
elif variable_name == 'Method Type':
    data = method_type_data
elif variable_name == 'Nesting Level':
    data = nesting_level_data
elif variable_name == 'Mutation Operator':
    data = mutation_operator_data
elif variable_name == 'Node Type':
    data = node_type_data
df = pd.DataFrame(data)
df.set_index(variable_name, inplace=True)

# Function to analyze one rank
def analyze_rank(df, rank_label):
    # Prepare contingency table
    observed = pd.DataFrame({
        rank_label: df[rank_label],
        'Not_' + rank_label: df['All'] - df[rank_label]
    })

    chi2, p, dof, expected = chi2_contingency(observed)
    cramer_v_val = cramers_v(chi2, observed.to_numpy().sum(), observed)

    residuals = (observed - expected) / np.sqrt(expected)

    print(f"\n=== {rank_label} Analysis ===")
    print(f"Chi2 = {chi2:.4f}, p = {p:.4f}, Cramér's V = {cramer_v_val:.4f}")
    print("Standardized Residuals:")
    print(residuals)

    return {
        'rank': rank_label,
        'chi2': chi2,
        'p': p,
        'cramers_v': cramer_v_val,
        'residuals': residuals
    }

# Run for Rank1 to Rank5
results = {}
for rank in ['Rank1', 'Rank2', 'Rank3', 'Rank4', 'Rank5']:
    results[rank] = analyze_rank(df, rank)

