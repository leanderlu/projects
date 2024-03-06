import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor

# Load JSON file
json_file_path = 'final_merged_db.json'  # Replace with your JSON file path
df = pd.read_json(json_file_path)

# Assuming df has the columns 'feature1', 'feature2', ..., 'target'
X = df[['Age', 'bWAR', 'DRS', 'xwOBA']]  # Independent variables
y = df['Salary']  # Dependent variable

# Add a constant to the model (intercept)
X = sm.add_constant(X)

# Create and fit the model
model = sm.OLS(y, X).fit()

# View the results
print(model.summary())

vif_data = pd.DataFrame()
vif_data['Feature'] = X.columns
vif_data['VIF'] = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]

print(vif_data)
