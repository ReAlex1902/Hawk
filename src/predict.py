from typing import TYPE_CHECKING, Union
import torch
import numpy as np

if TYPE_CHECKING:
    from transformers.modeling_outputs import TokenClassifierOutput
    from transformers.models.bert.modeling_bert import BertForTokenClassification
    from transformers.models.bert.tokenization_bert import BertTokenizer

def predict(text: 'str', 
            model: 'BertForTokenClassification', 
            tokenizer: 'BertTokenizer', 
            device: 'torch.device', 
            idx2tag: 'dict', 
            include_null_tags: 'bool' = False) -> Union['list', 'list']:
    '''
    Function for token classification.

    in: text, str - text to use for token classification
        model, BertForTokenClassification - model to apply for a text
        tokenizer, BertTokenizer - tokenizer for sentence encoding
        device, torch.device - device to use for predicting
        idx2tag, dict - dictionary to transform predicted indices to tags
        include_null_tags, bool - either to include tokens with tags 'O' or not
    
    out: 
    '''

    sentence = tokenizer.encode(text, add_special_tokens = False)
    sentence = torch.tensor([sentence]).to(device)

    with torch.no_grad():
        output: 'TokenClassifierOutput' = model(sentence)
    
    logits: 'torch.Tensor' = output[0]
    tags = np.argmax(logits.to('cpu').numpy(), axis = 2)

    tokens = tokenizer.convert_ids_to_tokens(sentence.to('cpu').numpy()[0])
    new_tokens, new_tags = [], []
    prev_label = ''
    for token, label_idx in zip(tokens, tags[0]):
        current_label = idx2tag[label_idx]
        if include_null_tags == True or (include_null_tags == False and current_label != 'O'):
            if token.startswith("##") and len(new_tokens) > 0:
                new_tokens[-1] += token[2:]
            elif prev_label == current_label[2:]:
                prev_label = current_label[2:]
                new_tokens[-1] += ' ' + token
            else:
                prev_label = current_label[2:]
                new_tags.append(current_label[2:])
                new_tokens.append(token)

    return new_tokens, new_tags