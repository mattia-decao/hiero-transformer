# Load environment
!pip install transformers
!pip install sentencepiece
!pip install datasets

import json
import string
import torch
import pickle
import os
import re
import numpy as np
import shutil
import pandas as pd
import datasets
import transformers
import itertools
import random
from collections import defaultdict
from pprint import pprint
from tqdm.auto import tqdm, trange
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer

# Here you can load the model

# Traduction
#@title Traduction

language_input = 'tnt' #@param ["ea", "tnt"]
language_output = 'de' #@param ["de", "en", "tnt", "lKey", "wordClass"]
sentence_input = '*ra m p,t' #@param {type:"string"}
# resulted_input_tnt = '' #@param {type:"string"}
all_outputs = True #@param {type:"boolean"}

# Se si desidera mettere le maiuscole (per i nomi) basta aggiungere * prima del termine della traslitterazione

if language_input == 'tnt':
  sentence_input = (sentence_input

    .replace('*X', 'H̱')
    .replace('*S', 'Š')
    .replace('*T', 'Ṯ')
    .replace('*D', 'Ḏ')
    .replace('*A', 'Ꜣ')
    .replace('*H', 'Ḥ')

    .replace('X', 'ẖ')
    .replace('S', 'š')
    .replace('T', 'ṯ')
    .replace('D', 'ḏ')
    .replace('A', 'ꜣ')
    .replace('H', 'ḥ')

    .replace('*j', 'J')
    .replace('*i', 'I')
    .replace('*y', 'Y')
    .replace('*a', 'Ꜥ')
    .replace('*w', 'W')
    .replace('*b', 'B')
    .replace('*p', 'P')
    .replace('*f', 'F')
    .replace('*m', 'M')
    .replace('*n', 'N')
    .replace('*r', 'R')
    .replace('*h', 'H')
    .replace('*x', 'Ḫ')
    .replace('*s', 'S')
    .replace('*z', 'Z')
    .replace('*q', 'Q')
    .replace('*k', 'K')
    .replace('*g', 'G')
    .replace('*t', 'T')
    .replace('*d', 'D')
    .replace('a', 'ꜥ')
    .replace('x', 'ḫ')
    .replace ('i', 'i̯')

  )
  print(sentence_input)

lang_to_m2m_lang_id = {
    'ea': 'ar',
    'tnt': 'ar',
    'en': 'en',
    'de': 'de',
    'lKey': 'my',
    'tnt': 'lo',
    'wordClass': 'th',
}

langs = [
 ('ea', 'de'),
 ('ea', 'en'),
 ('ea', 'tnt'),
 ('ea', 'lKey'),
 ('ea', 'wordClass'),
 ('tnt', 'de'),
 ('tnt', 'en'),
 ('tnt', 'lKey'),
 ('tnt', 'wordClass'),
]

def get_translation(language_input, language_output, sentence_input):
  with torch.no_grad():
    with torch.cuda.amp.autocast():
      tokenizer.src_lang = lang_to_m2m_lang_id[language_input]
      tokenizer.tgt_lang = lang_to_m2m_lang_id[language_output]

      model_inputs = tokenizer([sentence_input], return_tensors="pt").to(model.device)
      generated_tokens = model.generate(
          **model_inputs,
          num_beams=10,
          max_length=32,
          forced_bos_token_id=tokenizer.get_lang_id(lang_to_m2m_lang_id[language_output]))
      return tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]

if not all_outputs:
  assert (language_input, language_output) in langs, 'Coppia lingue non valida'
  result =  get_translation(language_input, language_output, sentence_input)
else:
  result = {
      language_output: get_translation(language_input, language_output, sentence_input)
      for language_input_tmp, language_output in langs if language_input == language_input_tmp
  }
result
