# from typing import TYPE_CHECKING

# if TYPE_CHECKING:
from transformers.modeling_outputs import TokenClassifierOutput
import torch

def predict(text, model, tokenizer):
    '''
    Function for token classification.

    in: text, str - text to use for token classification
        model, bert model - model to apply for a text
        tokenizer, bert tokenizer - tokenizer for sentence encoding
    '''
    sentence = tokenizer.encode(text, add_special_tokens = False)
    sentence = torch.tensor([sentence]).to(device)

    with torch.no_grad():
        output: TokenClassifierOutput = model(sentence)
    
    logits: torch.Tensor = output[0]
    labels = np.argmax(logits.to('cpu').numpy(), axis = 2)

    tokens = tokenizer.convert_ids_to_tokens(sentence.to('cpu').numpy()[0])
    new_tokens, new_labels = [], []
    for token, label_idx in zip(tokens, labels[0]):
        if token.startswith("##"):
            new_tokens[-1] = new_tokens[-1] + token[2:]
        else:
            new_labels.append(idx2tag[label_idx][2:])
            new_tokens.append(token)

    return new_tokens, new_labels