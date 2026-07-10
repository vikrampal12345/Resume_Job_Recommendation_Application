import pandas as pd
import numpy as np

df = pd.read_csv("data\\annotated\\annotated_resume.csv")
print(df.columns.tolist())

print(df['resume_text'].duplicated().sum())
print(df.shape)
print(df.duplicated().sum())

