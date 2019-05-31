#Building a Chatbot with Deep NLP
import numpy as np
import tensorflow as tf
import re
import time

# Importing the datasets
lines = open('/Users/shenglo1/Documents/chatbot/movie_lines.txt', encoding='utf-8', errors='ignore').read().split('\n')
conversations = open('/Users/shenglo1/Documents/chatbot/movie_conversations.txt', encoding='utf-8', errors='ignore').read().split('\n')

# Creating a dictionary that maps each line to its id
id_to_line = {}
for line in lines:
    _line = line.split(' +++$+++ ')
    if (len(_line) == 5) :
        id_to_line[_line[0]] = _line[4]

# Creating a list of all of the conversations
conversations_ids = []
for conversation in conversations:
    _conversation = conversation.split(' +++$+++ ')[-1][1:-1].replace("'", "").replace(" ", "")
    conversations_ids.append(_conversation.split(','))
    
# Getting seperately the questions and the answers
questions = []
answers = []
for conversation in conversations_ids:
    for i in range(len(conversation) - 1):
        questions.append(id_to_line[conversation[i]])
        answers.append(id_to_line[conversation[i+1]])