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
            sorted_clean_answers.append(answer_to_ints[i[0]])
            
# Creating placeholders for the input and the targets
def model_inputs():
    inputs = tf.placeholder(tf.int32, [None, None], name='input')
    targets = tf.placeholder(tf.int32, [None, None], name='target')
    lr = tf.placeholder(tf.float32, name='learning rate')
    keep_prob = tf.placeholder(tf.float32, name='keep_prob')
    return inputs, targets, lr, keep_prob

# Preprocessing the targets
def preprocess_targets(targets, word_to_int, batch_size):
    left_side = tf.fill([batch_size, 1], word_to_int['<SOS>'])
    right_side = tf.strided_slice(targets, [0, 0], [batch_size, -1], [1, 1])
    preprocessed_targets = tf.concat([left_side, right_side], 1)
    return preprocessed_targets
    
# Creating the Encoder RNN Layer
def encoder_rnn(rnn_inputs, rnn_size, num_layers, keep_prob, sequence_length):
    lstm = tf.contrib.rnn.BasicLSTMCell(rnn_size)
    lstm_dropout = tf.contrib.rnn.DropoutWrapper(lstm, input_keep_prob=keep_prob)
    encoder_cell = tf.contrib.rnn.MultiRNNCell([lstm_dropout] * num_layers)
    _, encoder_state = tf.nn.bidirectional_dynamic_rnn(cell_fw=encoder_cell,
                                                       cell_bw=encoder_cell,
                                                       sequence_length=sequence_length,
                                                       inputs=rnn_inputs,
                                                       dtype=tf.float32)
    return encoder_state

# Decoding the training set
def decode_training_set(encoder_state, decoder_cell, decoder_embadded_input, 
                        sequence_length, decoding_scope, output_function,
                        keep_prob, batch_size):
    attention_states = tf.zeros([batch_size, 1, decoder_cell.output_size])
    attention_keys, attention_values, attention_score_function, attention_construct_function = tf.contrib.seq2seq.prepare_attention(attention_states, attention_option= 'bahdanau', num_units=decoder_cell.output_size)
    training_decoder_function = tf.contrib.seq2seq.attention_decoder_fn_train(encoder_state[0], 
                                                                              attention_keys, 
                                                                              attention_values, 
                                                                              attention_score_function, 
                                                                              attention_construct_function, 
                                                                              name="attn_dec_train")
    decoder_ouput, decoder_final_state, decoder_final_context_state = tf.contrib.seq2seq.dynamic_rnn_decoder(decoder_cell, 
                                                                                                             training_decoder_function, 
                                                                                                             decoder_embadded_input, 
                                                                                                             sequence_length, 
                                                                                                             scope=decoding_scope)
    decoder_ouput_dropout = tf.nn.dropout(decoder_ouput, keep_prob)
    return output_function(decoder_ouput_dropout)

# Decoding the test/validation set
def decode_test_set(encoder_state, decoder_cell, decoder_embaddings_matrix, sos_id,
                        eos_id, max_length, num_words, decoding_scope, 
                        output_function, keep_prob, batch_size):
    attention_states = tf.zeros([batch_size, 1, decoder_cell.output_size])
    attention_keys, attention_values, attention_score_function, attention_construct_function = tf.contrib.seq2seq.prepare_attention(attention_states, attention_option= 'bahdanau', num_units=decoder_cell.output_size)
    test_decoder_function = tf.contrib.seq2seq.attention_decoder_fn_inference(output_function, 
                                                                              encoder_state[0], 
                                                                              attention_keys, 
                                                                              attention_values, 
                                                                              attention_score_function, 
                                                                              attention_construct_function, 
                                                                              decoder_embaddings_matrix,
                                                                              sos_id, 
                                                                              eos_id, 
                                                                              max_length, 
                                                                              num_words,
                                                                              name="attn_dec_inf")
    test_predictions, decoder_final_state, decoder_final_context_state = tf.contrib.seq2seq.dynamic_rnn_decoder(decoder_cell, 
                                                                                                                test_decoder_function, 
                                                                                                                scope=decoding_scope)
    return test_predictions

# Creating the decoder RNN      
def decoder_rnn(decoder_embadded_input, decoder_embaddings_matrix, encoder_state, num_words, sequence_length, rnn_size, num_layers, word_to_int, keep_prob, batch_size):
    with tf.variable_scope("decoding") as decoding_scope:
        lstm = tf.contrib.rnn.BasicLSTMCell(rnn_size)
        lstm_dropout = tf.contrib.rnn.DropoutWrapper(lstm, input_keep_prob=keep_prob)
        decoder_cell = tf.contrib.rnn.MultiRNNCell([lstm_dropout] * num_layers)
        weights =tf.truncated_normal_initializer(stddev=0.1)
        biases = tf.zeros_initializer()
        output_function = lambda x: tf.contrib.layers.fully_connected(x,
                                                                      num_words,
                                                                      None,
                                                                      scope=decoding_scope,
                                                                      weights_initializer=weights,
                                                                      biases_initializer=biases)
        training_predictions = decode_training_set(encoder_state,
                                                   decoder_cell,
                                                   decoder_embadded_input,
                                                   sequence_length,
                                                   decoding_scope,
                                                   output_function,
                                                   keep_prob,
                                                   batch_size)
        decoding_scope.reuse_variables()
        test_predictions = decode_test_set(encoder_state, 
                                           decoder_cell, 
                                           decoder_embaddings_matrix, 
                                           word_to_int['<SOS>'],
                                           word_to_int['<EOS>'], 
                                           sequence_length-1, 
                                           num_words,
                                           decoding_scope, 
                                           output_function, 
                                           keep_prob, 
                                           batch_size)
    return training_predictions, test_predictions
    
# Building a seq2seq model
def seq2seq_model(inputs, targets, keep_prob, batch_size, sequence_length, answer_num_words, question_num_words, encoder_embadding_size, decoder_embadding_size, rnn_size, num_layers, questionwords_to_int):
    encoder_embadded_input = tf.contrib.layers.embed_sequence(inputs,
                                                              answer_num_words+1,
                                                              encoder_embadding_size,
                                                              initializer=tf.random_uniform_initializer(0, 1))
    encoder_state = encoder_rnn(encoder_embadded_input, rnn_size, num_layers, keep_prob, sequence_length)
    preprocessed_targets = preprocess_targets(targets, questionwords_to_int, batch_size)
    decoder_embaddings_matrix = tf.Variable(tf.random_uniform([question_num_words+1, decoder_embadding_size], 0, 1))
    decoder_embadded_input = tf.nn.embedding_lookup(decoder_embaddings_matrix, preprocessed_targets)
    training_predictions, test_predictions = decoder_rnn(decoder_embadded_input, 
                                                         decoder_embaddings_matrix, 
                                                         encoder_state,
                                                         question_num_words,
                                                         sequence_length,
                                                         rnn_size,
                                                         num_layers,
                                                         questionwords_to_int,
                                                         keep_prob, 
                                                         batch_size)
    return training_predictions, test_predictions
    
    
    
    
    
    
    
    
    