from relevanceai.utils import MissingPackageError
from relevanceai.operations_new.base import OperationBase


class CountTextBase(OperationBase):
    _imported_nltk = False

    def __init__(
        self,
        text_fields: list,
        include_char_count: bool = True,
        include_word_count: bool = True,
        include_sentence_count: bool = False,
        output_fields: list = None,
    ):
        self.text_fields = text_fields
        self.include_char_count = include_char_count
        self.include_word_count = include_word_count
        self.include_sentence_count = include_sentence_count
        self.output_fields = output_fields

    def count_characters(self, text):
        return len(text)

    def count_words(self, text):
        return len(text.split())

    def count_sentences(self, text):
        try:
            from sentence_splitter import split_text_into_sentences
        except ModuleNotFoundError:
            raise MissingPackageError("sentence-splitter")
        sentences = split_text_into_sentences(
            text='This is a paragraph. It contains several sentences. "But why," you ask?',
            language="en",
        )
        return len(sentences)

    def count_text_document(self, document):
        output_doc = {"_id": document["_id"]}
        for i, t in enumerate(self.text_fields):
            text = self.get_field(t, document)
            if self.include_char_count:
                self.set_field(
                    t + "_char_count", output_doc, self.count_characters(text)
                )
            if self.include_word_count:
                self.set_field(t + "_word_count", output_doc, self.count_words(text))
            if self.include_sentence_count:
                self.set_field(
                    t + "_sentence_count", output_doc, self.count_sentences(text)
                )
        return output_doc

    def transform(self, documents: list):
        new_docs = [self.count_text_document(d) for d in documents]
        return new_docs
