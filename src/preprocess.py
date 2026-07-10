import pandas as pd
import numpy as np

df = pd.read_csv("final_complete_resume_dataset.csv")

print(df.isnull().mean() * 100)


df =  df.iloc[:,[1,2,3]]
print(df.shape)

print(df.head())

df['word_count'] = df['resume_text'].fillna("").apply(lambda x: len(str(x).split()))  # fillna used for the if the nan column than not count

total = df[df['word_count']< 30]  # less than 26 words

len(total)


df = df[df['word_count'] >= 30].reset_index(drop=True)

df = df.iloc[:,[0,1,2]]

df.to_csv(
    "clean_resume.csv",
    index=False,
    encoding="utf-8-sig"
)