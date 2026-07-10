# import pandas as pd


# df1 = pd.read_csv("data\\extracted\\resume_text_100.csv")
# print(df1.shape)

# df2 = pd.read_csv("data\\extracted\\resume_text_101_1000.csv")
# print(df2.shape)

# df3 = pd.read_csv("data\\extracted\\resume_text_1001_1500.csv")
# print(df3.shape)

# df4 = pd.read_csv("data\\extracted\\resume_text_1501_2000.csv")
# print(df4.shape)

# df5 = pd.read_csv("data\\extracted\\resume_text_2001_2500.csv")
# print(df5.shape)
# df6 = pd.read_csv("data\\extracted\\resume_text_2501_3000.csv")
# print(df6.shape)
# df7 = pd.read_csv("data\\extracted\\resume_text_3001_4000.csv")
# print(df7.shape)
# df8 = pd.read_csv("data\\extracted\\resume_text_4001_5000.csv")
# print(df8.shape)
# df9 = pd.read_csv("data\\extracted\\resume_text_5000_6000.csv")
# print(df9.shape)
# df10 = pd.read_csv("data\\extracted\\resume_text_6000_6500.csv")
# print(df10.shape)
# df11 = pd.read_csv("data\\extracted\\resume_text_6500_6550.csv")
# print(df11.shape)
# df12 = pd.read_csv("data\\extracted\\resume_text_6550_7500.csv")
# print(df12.shape)
# df13 = pd.read_csv("data\\extracted\\resume_text_7500_8500.csv")
# print(df13.shape)
# df14 = pd.read_csv("data\\extracted\\resume_text_8500_9063.csv")
# print(df14.shape)

# df = pd.concat([df1, df2, df3, df4, df5, df6, df7, df8, df9, df10, df11, df12, df13, df14])

# print(df.shape)

# print(df['resume_text'].duplicated().mean() * 100)

# df = df.drop_duplicates(subset=["resume_text"]).reset_index(drop=True)
# print(df.shape)

# df.to_csv("final_complete_resume_dataset.csv")

# print("successfully created main file")



import pandas as pd
df = pd.read_csv("final_complete_resume_dataset.csv")

print(df.tail(5))

print(df.shape)