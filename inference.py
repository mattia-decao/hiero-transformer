import string

import datasets
import pandas as pd
import torch
from tqdm.auto import tqdm
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer

from utils import lang_to_m2m_lang_id, load_data_from_folder, processed_data

# Load data
test_data = load_data_from_folder("test_data")

# Filter and extract data
# Dict[str, Dict[str, List[Dict[str, str]]]]
# {src_lang: {tgt_lang: [{'source': ..., 'target': ...}]}}
test_data = processed_data(test_data)


# Load model to generate predictions
model = M2M100ForConditionalGeneration.from_pretrained("ea9all").to("cuda:0").eval()
tokenizer = M2M100Tokenizer.from_pretrained("facebook/m2m100_418M")

# Produce predictions
for src_lang, values in test_data.items():
    for tgt_lang, data in values.items():
        for element in tqdm(data):
            with torch.no_grad():
                with torch.cuda.amp.autocast():
                    tokenizer.src_lang = lang_to_m2m_lang_id[src_lang]
                    tokenizer.tgt_lang = lang_to_m2m_lang_id[tgt_lang]

                    model_inputs = tokenizer(
                        [element["source"]], return_tensors="pt"
                    ).to(model.device)
                    generated_tokens = model.generate(
                        **model_inputs,
                        num_beams=10,
                        forced_bos_token_id=tokenizer.get_lang_id(
                            lang_to_m2m_lang_id[tgt_lang]
                        )
                    )
                    element["prediction"] = tokenizer.batch_decode(
                        generated_tokens, skip_special_tokens=True
                    )[0]

# Calculate metrics
metrics = {
    src_lang: {
        tgt_lang: {m: datasets.load_metric(m) for m in ("sacrebleu", "rouge")}
        for tgt_lang, _ in values.items()
    }
    for src_lang, values in test_data.items()
}
for src_lang, values in test_data.items():
    for tgt_lang, data in values.items():
        for element in data:
            for metric in metrics[src_lang][tgt_lang].values():
                metric.add_batch(
                    predictions=[
                        element["prediction"].strip(string.punctuation).lower().split()
                    ],
                    references=[
                        [element["target"].strip(string.punctuation).lower().split()]
                    ],
                )

metrics = {
    src_lang: {
        tgt_lang: {name: metric.compute() for name, metric in metrics.items()}
        for tgt_lang, metrics in values.items()
    }
    for src_lang, values in metrics.items()
}

# Compute tables
tables = {
    "sacrebleu": {
        src_lang: {
            tgt_lang: metric["sacrebleu"]["score"]
            for tgt_lang, metric in values.items()
        }
        for src_lang, values in metrics.items()
    },
    "rougeL": {
        src_lang: {
            tgt_lang: 100 * metric["rouge"]["rougeL"].mid.fmeasure
            for tgt_lang, metric in values.items()
        }
        for src_lang, values in metrics.items()
    },
}

print("sacrebleu")
print(pd.DataFrame(tables["sacrebleu"]).T)
print("rougeL")
print(pd.DataFrame(tables["rougeL"]).T)
