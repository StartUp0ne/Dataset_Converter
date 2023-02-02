import unittest
from dataset_parser import convert_bert_format, read_bert_file, parse_spacy_to_bert_format


class ParseSpacyToBertTestCase(unittest.TestCase):
    def test_spacy_to_bert(self):
        test_files = r"C:\Users\tropi\OneDrive\Desktop\RoadmapPython_5_Files\source_spacy.jsonl"

        expect_file = r"C:\Users\tropi\OneDrive\Desktop\RoadmapPython_5_Files\source_bert.txt"
        expected_dataset = read_bert_file(expect_file)

        res_file = r"C:\Users\tropi\OneDrive\Desktop\RoadmapPython_5_Files\test_files\result_file.txt"
        parse_spacy_to_bert_format(test_files, res_file)
        result_dataset = read_bert_file(res_file)

        self.assertEqual(result_dataset, expected_dataset)


class ParseBertToSpacyTestCase(unittest.TestCase):
    def test_bert_to_spacy(self):
        test_data = read_bert_file(r"C:\Users\tropi\OneDrive\Desktop\RoadmapPython_5_Files\test_files\bert_to_spacy_test.txt")
        expected_dataset = [
            {"id": 0, "text": " Compromise indicators name md5 sha256 Cobalt Strike MD5_TOKEN ",
             "label": [[39, 52, "MALWARE_NAME"], [53, 62, "IOC_MD5"]]},
            {"id": 1, "text": " SHA256_TOKEN Rare MD5_TOKEN SHA256_TOKEN DanceWithMe MD5_TOKEN SHA256_TOKEN ",
             "label": [[1, 13, "IOC_SHA256"], [14, 18, "MALWARE_NAME"], [19, 28, "IOC_MD5"], [29, 41, "IOC_SHA256"],
                       [42, 53, "MALWARE_NAME"], [54, 63, "IOC_MD5"], [64, 76, "IOC_SHA256"]]}
        ]
        for idx in range(len(test_data)):
            self.assertEqual(convert_bert_format(test_data[idx], idx), expected_dataset[idx])
