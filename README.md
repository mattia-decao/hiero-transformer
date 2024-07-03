# hiero-transformer
## work in progress

Every cleaning operation was meticulously documented along with a concise description highlighting its purpose, implementation, and the rationale behind its choice. These operations were compiled into tables, incorporating the regular symbol expression ".*?" to depict an undefined sequence of words, numbers, and/or graphic symbols.

Furthermore, any text found in the _Subject_ section was retained entirely, including spaces. At the same time, any of our annotations were enclosed within brackets not present in the TLA dataset, specifically "(£" "£)".

The meanings of cleaned characters were primarily derived from the MdC~\citep{MdC} conventions. Others were extracted from the Berlin Text System 3.1 (V 3.0) user manual~\citep{berlin_text_system}.

The management of translations is documented in Table x***, while the handling of transliterations is recorded in Table y***. The processing of Gardiner code is detailed in Table z***, and the treatment of parts of speech is presented in Table k***.


***++tabelle di descrizione delle operazioni di pulizia



## Model functioning tips
Hiero-transformer is a useful tool, but it could generate inaccurate results, especially if the input provided isn't correct. Users need to be aware of this and able to distinguish any potential machine-generated mistakes. To help you get better output using Hiero-transformer, here are some tips. 

### Hieroglyphic input
To provide hieroglyphs to Hiero-transformer, you will need to use the Gardiner code. This code requires some preparation.
- **Cleaning:** Remove any brackets, graphic signs, or letters (which are not part of the hieroglyph) attached to them, like you might see working with Jsesh~{Jsesh}.
- **Separation:** Use spaces to separate individual hieroglyphs and erase any other character.

Keep in mind that the model is trained on Old and Middle Egyptian hieroglyphs. It might struggle with later stages of the language or grammatical forms developed after the Second Intermediate Period.
For best results, we recommend using a sign list like Gardiner's~{gardiner_grammar} or, even better, Allen's~{allen_grammar}.


### Transliteration input
To provide Hiero-transformer with transliteration, you will need to use the same conventions used by the TLA.
- **Capitalization:** Proper nouns need to be capitalized.
- **Hyphens:** You need to use hyphens (-) to separate individual words within proper nouns (e.g., _sḥtp-jb-rꜥ_) or concepts (e.g., _wꜣḏ-wr_). Otherwise, the model will translate them as separate words.
- **Suffix pronouns:** When using the _=_ sign to indicate a suffix pronoun, always add a space before the sign directly followed by the suffix pronoun letters (e.g., _zꜣ =f m pr_).
- **Yod:** The consonant _j_ is used for the strong radical yod, while _i̯_ represents the weak radical yod.
- **Dots:** Use a dot to separate the verb root and the suffixes (other than pronouns). For example, in the form _sḏm.n =f_, the dot separates _sḏm_ (root) from _n_ (suffix other than pronoun). Dots may also be used for plural/dual forms.
- **Commas:** Commas are used for the feminine suffix and may also be used for plural/dual forms.

You can provide characters in transliteration either in Unicode (the standard encoding) or according to the computer transcription of the Manuel de Codage~{manuel_de_codage} (a hieroglyphs-specific encoding system that does not make use of special characters). Furthermore, we ensured the insertion of other characters.
- **Capital letters**: Add an asterisk (*) directly before the letter you want to capitalize. For example, using the MdC system, to get a capitalized _ḏ_, type _*D_ (instead of _D_); similarly, to get a capitalized _d_, type _*d_.
- **Weak radical yod (_i̯_)**: Type _i_ to insert this character.
