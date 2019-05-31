#Building a Chatbot with Deep NLP
import numpy as np
import tensorflow as tf
import re
import time
import os

lines = open('/Users/shenglo1/Documents/chatbot/movie_lines.txt', encoding='utf-8', errors='ignore').read().split('\n')
conversations = open('/Users/shenglo1/Documents/chatbot/movie_conversations.txt', encoding='utf-8', errors='ignore').read().split('\n')
