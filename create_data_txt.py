import os
import argparse
import random
random.seed(0)


# Token id: 14457; token: Cambridge
# We use this token to separate the source and the target
# It's unlikely to appear in the Isabelle proof corpus as it's the name of a place
# Token id: 50256; token <|endoftext|>

def process(src_path, tgt_path, output_path, mode):
    with open(src_path) as src_fhand, open(tgt_path) as tgt_fhand, open(output_path, "w") as output_fhand:
        src_lines = src_fhand.readlines()
        tgt_lines = tgt_fhand.readlines()

        total_lines = len(src_lines)
        random_order = list(range(total_lines))
        random.shuffle(random_order)
        for index in random_order:
            src_line = src_lines[index]
            tgt_line = tgt_lines[index]
        
            if mode == "state_only":
                output_fhand.write(src_line.strip().replace("State:", "<ISA_OBS>") + " Cambridge " + tgt_line.strip() + " <|endoftext|> ")
            elif mode == "proof_only":
                raise NotImplementedError
            elif mode == "proof_and_state":
                output_fhand.write(
                    src_line.strip().replace("<PS_SEP> State:", "<ISA_OBS>").replace("Proof:", "<ISA_PRF>")
                    + " Cambridge " + tgt_line.strip() + " <|endoftext|> "
                )
            else:
                raise AssertionError


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create the .txt files for fine-tuning from the raw PISA src-tgt pairs.")
    parser.add_argument("--data-dir", type=str, default="",
                        help="Input directory (default: current directory)")
    parser.add_argument("--output-dir", type=str, default="/home/qj213/data",
                        help="Output directory (default: home data directory)")
    parser.add_argument("--name", type=str,
                        help="Name of the currently processed data (state_only, proof_only, proof_and_state).")
    args = parser.parse_args()
    train_src_path = os.path.join(args.data_dir, "train.src")
    train_tgt_path = os.path.join(args.data_dir, "train.tgt")
    assert args.name in ["state_only", "proof_only", "proof_and_state"]
    train_output_path = os.path.join(args.output_dir, "{}_train.txt".format(args.name))
    val_src_path = os.path.join(args.data_dir, "val.src")
    val_tgt_path = os.path.join(args.data_dir, "val.tgt")
    val_output_path = os.path.join(args.output_dir, "{}_val.txt".format(args.name))

    process(train_src_path, train_tgt_path, train_output_path, mode=args.name)
    process(val_src_path, val_tgt_path, val_output_path, mode=args.name)
