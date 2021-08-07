import os
import sys

import numpy as np
import pandas as pd
import json
import torch
from transformers import BertTokenizer, BertForTokenClassification, logging

from predict import predict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from transformers.models.bert.tokenization_bert import BertTokenizer
    from transformers.models.bert.modeling_bert import BertForTokenClassification

def main():
    logging.set_verbosity_error()
    
    with open(os.path.join(sys.path[0], "idx2tag.json"), "r") as json_file:
        idx2tag_str = json.load(json_file)

    tag2idx = {idx2tag_str[key]: int(key) for key in idx2tag_str.keys()}
    idx2tag = {int(key): idx2tag_str[key] for key in idx2tag_str.keys()}

    with open(os.path.join(sys.path[0], "character_map.json"), "r") as json_file:
        charachter_map = json.load(json_file)

    device: torch.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    tokenizer: 'BertTokenizer' = BertTokenizer.from_pretrained('bert-base-german-cased', do_lower_case = False)
    model: 'BertForTokenClassification' = BertForTokenClassification.from_pretrained('bert-base-german-cased', num_labels = len(tag2idx))
    model: 'BertForTokenClassification' = model.to(device)

    path_to_model = os.path.join(sys.path[0], 'HAWK_3.0.pth')
    model.load_state_dict(torch.load(path_to_model, map_location = device))

    while True:
        text = input('Write down your text: ')
        tokens, labels = predict(text, model, tokenizer, device, idx2tag, charachter_map)
        for token, label in zip(tokens, labels):
            # print("{}\t\t\t{}".format(label, token))
            print('{0:25}  {1}'.format(label, token))

if __name__ == '__main__':
    main()
