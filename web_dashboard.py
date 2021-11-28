import streamlit as st
import requests
import time
import webbrowser
import pickle
import os
import pandas as pd


import numpy as np
import seaborn as sns
import re
import matplotlib.pyplot as plt
import os
import contractions

from wordcloud import WordCloud
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation as LDA

#from decouple import config
from topicmapping import topicmapping as tm

if __name__ == '__main__':
	st.title('Streamlit run...')
