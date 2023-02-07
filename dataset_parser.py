import argparse
import logging
import os
import sys
import re

import srsly
import spacy
from spacy.training import offsets_to_biluo_tags
from spacy.training.iob_utils import spans_from_biluo_tags
from spacy.tokens import Doc

import warnings
warnings.filterwarnings("error")

NLP = spacy.load("en_core_web_sm")


def normalize_label(entity_text: str, text: str, label: str):
    """
    Normalizes labels in spacy format \n
    :param entity_text: the text containing the entity
    :param text: text in which entities are searched
    :param label: entity label
    :return: list of lists of the following format: [start index entity, end index entity, entity label]
    """
    return [[i.start(), i.start() + len(entity_text), label] for i in re.finditer(entity_text, text, 1)]


def convert_spacy_to_bert(spacy_format: dict):
    """
    Converts a dictionary in spacy format to a string in bert format \n
    :param spacy_format: dictionary in spacy format
    :return: string in bert format
    """
    text = spacy_format['text']
    doc = NLP.make_doc(text)

    try:
        tags = offsets_to_biluo_tags(doc, spacy_format['label'])
    except Warning:
        labeled_entities = [[text[start - 1:end].strip(' .,!?\\-/()[]{};:'), label]
                            for start, end, label in spacy_format['label']]
        labels = []
        for entity in labeled_entities:
            label = normalize_label(entity[0], text, entity[1])
            if label[0] not in labels:
                labels.append(label)
        labels = sorted(labels, key=lambda elem: elem[0])
        tags = offsets_to_biluo_tags(doc, labels)

    entities = spans_from_biluo_tags(doc, tags)
    doc.ents = entities

    bert_format = ''
    for token in doc:
        if token.text == ' ':
            continue
        if token.ent_iob_ == 'O':
            bert_format += f'{token.text} {token.ent_iob_}\n'
        else:
            bert_format += f'{token.text} {token.ent_iob_}-{token.ent_type_}\n'

    return bert_format


def read_bert_split_into_texts(source_file: str):
    """
    Reads txt files and converts each text of bert format into one separate line \n
    :param source_file: path to the file with bert dataset
    :return: list of bert format strings
    """
    bert_format = []
    with open(source_file, "r") as file:
        text = ''
        line = file.readline().rstrip('\n')
        while line:
            text += f'{line} '
            line = file.readline()
            if line == '\n':
                text = text.replace('\n', '')
                bert_format.append(text)
                text = ''

    return bert_format


def read_bert_in_one_line(source_file: str):
    """
    Reads txt files and join text of bert format into one line \n
    :param source_file: path to the file with bert dataset
    :return: list of bert format strings
    """
    bert_format = []
    with open(source_file, "r") as file:
        text = ''
        line = file.readline()
        while line:
            text += line
            line = file.readline()
    text = text.replace('\n', ' ')
    bert_format.append(text)
    return bert_format


def convert_bert_to_spacy(bert_format: str, data_id: int):
    """
    converts text in best format to dictionary in spacy format \n
    :param bert_format: string in bert format
    :param data_id: number of current bert text
    :return: dictionary of spacy format
    """

    bert_format = bert_format.split()
    words = [bert_format[i] for i in range(0, len(bert_format), 2)]
    iob_tokens = [bert_format[i] for i in range(1, len(bert_format), 2)]

    doc = Doc(NLP.vocab, words=words, ents=iob_tokens)

    labels = [[ent.start_char, ent.end_char, ent.label_] for ent in doc.ents]
    return {'id': data_id, 'text': doc.text, 'label': labels}


def parse_spacy_to_bert_format(source_file: str, result_file: str):
    """
    parses dataset in spacy format from source_file and based on it writes dataset in bert format in result_file \n
    :param source_file: path to source file containing spacy dataset
    :param result_file: path to the file to which bert dataset is written
    :return:
    """
    logging.info(f"Start converting dataset from spacy-NER to BERT-NER format...")
    source_dataset = srsly.read_jsonl(os.getcwd() + '/' + source_file)
    with open(os.getcwd() + '/' + result_file, "w") as file_stream:
        for data in source_dataset:
            file_stream.write(f'{convert_spacy_to_bert(data)}\n')
    logging.info(f"Process finished. Result file saved to {result_file}")


def parse_bert_to_spacy_format(source_file: str, result_file: str):
    """
    parses dataset in bert format from source_file and based on it writes dataset in space format in result_file \n
    :param source_file: path to source file containing bert dataset
    :param result_file: path to the file to which spacy dataset is written
    :return:
    """
    logging.info(f"Start converting dataset from BERT-NER to spacy-NER format...")
    source_dataset = read_bert_split_into_texts(source_file)
    result_dataset = []
    for data_id in range(len(source_dataset)):
        result_dataset.append(convert_bert_to_spacy(source_dataset[data_id], data_id))
    srsly.write_jsonl(os.getcwd() + '/' + result_file, result_dataset)
    logging.info(f"Process finished. Result file saved to {result_file}")


def main(options):
    if options.spacy_to_bert:
        parse_spacy_to_bert_format(source_file=options.source, result_file=options.result)

    elif options.bert_to_spacy:
        parse_bert_to_spacy_format(source_file=options.source, result_file=options.result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Dataset Converter",
        description="This program converts spacy-NER dataset to BERT-NER dataset and conversely")
    parser.add_argument("-s", "--source", action="store",
                        help="Path to source file for parsing")
    parser.add_argument("-r", "--result", action="store",
                        help="Path to result file of parsing")
    parser.add_argument("--spacy_to_bert", action="store", type=bool, default=False,
                        help="Flag of using spacy to bert dataset parsing")
    parser.add_argument("--bert_to_spacy", action="store", type=bool, default=False,
                        help="Flag of using bert to spacy dataset parsing")
    parser.add_argument("--dry", action="store_true", default=False,
                        help="Flag of dry run. If True, use log level - DEBUG")
    parser.add_argument("-l", "--log", action="store", default=None,
                        help="File name of log file")
    args = parser.parse_args()

    logging.basicConfig(filename=args.log, level=logging.INFO if not args.dry else logging.DEBUG,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')

    logging.info(f"Dataset Converter started with options: {args.__dict__}")
    try:
        main(args)
    except Exception as e:
        logging.exception(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)
