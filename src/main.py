import os
import sys

import numpy as np
import pandas as pd
import json
import torch
import torch.nn.functional as F
from transformers import BertTokenizer, BertForTokenClassification
import spacy

from predict import predict

def main():
    nlp = spacy.load("de_core_news_lg")

    prefixes = ['\\n', ] + nlp.Defaults.prefixes
    prefix_regex = spacy.util.compile_prefix_regex(prefixes)
    nlp.tokenizer.prefix_search = prefix_regex.search

    with open(os.path.join(sys.path[0], "idx2tag.json"), "r") as json_file:
        idx2tag_str = json.load(json_file)

    tag2idx = {idx2tag_str[key]: int(key) for key in idx2tag_str.keys()}
    idx2tag = {int(key): idx2tag_str[key] for key in idx2tag_str.keys()}

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    tokenizer = BertTokenizer.from_pretrained('bert-base-german-cased', do_lower_case = False)
    model = BertForTokenClassification.from_pretrained("bert-base-german-cased", num_labels = len(tag2idx))
    model.to(device)

    path_to_model = os.path.join(sys.path[0], 'HAWK_3.0.pth')
    model.load_state_dict(torch.load(path_to_model, map_location = device))

    while True:
        print(type(model), type(tokenizer), type(device), type(idx2tag))
        text = input('Write down your text: ')
        tokens, labels = predict(text, model, tokenizer, device, idx2tag)
        for token, label in zip(tokens, labels):
            print("{}\t\t\t{}".format(label, token))

if __name__ == '__main__':
    main()
