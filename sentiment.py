import nltk
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA

import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import re
import matplotlib.pyplot as plt 
import os
import contractions
import altair as alt

class Sentiment(object):

	def load_dataset(self, df):
		clean_comments =  df['Comments'].apply(self.remove_punctuations).apply(self.to_lowercase).apply(self.clean_html).apply(self.fix_apostrophe).apply(self.expand_contractions)
		return clean_comments

	def remove_punctuations(self, comment):
		return re.sub('[,\.!?]','', comment)

	def fix_apostrophe(self, comment):
		apos =  re.sub("&#39;","''", comment)
		return re.sub("&quot", "", apos)

	def expand_contractions(self, comment):
		exp_comments = [contractions.fix(word) for word in comment.split()]
		return ' '.join(exp_comments)

	def clean_html(self, comment):
		cleanr = re.compile('<.*?>')
		cleantext = re.sub(cleanr, '', comment)
		return cleantext

	def to_lowercase(self, comments):
		return comments.lower()

	def hist_plot(self, df):
		df["compound_trunc"] = df.compound.round(1) # Truncate compound scores into 0.1 buckets 

		res = (df.groupby(["compound_trunc"])
		        .count()
		        .reset_index()
		      )

		hist = alt.Chart(res).mark_bar(width=15).encode(
		    alt.X("compound_trunc:Q", axis=alt.Axis(title="")),
		    y=alt.Y('count:Q', axis=alt.Axis(title="")),
		    color=alt.Color('compound_trunc:Q', scale=alt.Scale(scheme='redyellowgreen')), 
		    tooltip=['compound_trunc', 'count']
		)

		
		return hist

	def fetch_sentiment(self, df):
		with st.spinner('Analysing sentiments...'):
			comments = self.load_dataset(df)
			sia = SIA()
			results = [sia.polarity_scores(line) for line in comments]
    
			scores_df = pd.DataFrame.from_records(results)
			df = scores_df.join(comments, rsuffix="_right")
			return df

sentiment = Sentiment()

if __name__ == "__main__":
    pass



    
    
