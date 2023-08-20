import copy
import json
import shutil

import numpy as np
import torch
from tqdm.auto import tqdm
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer

from utils import (
    batch_it,
    clean_data,
    lang_to_m2m_lang_id,
    load_data_from_folder,
    processed_data,
    training_step,
    validation_step,
)

# Epochs, batch, periods variables
epochs = 20
batch_size = 16
eval_period = 1000
total_steps = 0
best_eval_loss = float("inf")
max_models = 1
topk_models = []

# Choose the pairs of languages to train and validate
langs = [
    ("ea", "de"),
    ("ea", "en"),
    #  ('ea', 'tnt'),
    #  ('ea', 'lKey'),
    #  ('ea', 'wordClass'),
    #  ('tnt', 'de'),
    #  ('tnt', 'en'),
    #  ('tnt', 'lKey'),
    #  ('tnt', 'wordClass'),
]


# Load data
training_data = load_data_from_folder("training_data")
validation_data = load_data_from_folder("validation_data")

# Clean data
training_data = clean_data(training_data)

# Filter and extract data
# Dict[str, Dict[str, List[Dict[str, str]]]]
# {src_lang: {tgt_lang: [{'source': ..., 'target': ...}]}}
training_data = processed_data(training_data)
validation_data = processed_data(validation_data)


# Adding traduction of corpus and vocabulary

with open("translations_de2en.json", encoding="utf-8") as f:
    translations = json.load(f)

for lang in ("ea", "tnt"):
    ids_sentence = {
        element["metadata"]["id_sentence"]
        for element in training_data[lang]["en"]
        if "id_sentence" in element["metadata"]
    }

    for element in training_data[lang]["de"]:
        if (
            "id_sentence" in element["metadata"]
            and element["metadata"]["id_sentence"] not in ids_sentence
        ):
            new_element = copy.deepcopy(element)
            new_element["target"] = translations[element["target"]]
            new_element["metadata"]["target_lang"] = "en"
            training_data[lang]["en"].append(new_element)

    print(
        f'{lang} -> en: Dopo la traduzione abbiamo {len(training_data[lang]["en"])} datapoints.'
    )

# loading model
model = M2M100ForConditionalGeneration.from_pretrained("facebook/m2m100_418M").to(
    "cuda:0"
)
tokenizer = M2M100Tokenizer.from_pretrained("facebook/m2m100_418M")
optimizer = torch.optim.Adam(model.parameters(), lr=3e-5)


# Training
validation_losses = {}
validation_data_batched = [
    (src_lang, trg_lang, batch)
    for src_lang, values in validation_data.items()
    for trg_lang, data in values.items()
    for batch in batch_it(data, batch_size)
    if (src_lang, trg_lang) in langs
]

for epoch in range(epochs):
    print(f"Starting epoch {epoch + 1}")

    for src_lang, values in training_data.items():
        for data in values.values():
            np.random.shuffle(data)

    training_data_batched = [
        (src_lang, trg_lang, batch)
        for src_lang, values in training_data.items()
        for trg_lang, data in values.items()
        for batch in batch_it(data, batch_size)
        if (src_lang, trg_lang) in langs
    ]

    np.random.shuffle(training_data_batched)

    iterator = tqdm(training_data_batched)
    for src_lang, tgt_lang, batch in iterator:
        loss = training_step(
            batch,
            model,
            tokenizer,
            optimizer,
            lang_to_m2m_lang_id[src_lang],
            lang_to_m2m_lang_id[tgt_lang],
        )
        total_steps += 1
        iterator.set_postfix(
            total_steps=total_steps, loss=loss, src_lang=src_lang, tgt_lang=tgt_lang
        )

        if total_steps % eval_period == 0 and total_steps != 0:
            total_eval_loss = 0
            total_eval_tokens = 0

            for src_lang, tgt_lang, batch in validation_data_batched:
                loss, tokens = validation_step(
                    batch,
                    model,
                    tokenizer,
                    lang_to_m2m_lang_id[src_lang],
                    lang_to_m2m_lang_id[tgt_lang],
                )
                total_eval_loss += loss * tokens
                total_eval_tokens += tokens

            validation_losses[total_steps] = total_eval_loss
            with open("validation_losses.json", "w") as f:
                json.dump(validation_losses, f)

            if total_eval_loss < best_eval_loss:
                print(
                    f"The model improved! Old loss={best_eval_loss}, new loss={total_eval_loss}"
                )
                fname = f"checkpoint_total_steps={total_steps}_loss={total_eval_loss / total_eval_tokens:.2f}"
                model.save_pretrained(fname)
                topk_models.append(fname)
                best_eval_loss = total_eval_loss

                if len(topk_models) > max_models:
                    fname = topk_models.pop(0)
                    shutil.rmtree(fname)
                    print(f"Removing {fname}")

# Last check before the end
total_eval_loss = 0
total_eval_tokens = 0

for src_lang, tgt_lang, batch in validation_data_batched:
    loss, tokens = validation_step(
        batch,
        model,
        tokenizer,
        lang_to_m2m_lang_id[src_lang],
        lang_to_m2m_lang_id[tgt_lang],
    )
    total_eval_loss += loss * tokens
    total_eval_tokens += tokens

    validation_losses[total_steps] = total_eval_loss
    with open("validation_losses.json", "w") as f:
        json.dump(validation_losses, f)

    if total_eval_loss < best_eval_loss:
        print(
            f"The model improved! Old loss={best_eval_loss}, new loss={total_eval_loss}"
        )
        fname = f"checkpoint_total_steps={total_steps}_loss={total_eval_loss / total_eval_tokens:.2f}"
        model.save_pretrained(fname)
        topk_models.append(fname)
        best_eval_loss = total_eval_loss

        if len(topk_models) > max_models:
            fname = topk_models.pop(0)
            shutil.rmtree(fname)
            print(f"Removing {fname}")
