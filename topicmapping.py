import pandas as pd
import numpy as np
import seaborn as sns
import re
import matplotlib.pyplot as plt
import os
import streamlit as st
import contractions

from wordcloud import WordCloud
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation as LDA

class TopicMapping(object):
        
    def load_dataset(self, df):
        clean_comments =  df['Comments'].apply(self.remove_punctuations).apply(self.to_lowercase).apply(self.clean_html).apply(self.fix_apostrophe).apply(self.expand_contractions)
        return clean_comments, self.generate_word_cloud(clean_comments)
    
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
    
    def generate_word_cloud(self, comments):
        long_string = ','.join(comments)
        word_cloud = WordCloud(background_color='white', max_words=5000, contour_width=5, contour_color='steelblue')
        word_cloud.generate(long_string)
        return word_cloud.to_image()
        
    def plot_most_common_words(self, count_data, count_vectorizer, value):
        words = count_vectorizer.get_feature_names()
        total_counts = np.zeros(len(words))
        for t in count_data:
            total_counts += t.toarray()[0]
        count_dict = (zip(words, total_counts))
        count_dict = sorted(count_dict, key=lambda x:x[1], reverse=True)[0:value]
        words = [w[0] for w in count_dict]
        counts = [w[1] for w in count_dict]
        x_pos = np.arange(len(words))
        plt.figure(2, figsize=(15, 15/1.6180))
        plt.subplot(title='asdasd')
        sns.set_context('notebook', font_scale=1.25, rc={'lines.linewidth': 2.5})
        sns.barplot(x_pos, counts, palette='husl')
        plt.xticks(x_pos, words, rotation=90)
        plt.xlabel('words')
        plt.ylabel('counts')
        plt.show()
        
    def print_topics(self, model, count_vectorizer, n_top_words):
        topic_list = []
        words = count_vectorizer.get_feature_names()
        for topic_idx, topic in enumerate(model.components_):
            print("\nTopic #%d:" % topic_idx)
            print(" ".join([words[i] for i in topic.argsort()[:-n_top_words - 1:-1]]))
            topic_list.append(" ".join([words[i] for i in topic.argsort()[:-n_top_words - 1:-1]]))
        return topic_list
            
    def generate_topic(self, number_topics, number_words, count_vectorizer, count_data):
        lda = LDA(n_components=number_topics, n_jobs=-1)
        lda.fit(count_data)
        print("Topics generated using LDA:")
        topic_list = self.print_topics(lda, count_vectorizer, number_words)
        return topic_list
        
    def fetch_topic(self, df):
        with st.spinner('Generating topics...'):
            comments, result = self.load_dataset(df)
            count_vectorizer = CountVectorizer(stop_words='english')          
            count_data = count_vectorizer.fit_transform(comments) 
            topics = self.generate_topic(12, 9, count_vectorizer, count_data)
            return topics

topicmapping = TopicMapping()

if __name__ == "__main__":
    pass
