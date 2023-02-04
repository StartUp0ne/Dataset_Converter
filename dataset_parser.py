import argparse
import logging
import re
import sys

import srsly
import spacy

NLP = spacy.load("en_core_web_sm")


def split_spacy_text(text: str):
    """
    Separates punctuation marks from words and divides text into single words and punctuation marks \n
    :param text: one line of type string
    :return: list of single words and other symbols
    """
    idx = 0
    text = f' {text} '
    while idx < len(text):
        if text[idx] in ".,!?\\-/()[]{};:" and text[idx + 1] == ' ':
            text = text[:idx] + ' ' + text[idx:]
            idx += 1
        idx += 1
    return text.split()


def convert_spacy_to_bert(spacy_format: dict):
    """
    Converts a dictionary in spacy format to a string in bert format \n
    :param spacy_format: dictionary in spacy format
    :return: string in bert format
    """
    text = spacy_format['text']
    labels = [[text[start-1:end].rstrip('.,!?\\-/()[]{};:'), label] for start, end, label in spacy_format['label']]
    entities = [[split_spacy_text(entity_body), label] for entity_body, label in labels]
    bert_format = ''

    for label in labels:
        entity_text = label[0]
        text = text.replace(entity_text, ' label_token ', 1)

    words = split_spacy_text(text)
    for word in words:
        if word == 'label_token':
            entity_words = entities[0][0]
            entity_label = entities[0][1]
            bert_format += f'{entity_words[0]} B-{entity_label}\n'
            del entity_words[0]
            for entity in entity_words:
                bert_format += f'{entity} I-{entity_label}\n'
            del entities[0]
        else:
            bert_format += f'{word} O\n'

    return bert_format


def read_bert_file_split_into_texts(source_file: str):
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
                bert_format.append(text)
                text = ''

    return bert_format


def read_bert_file_one_line(source_file: str):
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


def formatting_entity(entity, text, label):
    """
    Forms entities as in spacy format \n
    :param entity: entity text
    :param text: text in which entities are searched
    :param label: entity label
    :return: list of lists of the following format: [start index entity, end index entity, entity label]
    """
    return [[i.start(), i.start() + len(entity), label] for i in re.finditer(entity, text)]


def join_bert_text(words: list):
    """
    joins words and other symbols into sentence \n
    :param words: list of single words and other symbols
    :return: one line of type string
    """
    text = ''
    for word in words:
        if word in r".,!?\/;:":
            text += word
        elif word in r"()[]{}":
            text += f'{word} '
        else:
            text += f' {word}'
    text += ' '
    text = text.replace('  ', ' ')
    return text


def convert_bert_to_spacy(bert_format: str, data_id: int):
    """
    converts text in best format to dictionary in spacy format \n
    :param bert_format: string in bert format
    :param data_id: number of current bert text
    :return: dictionary of spacy format
    """
    bert_format = bert_format.split()
    words = [bert_format[i] for i in range(0, len(bert_format), 2)]
    labels = [bert_format[i] for i in range(1, len(bert_format), 2)]

    text = join_bert_text(words)

    entity_text = ''
    entities = []

    for idx in range(len(labels)):
        temp_entities = []
        if labels[idx][0] == 'B' and entity_text == '':
            entity_text = words[idx]

        elif labels[idx][0] == 'B':
            temp_entities = formatting_entity(entity_text, text, labels[idx - 1][2:])
            entity_text = words[idx]

        elif labels[idx][0] == 'I':
            entity_text += f' {words[idx]}'

        elif entity_text != '':
            temp_entities = formatting_entity(entity_text, text, labels[idx - 1][2:])
            entity_text = ''

        if temp_entities and temp_entities[0] not in entities:
            entities += temp_entities

    if entity_text != '':
        temp_entities = formatting_entity(entity_text, text, labels[len(labels) - 1][2:])
        if temp_entities[0] not in entities:
            entities += temp_entities

    entities = sorted(entities, key=lambda elem: elem[0])
    return {"id": data_id, "text": text, "label": entities}


def parse_spacy_to_bert_format(source_file: str, result_file: str):
    """
    parses dataset in spacy format from source_file and based on it writes dataset in bert format in result_file \n
    :param source_file: path to source file containing spacy dataset
    :param result_file: path to the file to which bert dataset is written
    :return:
    """
    logging.info(f"Start converting dataset from spacy-NER to BERT-NER format...")
    source_dataset = srsly.read_jsonl(source_file)
    try:
        with open(result_file, "w") as file_stream:
            while source_dataset:
                print(convert_spacy_to_bert(next(source_dataset)), file=file_stream)
    except StopIteration:
        logging.info(f"Process finished. Result file saved to {result_file}")


def parse_bert_to_spacy_format(source_file: str, result_file: str):
    """
    parses dataset in bert format from source_file and based on it writes dataset in space format in result_file \n
    :param source_file: path to source file containing bert dataset
    :param result_file: path to the file to which spacy dataset is written
    :return:
    """
    logging.info(f"Start converting dataset from BERT-NER to spacy-NER format...")
    source_dataset = read_bert_file_one_line(source_file)
    result_dataset = []
    for data_id in range(len(source_dataset)):
        result_dataset.append(convert_bert_to_spacy(source_dataset[data_id], data_id))
    srsly.write_jsonl(result_file, result_dataset)
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
