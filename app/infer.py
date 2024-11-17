import pickle
import re
import sys

import fire
import nltk
import pandas as pd
import pymorphy3
from nltk.corpus import stopwords
from spellchecker import SpellChecker
from tqdm import tqdm

tqdm.pandas()


class LogRegClassifier:
    def __init__(self):
        with open("./models/logreg.pickle", "rb") as fs:
            self.model = pickle.load(fs)

        with open("./models/tfidf-vectorizer.pickle", "rb") as fs:
            self.vectorizer = pickle.load(fs)

        # Загрузка стоп-слов
        nltk.download("stopwords")
        nltk.download("punkt")

        # Инициализация инструментов
        self.stopwords_ru = set(stopwords.words("russian"))
        self.morph = pymorphy3.MorphAnalyzer()
        self.spell = SpellChecker(language="ru")

        self.category_map = {
            "BANK_SERVICE": 0,
            "FOOD_GOODS": 1,
            "NON_FOOD_GOODS": 2,
            "LEASING": 3,
            "LOAN": 4,
            "REALE_STATE": 5,
            "SERVICE": 6,
            "TAX": 7,
            "NOT_CLASSIFIED": 8,
        }

    def preprocess_text(self, text: str) -> str:
        if not isinstance(text, str):  # Проверяем, что текст не NaN
            return ""

        # Удаление цифр и знаков препинания
        text = re.sub(r"[^\w\s]", "", text)
        text = re.sub(r"\d+", "", text)

        # Исправление опечаток
        words = text.lower().split()
        corrected_words = [
            self.spell.correction(word) if word in self.spell else word
            for word in words
        ]

        # Приведение к начальной форме и удаление стоп-слов
        lemmatized_words = [
            self.morph.parse(word)[0].normal_form
            for word in corrected_words
            if word is not None
        ]
        filtered_words = [
            word for word in lemmatized_words if word not in self.stopwords_ru
        ]

        return " ".join(filtered_words)

    def predict(
        self,
        data: pd.DataFrame,
        purpose_col_name: str = "purpose",
        *,
        preprocess: bool = True,
    ) -> pd.DataFrame:
        if preprocess:
            print("\nPREPROCESSING...", file=sys.stderr)
            data[purpose_col_name] = data[purpose_col_name].progress_apply(
                self.preprocess_text
            )

        X = self.vectorizer.transform(data[purpose_col_name])

        y_pred = self.model.predict(X)

        # Заменяем числа на категории
        reverse_category_map = {v: k for k, v in self.category_map.items()}
        categories = [reverse_category_map.get(num, "UNKNOWN") for num in y_pred]

        return pd.DataFrame({"Index": range(len(categories)), "Category": categories})


def main(input_path: str, output_path: str | None = None):
    model = LogRegClassifier()
    data = pd.read_csv(
        input_path,
        sep="\t",
        names=["index", "date", "amount", "purpose"],
        header=None,
    )
    predicts = model.predict(data)
    for idx, label in predicts.values:
        print(f"{idx}\t{label}")
    if output_path:
        predicts.to_csv(output_path, sep="\t", header=False, index=False)


if __name__ == "__main__":
    fire.Fire(main)
