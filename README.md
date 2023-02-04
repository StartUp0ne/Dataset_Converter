# Dataset Converter #

## Описание ##

**1) Реализован конвертер датасета spacy-NER (в формате jsonl) в датасет BERT-NER (в формате txt).**

> Датасеты данной задачи предназначены для задачи обработки естественного языка NER
(named-entity recognition). То есть они представляют собой наборы текстов и описаний,
содержащихся в них именованных сущностей.

> **Датасет Spacy-NER** хранится в формате jsonl, где каждая запись представляет собой
информацию о некотором тексте и размеченных именованных сущностях в нем. 
(датасет содержится в файле source_spacy.jsonl)

```
{
   "id":0,
   "text":" The main villain of all groups 2.12.2021 by Kunar Mayan, Dmitriy Kapor. ",
   "label":[[1,31,"NAME_OF_REPORT"],[32,41,"DATE_OF_PUBLICATION"],[45,56,"AUTHORS"],[59,72,"AUTHORS"]]  
 }
 ```
 
 Поля каждой записи в jsonl-датасете:
 
- id – идентификатор документа, по умолчанию целые числа начиная с 0.
- text – Исходный текст документа. Текст может быть произвольной длинны – то есть содержать 1 и
более предложений.
- label – Список именованных сущностей в документе и их разметки. Формат каждого элемента в
списке:

  - индекс символа-начала сущности
  - индекс символа-конца сущности
  - имя сущности

> **Датасет BERT-NER** хранится в формате txt, где каждая строка соответствует каждому токену в
тексте, его IOB-тэгу и имени сущности к которой он принадлежит (при наличии):

```
The B-NAME_OF_REPORT
main I-NAME_OF_REPORT
villain I-NAME_OF_REPORT
of I-NAME_OF_REPORT
all I-NAME_OF_REPORT
groups I-NAME_OF_REPORT
2.12.2021 B-DATE_OF_PUBLICATION
by O
Kunar B-AUTHORS
Mayan I-AUTHORS
, O
Dmitriy B-AUTHORS
Kapor I-AUTHORS
. O
```

IOB-теги – формат для обозначения семантических фрагментов текста. Каждому токену
соответвует iob-тег, который может означать следующее:
- I – токен находится внутри сущности.
- O – токен находится вне объекта.
- B – токен - это начало сущности.

Между IOB-тегом и именем сущности ставится знак дефис «-». Токен и IOB-тег разделяет пробел.

**2) Реализована конвертация датасета **BERT-NER** в **Spacy-NER**.**
В данном случае все предложения из txt-датасета записываются в одну запись (один документ) в jsonl-датасете.

**3) Написаны unit-тесты на реализованный функционал.**
Тесты размесщены в отдельном скрипте tests.py. Для реализации использовалась библиотека unittest.

## Примеры запуска ##

1. Пример запуска алгоримта конвертации spacy в BERT

Входные данные:
```
dataset_parser.py -s source_spacy.jsonl -r result_bert.txt --spacy_to_bert True -l log.txt
```
log.txt:
```
[2023.02.02 20:08:12] I Dataset Converter started with options: {'source': 'source_spacy.jsonl', 'result': 'result_bert.txt', 'spacy_to_bert': True, 'bert_to_spacy': False, 'dry': False, 'log': 'log.txt'}
[2023.02.02 20:08:12] I Start converting dataset from spacy-NER to BERT-NER format...
[2023.02.02 20:08:12] I Process finished. Result file saved to result_bert.txt
```
В репозитории представлен исходный датасет в файле *source_spacy.jsonl*, а результат в *result_bert.txt*

1. Пример запуска алгоримта конвертации BERT в spacy
```
C:\Users\tropi\OneDrive\Desktop\RoadmapPython_5_Files\dataset_parser.py -s source_bert.txt -r result_spacy.jsonl --bert_to_spacy True -l log.txt
```
log.txt:
```
[2023.02.02 20:07:26] I Dataset Converter started with options: {'source': 'source_bert.txt', 'result': 'result_spacy.jsonl', 'spacy_to_bert': False, 'bert_to_spacy': True, 'dry': False, 'log': 'log.txt'}
[2023.02.02 20:07:26] I Start converting dataset from BERT-NER to spacy-NER format...
[2023.02.02 20:07:26] I Process finished. Result file saved to result_spacy.jsonl
```
В репозитории представлен исходный датасет в файле *source_bert.txt*, а результат в *result_spacy.jsonl*
