import common



class IPreprocessor:
    @staticmethod
    def preprocess(code: str) -> str:
        moditify = ""
        for i in
        return code




code = """import nltk
 from nltk.stem import PorterStemmer
 porter_stemmer=PorterStemmer()
 words=["connect","connected","connection","connections","connects"]
 stemmed_words=[porter_stemmer.stem(word) for word in words]
 stemmed_words"""

for tok in tokenize(BytesIO(code.encode('utf-8')).readline):
    print(f"Type: {tok.type}\nString: {tok.string}\nStart: {tok.start}\nEnd: {tok.end}\nLine: {tok.line.strip()}\n======\n")