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
        
# Doing a first cleaning of the text
def clean_text(text):
    text = text.lower()
    text = re.sub(r"i'm", "i am", text)
    text = re.sub(r"he's", "he is", text)
    text = re.sub(r"she's", "she is", text)
    text = re.sub(r"that's", "that is", text)
    text = re.sub(r"what's", "what is", text)
    text = re.sub(r"where's", "where is", text)
    text = re.sub(r"here's", "here is", text)
    text = re.sub(r"what's", "what is", text)
    text = re.sub(r"\'ll", " will", text)
    text = re.sub(r"\'ve", " have", text)
    text = re.sub(r"\'re", " are", text)
    text = re.sub(r"\'d", " would", text)
    text = re.sub(r"won't", "will not", text)
    text = re.sub(r"aren't", "are not", text)
    text = re.sub(r"isn't", "is not", text)
    text = re.sub(r"con't", " cannot", text)
    text = re.sub(r"""[-()+"=\&'@`{}#$%^~_|!*/?;,.:]""", "", text)
    return text

# Cleaning the questions
clean_questions = []
for question in questions:
    clean_questions.append(clean_text(question))
    
# Cleaning the answers
clean_answers = []
for answer in answers:
    clean_answers.append(clean_text(answer))
    
# Creating a dictionary that maps each word to its number of occurences
word_to_count = {}
for question in clean_questions:
    for word in question.split() :
        if word not in word_to_count:
            word_to_count[word] = 1
        else:
            word_to_count[word] += 1

for answer in clean_answers:
    for word in answer.split() :
        if word not in word_to_count:
            word_to_count[word] = 1
        else:
            word_to_count[word] += 1
            
# Creating two dictionaries that map the question word and the answer word to the unique integer
threshold = 20
questionwords_to_int = {}
word_num = 0
for word, count in word_to_count.items():
    if count >= threshold:
        questionwords_to_int[word] = word_num
        word_num += 1

answerwords_to_int = {}
word_num = 0
for word, count in word_to_count.items():
    if count >= threshold:
        answerwords_to_int[word] = word_num
        word_num += 1

# Adding the last tokens to these two dictionaries
tokens = ['<PAD>', '<EOS>', '<OUT>', '<SOS>'] 
for token in tokens:
    questionwords_to_int[token] = len(questionwords_to_int) + 1
    
for token in tokens:
    answerwords_to_int[token] = len(answerwords_to_int) + 1
    
# Creating the inverse dictionary of the answerword_to_int dictionary
answerint_to_word = {w_i: w for w, w_i in answerwords_to_int.items()}

# Adding the End of String token to the end of every answer
for i in range(len(clean_answers)):
    clean_answers[i] += ' <EOS>'
    
# Translating all the questoins and answer into integers
# and replacing all the words that were filtered out by <OUT>
question_to_ints = []
for question in clean_questions:
    ints = []
    for word in question.split():
        if word not in questionwords_to_int:
            ints.append(questionwords_to_int['<OUT>'])
        else:
            ints.append(questionwords_to_int[word])
    question_to_ints.append(ints)
    
answer_to_ints = []
for answer in clean_answers:
    ints = []
    for word in answer.split():
        if word not in answerwords_to_int:
            ints.append(answerwords_to_int['<OUT>'])
        else:
            ints.append(answerwords_to_int[word])
    answer_to_ints.append(ints)
    
# Sorting questions and answers by the length of questions
sorted_clean_questions = []
sorted_clean_answers = []
for length in range (1, 26):
    for i in enumerate(question_to_ints):
        if len(i[1]) == length:
            sorted_clean_questions.append(question_to_ints[i[0]])
            sorted_clean_answers.append(answers_to_ints[i[0]])
            