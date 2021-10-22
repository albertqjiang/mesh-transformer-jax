import requests
import random
import os
import json
import argparse


def get_candidates(response):
    completions = response["completion"]
    all_candidates = []

    for src, _ in completions:
        src_tokens = [x for x in list(map(
            lambda x: x.replace("\u0120", " ").replace("\\\\", "\\").replace("\u0027", "'").replace("\\\"", "\"").strip(),
            src
        )) if x]
        try:
            endoftext_index = src_tokens.index("<|endoftext|>")
        except ValueError:
            endoftext_index = len(src_tokens)
        src_tokens = src_tokens[:endoftext_index]
        src_string = "".join(src_tokens).strip()
        all_candidates.append(src_string)
    return all_candidates


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--temp", type=float)
    parser.add_argument("--tokens", type=int)
    parser.add_argument("--n", type=int)
    args = parser.parse_args()

    random.seed(0)
    url = 'http://localhost:5000/complete'
    headers = {'Content-Type': 'application/json'}
    data_path = "/home/qj213/seq2seq/seq2seq_with_state"
    src_path = os.path.join(data_path, "val.src")
    tgt_path = os.path.join(data_path, "val.tgt")

    with open(src_path) as src_fhand, open(tgt_path) as tgt_fhand:
        src_lines = src_fhand.readlines()
        tgt_lines = tgt_fhand.readlines()

    src2tgt = dict()
    for src_line, tgt_line in zip(src_lines, tgt_lines):
        src2tgt[src_line.strip().replace("State:", "<ISA_OBS>") + " Cambridge"] = tgt_line.strip()
    # .replace("\\", "\\\\").replace("'", "\u0027").replace("\"", "\\\"")

    src_selected = random.sample(list(src2tgt.keys()), k=3000)
    total_correct_sequences, total_sequences = 0, 0

    for src in src_selected:
        if src:
            tgt = src2tgt[src]

            response = requests.post(url,
                                     json={"context": src,
                                           "top_p": 1.0,
                                           "temp": args.temp,
                                           "gen_tokens": args.tokens,
                                           "n": args.n,
                                           },
                                     headers=headers)
            processed_response = get_candidates(response.json())
            total_sequences += 1
            if tgt in processed_response:
                total_correct_sequences += 1
    print("Sequence accuracy: {}".format(total_correct_sequences/total_sequences))
