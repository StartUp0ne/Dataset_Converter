import unittest
from dataset_parser import convert_bert_to_spacy, read_bert_split_into_texts, parse_spacy_to_bert_format, \
    read_bert_in_one_line


class ParseSpacyToBertTestCase(unittest.TestCase):
    def test_spacy_to_bert(self):
        test_files = r"C:\Users\tropi\OneDrive\Desktop\RoadmapPython_5_Files\source_spacy.jsonl"

        expect_file = r"C:\Users\tropi\OneDrive\Desktop\RoadmapPython_5_Files\source_bert.txt"
        expected_dataset = read_bert_split_into_texts(expect_file)

        res_file = r"C:\Users\tropi\OneDrive\Desktop\RoadmapPython_5_Files\test_files\result_file.txt"
        parse_spacy_to_bert_format(test_files, res_file)
        result_dataset = read_bert_split_into_texts(res_file)

        self.assertEqual(result_dataset, expected_dataset)


class ParseBertToSpacyTestCase(unittest.TestCase):
    def test_bert_to_spacy_one_text(self):
        test_data = read_bert_in_one_line(r"C:\Users\tropi\OneDrive\Desktop\RoadmapPython_5_Files\test_files\bert_to_spacy_test.txt")
        expected_dataset = [
            {'id': 0,
             'text': 'Compromise indicators name md5 sha256 Cobalt Strike MD5_TOKEN '
                     'SHA256_TOKEN Rare MD5_TOKEN SHA256_TOKEN DanceWithMe MD5_TOKEN '
                     'SHA256_TOKEN ',
             'label': [[38, 51, 'MALWARE_NAME'], [52, 61, 'IOC_MD5'], [62, 74, 'IOC_SHA256'], [75, 79, 'MALWARE_NAME'],
                       [80, 89, 'IOC_MD5'], [90, 102, 'IOC_SHA256'], [103, 114, 'MALWARE_NAME'], [115, 124, 'IOC_MD5'],
                       [125, 137, 'IOC_SHA256']]
             }
        ]
        for idx in range(len(test_data)):
            self.assertEqual(convert_bert_to_spacy(test_data[idx], idx), expected_dataset[idx])

    def test_bert_to_spacy_split_texts(self):
        test_data = read_bert_split_into_texts(
            r"C:\Users\tropi\OneDrive\Desktop\RoadmapPython_5_Files\test_files\bert_to_spacy_test.txt")
        expected_dataset = [
            {
             "id": 0,
             "text": "Compromise indicators name md5 sha256 Cobalt Strike MD5_TOKEN ",
             "label": [[38, 51, "MALWARE_NAME"], [52, 61, "IOC_MD5"]]},
            {
             "id": 1,
             "text": "SHA256_TOKEN Rare MD5_TOKEN SHA256_TOKEN DanceWithMe MD5_TOKEN SHA256_TOKEN ",
             "label": [[1, 13, "IOC_SHA256"], [14, 18, "MALWARE_NAME"], [19, 28, "IOC_MD5"], [29, 41, "IOC_SHA256"],
                       [42, 53, "MALWARE_NAME"], [54, 63, "IOC_MD5"], [64, 76, "IOC_SHA256"]]
             }

        ]
        for idx in range(len(test_data)):
            self.assertEqual(convert_bert_to_spacy(test_data[idx], idx), expected_dataset[idx])
