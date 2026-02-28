#!/usr/bin/env python3
"""
Minimal wiring of Hugging Face Arabic Wav2Vec2-CTC emissions with GTN
for constrained CTC loss using optional Arabic diacritic insertions.

Usage:
  python bindings/python/examples/wav2vec2_arabic_ctc_gtn.py \
    --audio path/to/audio.wav \
    --target "سلام"
"""

import argparse
from pathlib import Path

import numpy as np
import torch
import torchaudio
import gtn
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor


DEFAULT_MODEL_ID = "jonatasgrosman/wav2vec2-large-xlsr-53-arabic"
ARABIC_DIACRITICS = ["َ", "ً", "ُ", "ٌ", "ِ", "ٍ", "ْ", "ّ"]


def load_audio_16k(path):
    wav, sr = torchaudio.load(path)
    if wav.size(0) > 1:
        wav = wav.mean(dim=0, keepdim=True)
    if sr != 16000:
        wav = torchaudio.functional.resample(wav, sr, 16000)
    return wav.squeeze(0)


def build_emissions_graph(log_probs):
    """
    log_probs: np.ndarray of shape [T, V], log-softmax probabilities.
    """
    t, v = log_probs.shape
    g = gtn.linear_graph(t, v, calc_grad=False)
    g.set_weights(log_probs.astype(np.float32).reshape(-1))
    return g


def create_ctc_target_graph(target_ids, blank_idx):
    """
    Standard CTC target graph: # y1 # y2 # ... # yL #
    """
    l = len(target_ids)
    u = 2 * l + 1
    g = gtn.Graph(False)
    for p in range(u):
        idx = (p - 1) // 2
        g.add_node(p == 0, p == u - 1 or p == u - 2)
        label = target_ids[idx] if p % 2 else blank_idx

        g.add_arc(p, p, label)
        if p > 0:
            g.add_arc(p - 1, p, label)
        if p % 2 and p > 1 and label != target_ids[idx - 1]:
            g.add_arc(p - 2, p, label)
    return g


def build_optional_diacritic_wfst(ctc_symbols, base_symbol_ids, diacritic_ids):
    """
    Input labels: symbols from the CTC target graph.
    Output labels: same symbols, with optional diacritic insertion after base symbols.
    """
    g = gtn.Graph(False)
    s0 = g.add_node(True, True)
    s1 = g.add_node(False, False)

    base_set = set(base_symbol_ids)

    for sym in ctc_symbols:
        if sym in base_set:
            g.add_arc(s0, s1, sym, sym, 0.0)
        else:
            g.add_arc(s0, s0, sym, sym, 0.0)

    for d in diacritic_ids:
        g.add_arc(s1, s0, gtn.epsilon, d, 0.0)
    g.add_arc(s1, s0, gtn.epsilon, gtn.epsilon, 0.0)
    return g


def tokenize_target(processor, target_text):
    ids = processor.tokenizer(target_text, add_special_tokens=False).input_ids
    if not ids:
        raise ValueError("Target text tokenized to empty sequence.")
    return ids


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--audio", type=str, required=True, help="Path to wav/flac/ogg audio.")
    parser.add_argument("--target", type=str, required=True, help="Arabic target text (typically undiacritized).")
    parser.add_argument("--model_id", type=str, default=DEFAULT_MODEL_ID, help="HF model id.")
    args = parser.parse_args()

    audio_path = Path(args.audio)
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio not found: {audio_path}")

    print(f"Loading model: {args.model_id}")
    processor = Wav2Vec2Processor.from_pretrained(args.model_id)
    model = Wav2Vec2ForCTC.from_pretrained(args.model_id).eval()

    blank_idx = model.config.pad_token_id
    if blank_idx is None:
        raise RuntimeError("Model has no pad_token_id; cannot infer CTC blank index.")

    wav = load_audio_16k(str(audio_path))
    inputs = processor(wav.numpy(), sampling_rate=16000, return_tensors="pt")

    with torch.no_grad():
        logits = model(inputs.input_values).logits[0]  # [T, V]
        log_probs = torch.log_softmax(logits, dim=-1).cpu().numpy()

    # Simple greedy decode for reference
    pred_ids = torch.argmax(logits, dim=-1).unsqueeze(0)
    pred_text = processor.batch_decode(pred_ids)[0]
    print("Greedy decode:", pred_text)

    target_ids = tokenize_target(processor, args.target)
    print("Target ids:", target_ids)

    # Collect available diacritic token ids from tokenizer vocab.
    vocab = processor.tokenizer.get_vocab()
    inv_vocab = {idx: tok for tok, idx in vocab.items()}
    diacritic_ids = sorted({vocab[d] for d in ARABIC_DIACRITICS if d in vocab})
    print("Diacritic ids available in vocab:", diacritic_ids)

    # Build GTN graphs
    emissions = build_emissions_graph(log_probs)
    ctc_target = create_ctc_target_graph(target_ids, blank_idx=blank_idx)

    vanilla_alignments = gtn.compose(ctc_target, emissions)
    vanilla_loss = gtn.negate(gtn.forward_score(vanilla_alignments))

    # Constrained CTC: allow optional diacritic insertion after target base symbols
    ctc_symbols = sorted(set([blank_idx] + target_ids))
    diacritic_wfst = build_optional_diacritic_wfst(
        ctc_symbols=ctc_symbols,
        base_symbol_ids=target_ids,
        diacritic_ids=diacritic_ids,
    )

    constrained_target = gtn.compose(ctc_target, diacritic_wfst)
    constrained_alignments = gtn.compose(constrained_target, emissions)
    constrained_loss = gtn.negate(gtn.forward_score(constrained_alignments))

    print(f"Vanilla CTC loss      : {vanilla_loss.item():.4f}")
    print(f"Constrained CTC loss  : {constrained_loss.item():.4f}")

    # Optional DOT export for inspection
    symbols = {i: inv_vocab.get(i, str(i)) for i in ctc_symbols + diacritic_ids}
    symbols[gtn.epsilon] = "ε"
    gtn.draw(diacritic_wfst, "arabic_optional_diacritic_wfst.dot", symbols, symbols)
    print("Wrote: arabic_optional_diacritic_wfst.dot")


if __name__ == "__main__":
    main()
