# -*- coding: utf-8 -*-
"""data _cleaning (1).ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Y7eSu-W0nA_-eR0BJ8xemrAuKY6X8Ij2
"""

import pandas as pd

df = pd.read_csv('DATASET.csv')

df.head()

len(df)

len(df[df['label'] == 0])/len(df)

len(df[df['label'] == 1])/len(df)

df['content'].iloc[0]

"""#### Cleaning function:"""

import re
import string
def clean_text(article):
    text = article.lower()
    text = text.replace('\n', " ")
    tokens = text.split(" ")
    regex = "[a-zA-Z]"
    refined_tokens = []
    for item in tokens:
        if re.match(regex, item):
            refined_tokens.append(item)
    cleaned_text = ' '.join(token for token in refined_tokens)
    return cleaned_text.translate(str.maketrans('', '', string.punctuation))

clean_text(df['content'].iloc[0])

clean_text(df['title'].iloc[0])

"""#### Run the cleaning function on all rows for 'content' and 'title' columns:"""

df['cleaned_content'] = df['content'].apply(lambda x: clean_text(x))

df['cleaned_title'] = df['title'].apply(lambda x: clean_text(x))

df.head()

"""#### Save the cleaned dataset"""

df.to_csv('cleaned_data.csv')

"""#### Shuffle data and split train and test set"""

# Shuffle data
df = df.sample(frac=1)

len(df)

import math
n = math.ceil(len(df) * 0.9)

train = df[0:n]

test = df[n:]

len(train)

len(test)

train.to_csv('train.csv')

test.to_csv('test.csv')