import os
os.system('pip install -r requirements.txt ')
os.system('python -m spacy download de_core_news_lg')

import numpy as np
import pandas as pd
import json
import torch
import torch.nn.functional as F
from transformers import BertTokenizer, BertForTokenClassification
import spacy

nlp = spacy.load("de_core_news_lg")

prefixes = ['\\n', ] + nlp.Defaults.prefixes
prefix_regex = spacy.util.compile_prefix_regex(prefixes)
nlp.tokenizer.prefix_search = prefix_regex.search

with open('idx2tag.json') as json_file:
    idx2tag_str = json.load(json_file)

tag2idx = {idx2tag_str[key]: int(key) for key in idx2tag_str.keys()}
idx2tag = {int(key): idx2tag_str[key] for key in idx2tag_str.keys()}

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
tokenizer = BertTokenizer.from_pretrained('bert-base-german-cased', do_lower_case = False)

model = BertForTokenClassification.from_pretrained("bert-base-german-cased", num_labels = len(tag2idx))
model.to(device)

PATH_TO_MODEL = input('Write the path to the pretrained BERT model: ')
model.load_state_dict(torch.load(PATH_TO_MODEL, map_location = device))

def predict(text, model = model, tokenizer = tokenizer):
    '''
    Function for token classification.

    in: text, str - text to use for token classification
        model, bert model - model to apply for a text
        tokenizer, bert tokenizer - tokenizer for sentence encoding
    '''
    sentence = tokenizer.encode(text, add_special_tokens = False)
    sentence = torch.tensor([sentence]).to(device)

    with torch.no_grad():
        logits = model(sentence)
    
    labels = np.argmax(logits[0].to('cpu').numpy(), axis = 2)

    tokens = tokenizer.convert_ids_to_tokens(sentence.to('cpu').numpy()[0])
    new_tokens, new_labels = [], []
    for token, label_idx in zip(tokens, labels[0]):
        if token.startswith("##"):
            new_tokens[-1] = new_tokens[-1] + token[2:]
        else:
            new_labels.append(idx2tag[label_idx][2:])
            new_tokens.append(token)

    for token, label in zip(new_tokens, new_labels):
        print("{}\t\t\t{}".format(label, token))

if __name__ == '__main__':
    while True:
        text = input('Write down your text: ')
        predict(text)