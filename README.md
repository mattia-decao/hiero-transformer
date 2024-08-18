# hiero-transformer (work in progress)
This repository collects additional information for our article _Deep Learning Meets Egyptology: a Hieroglyphic Transformer for Translating Ancient Egyptian_ (De Cao et al. 2024). In particular, here you can find:
- the complete list of the cleansing operations used to clean the data before the model training;
- advice on how to enter the input, both from hieroglyphs and transliteration;
- the examples and the analysis of the human evaluation;
- the code we used to clean, train, evaluate and run the data and the model.

The model is also on Huggingface: https://huggingface.co/mattiadc/hiero-transformer

## Cleansing operations

Every cleansing operation was meticulously documented along with a concise description highlighting its purpose, implementation, and the rationale behind its choice. These operations were compiled into tables, incorporating the regular symbol expression ".*?" to depict an undefined sequence of words, numbers, and/or graphic symbols.

Furthermore, any text found in the _Subject_ section was retained entirely, including spaces. At the same time, all of our annotations were enclosed within brackets not present in the TLA dataset, specifically "(£" "£)".

The meanings of the cleaning procedures were derived from the _Manuel de Codage_ (Buurman et al. 1988; Hans Van Den Berg) conventions, the _Berlin Text System 3.1 (V 3.0) user manual_ (Kupreyev and Sperveslage 2011), or realized by us.

The "cleansing_operations.pdf" file contains the management of translations, transliterations, Gardiner code and part-of-speech tags.


## Model functioning tips
Hiero-transformer is a useful tool, but it could generate inaccurate results, especially if the input provided isn't correct. Users need to be aware of this and able to distinguish any potential machine-generated mistakes. To help you get better output using Hiero-transformer, here are some tips. 

### Hieroglyphic input
You will need to use the Gardiner code to provide hieroglyphs to Hiero-transformer. This code requires some preparation.
- **Cleaning:** Remove any brackets, graphic signs, or letters (which are not part of the hieroglyph) attached to them, like you might see working with Jsesh (Rosmorduc).
- **Separation:** Use spaces to separate individual hieroglyphs and erase any other character.

Remember that the model is trained on Old and Middle Egyptian hieroglyphs. It might struggle with later stages of the language or grammatical forms developed after the Second Intermediate Period.
For best results, we recommend using a sign list like Gardiner's (Gardiner 1957) or, even better, Allen's (Allen 2014).


### Transliteration input
To provide Hiero-transformer with transliteration, you will need to use the same conventions used by the TLA.
- **Capitalization:** Proper nouns need to be capitalized.
- **Hyphens:** You need to use hyphens (-) to separate individual words within proper nouns (e.g., _sḥtp-jb-rꜥ_) or concepts (e.g., _wꜣḏ-wr_). Otherwise, the model will translate them as separate words.
- **Suffix pronouns:** When using the _=_ sign to indicate a suffix pronoun, always add a space before the sign directly followed by the suffix pronoun letters (e.g., _zꜣ =f m pr_).
- **Yod:** The consonant _j_ is used for the strong radical yod, while _i̯_ represents the weak radical yod.
- **Dots:** Use a dot to separate the verb root and the suffixes (other than pronouns). For example, in the form _sḏm.n =f_, the dot separates _sḏm_ (root) from _n_ (suffix other than pronoun). Dots may also be used for plural/dual forms.
- **Commas:** Commas are used for the feminine suffix and may also be used for plural/dual forms.

You can provide characters in transliteration either in Unicode (the standard encoding) or according to the computer transcription of the Manuel de Codage (a hieroglyphs-specific encoding system that does not make use of special characters). Furthermore, we ensured the insertion of other characters.
- **Capital letters**: Add an asterisk (*) directly before the letter you want to capitalize. For example, using the MdC system, to get a capitalized _ḏ_, type _*D_ (instead of _D_); similarly, to get a capitalized _d_, type _*d_.
- **Weak radical yod ( _i̯_ )**: Type _i_ to insert this character.


## Human evaluation examples and analysis
As soon as possible, we will add a PDF file in which we have analyzed all the examples we worked on.


## References

Mattia De Cao, Nicola De Cao, Angelo Colonna, and Alessandro Lenci. 2024. Deep Learning Meets Egyptology: a Hieroglyphic Transformer for Translating Ancient Egyptian. In _Proceedings of the 1st Workshop on Machine Learning for Ancient Languages (ML4AL 2024)_, pages 71–86, Hybrid in Bangkok, Thailand and online. Association for Computational Linguistics.

Jan Buurman, Nicolas-Christophe Grimal, Michale Hainsworth, Jochen Hallof, and Dirk Van der Plas. 1988. Inventaire des signes hieroglyphiques en vue de leur saisie informatique: Manuel de codage des textes  ieroglyphiques en vue de leur saisie sur ordinateur, volume 2 of Informatique et egyptologie. Imprimerie Lienharte et Cie.; Difussion Boccard, Paris.

Hans Van Den Berg, _“Manuel de Codage” A standard system for the computerencoding of Egyptian transliteration and hieroglyphic texts_, <http://www.catchpenny.org/codage/> (last access: 28 July 2023).

Maxim Kupreyev and Gunnar Sperveslage. 2011.  _Berlin Text System 3.1 User Manual: Editorial Software of the Thesaurus Linguae Aegyptiae Project_.

Alan H. Gardiner. 1957. _Egyptian Grammar, Being an Introduction to the Study of Hieroglyphs_, third edition. Griffith Institute, Oxford.

James P. Allen. 2014. _Middle Egyptian: An Introduction to the Language and Culture of Hieroglyphs_, 3 edition. Cambridge University Press.

Serge Rosmorduc, _JSesh Documentation_, <http://jseshdoc.qenherkhopeshef.org> (last access 09 September 2023).
