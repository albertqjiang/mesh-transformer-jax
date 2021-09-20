import requests
import random
import os
import json


def process_response(response):
    completions = response["completion"][0]
    total_correct_tokens, total_tokens = 0, 0
    total_correct_sequences, total_sequences = 0, 0
    tokens_lengths = []

    for src, tgt in completions:
        src_tokens = list(map(
            lambda x: x.replace("\u0120", " ").replace("\\\\", "\\").replace("\u0027", "'").replace("\\\"", "\"").strip(),
            src
        ))
        tgt_tokens = list(map(
            lambda x: x.replace("\u0120", " ").replace("\\\\", "\\").replace("\u0027", "'").replace("\\\"", "\"").strip(),
            tgt
        ))
        try:
            endoftext_index = src_tokens.index("<|endoftext|>")
        except ValueError:
            endoftext_index = len(src_tokens)
        src_tokens = src_tokens[:endoftext_index]

        tgt_token_length = len(tgt_tokens)
        tokens_lengths.append(tgt_token_length)
        all_tokens = min(len(src_tokens), len(tgt_tokens))
        correct_tokens = 0
        for i in range(all_tokens):
            if src_tokens[i] == tgt_tokens[i]:
                correct_tokens += 1
        total_correct_tokens += correct_tokens
        total_tokens += all_tokens

        src_string = "".join(src_tokens).strip()
        tgt_string = "".join(tgt_tokens).strip()
        if src_string == tgt_string:
            total_correct_sequences += 1
        total_sequences += 1
    return {
        "total_correct_tokens": total_correct_tokens,
        "total_tokens": total_tokens,
        "total_correct_sequences":total_correct_sequences,
        "total_sequences": total_sequences,
        "tokens_lengths": tokens_lengths
    }


if __name__ == "__main__":
    random.seed(0)
    url = 'http://localhost:5000/complete'
    headers = {'content-type': 'application/json'}
    data_path = "/home/qj213/seq2seq/seq2seq_with_state"
    src_path = os.path.join(data_path, "val.src")
    tgt_path = os.path.join(data_path, "val.tgt")

    with open(src_path) as src_fhand, open(tgt_path) as tgt_fhand:
        src_lines = src_fhand.readlines()
        tgt_lines = tgt_fhand.readlines()

    src2tgt = dict()
    for src_line, tgt_line in zip(src_lines, tgt_lines):
        src2tgt[src_line.strip().replace("State:", "<ISA_OBS>") + " <ISA_ACT>"] = tgt_line.strip()
    # .replace("\\", "\\\\").replace("'", "\u0027").replace("\"", "\\\"")

    src_selected = random.sample(list(src2tgt.keys()), k=16)

    total_correct_tokens, total_tokens = 0, 0
    total_correct_sequences, total_sequences = 0, 0
    tokens_lengths = []

    src_batch = []
    tgt_batch = []
    for src in src_selected:
        src_batch.append(src)
        tgt_batch.append(src2tgt[src])

        if len(src_batch) == 8:
            response = requests.post(url,
                                     data={"contexts": src_batch,
                                           "targets": tgt_batch,
                                           "top_p": 0.0,
                                           "temp": 0.0,
                                           "gen_tokens": 64
                                           },
                                     headers=headers)
            processed_response = process_response(response.json())

            src_batch = []
            tgt_batch = []

            total_correct_tokens += processed_response["total_correct_tokens"]
            total_tokens += processed_response["total_tokens"]
            total_correct_sequences += processed_response["total_correct_sequences"]
            total_sequences += processed_response["total_sequences"]
            tokens_lengths.extend(processed_response["token_lengths"])
    print("Sequence acc: {}".format(total_correct_sequences/total_sequences))
    print("Token acc: {}".format(total_correct_tokens/total_tokens))
    json.dump(tokens_lengths, open("token_lengths", "w"))
