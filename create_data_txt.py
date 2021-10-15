import os
import argparse


# Token id: 14457; token: Cambridge
# We use this token to separate the source and the target
# It's unlikely to appear in the Isabelle proof corpus as it's the name of a place

def process(src_path, tgt_path, output_path):
    with open(src_path) as src_fhand, open(tgt_path) as tgt_fhand, open(output_path, "w") as output_fhand:
        src_lines = src_fhand.readlines()
        tgt_lines = tgt_fhand.readlines()
        for src_line, tgt_line in zip(src_lines, tgt_lines):
            output_fhand.write(
                src_line.strip().replace("State:", "<ISA_OBS>") + " Cambridge " + tgt_line.strip() + " <|endoftext|> "
            )


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
    train_output_path = os.path.join(args.output_dir, "{}_train.txt".format(args.name))
    val_src_path = os.path.join(args.data_dir, "val.src")
    val_tgt_path = os.path.join(args.data_dir, "val.tgt")
    val_output_path = os.path.join(args.output_dir, "{}_val.txt".format(args.name))

    process(train_src_path, train_tgt_path, train_output_path)
    process(val_src_path, val_tgt_path, val_output_path)
