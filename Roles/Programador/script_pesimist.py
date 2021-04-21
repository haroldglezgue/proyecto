from sys import argv
import os
import json
from textwrap import dedent

import xlrd
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

print('Procesando...')
file_ = xlrd.open_workbook("constant_files/SEL.xlsx")

emotions = file_.sheet_by_index(0)

emotion_dic = {}
for i in range(1, emotions.nrows):
    fila = emotions.row(i)
    if fila[3].value not in emotion_dic.keys():
        emotion_dic[fila[3].value] = []

for i in range(1, emotions.nrows):
    fila = emotions.row(i)

    if fila[1].value not in emotion_dic[fila[3].value]:
        emotion_dic[fila[3].value].append((fila[1].value, fila[2].value))
try:
    entry_file = open(argv[1])
    metadata = entry_file.readline()

    comments = []
    for line in entry_file.readlines():
        comment = line.split("\t")[1]
        comments.append(comment)

    tokenized_comments = []
    for comment in comments:
        tokens = word_tokenize(comment)
        words = [word.lower() for word in tokens if word.isalpha()]
        stop_words = stopwords.words('spanish')
        tokenized_comments.append([w for w in words if w not in stop_words])

    max_pfa = 0
    for key in emotion_dic.keys():
        suma = 0
        prom = 0
        for pfa in emotion_dic[key]:
            suma += pfa[1]

        prom = round((suma / len(emotion_dic[key])), 4)

        if prom > max_pfa:
            max_pfa = prom

    emotion_dic_umbral = {}
    for key in emotion_dic.keys():
        emotion_dic_umbral[key] = []
        for pfa in emotion_dic[key]:
            if pfa[1] >= max_pfa:
                emotion_dic_umbral[key].append(pfa[0])

    def ocu(word, comments):
        """
        Calcula la ocurrencia de una palabra en todos los
        comentarios
        """
        count = 0
        for comment in comments:
            if word in comment:
                count += 1

        return count

    def concu(word1, word2, comments):
        """
        Calcula la ocurrencia de una palabra en todos los
        comentarios
        """
        count = 0
        for comment in comments:
            if word1 in comment and word2 in comment:
                count += 1

        return count

    all_words = []
    for key in emotion_dic_umbral.keys():
        all_words += emotion_dic_umbral[key]

    ocurrency_words = []
    for w in all_words:
        if ocu(w, tokenized_comments) > 0:
            ocurrency_words.append(w)

    words_ocu_dic = {}
    concur_dic = {}
    for comment in tokenized_comments:
        for w in comment:
            if w not in words_ocu_dic.keys():
                words_ocu_dic[w] = ocu(w, tokenized_comments)

            for w2 in ocurrency_words:
                key = f'{w}-{w2}'
                if key not in concur_dic.keys():
                    concur_dic[key] = concu(w, w2, tokenized_comments)

    f_words_ocu_dic = {}
    for comment in tokenized_comments:
        for w in ocurrency_words:
            if w not in f_words_ocu_dic.keys():
                f_words_ocu_dic[w] = ocu(w, tokenized_comments)

    # matrix_array = []
    # for comment in tokenized_comments:
    #     matrix = []
    #     for word in comment:
    #         word_matrix = []
    #         word_ocurrence = words_ocu_dic[word]
    #         if word_ocurrence == 0:
    #             word_matrix.append(0)
    #         else:
    #             for f_w in all_words:
    #                 if f'{word}-{f_w}' not in concur_dic:
    #                     word_matrix.append(0)
    #                 else:
    #                     try:
    #                         word_matrix.append(concur_dic[f'{word}-{f_w}'] /
    #                             (f_words_ocu_dic[f_w] * words_ocu_dic[word]))
    #                     except ZeroDivisionError:
    #                         word_matrix.append(0)

    #         matrix.append(word_matrix)
    #     matrix_array.append(matrix)

    average_word_emotion = {}
    for comment in tokenized_comments:
        original_comment = comments[tokenized_comments.index(comment)]
        average_word_emotion[original_comment] = {}

        for word in comment:
            average_word_emotion[original_comment][word] = {}

            for i in range(0, len(emotion_dic_umbral.keys())):
                mod_E = len(emotion_dic[list(emotion_dic_umbral.keys())[i]])
                emotion = list(emotion_dic_umbral.keys())[i]
                emotion_words = emotion_dic_umbral[emotion]
                word_ocurrence = words_ocu_dic[word]
                sum_ = 0

                for f_w in emotion_words:
                    try:
                        sum_ += round((concur_dic[f'{word}-{f_w}'] /
                            (f_words_ocu_dic[f_w] * words_ocu_dic[word])), 6)

                    except:
                        sum_ += 0

                average_word_emotion[original_comment][word][emotion] =\
                    round((sum_ / mod_E), 6)

    entry_file.close()

    result_file = open(f"exit_files/Result_pesimista {argv[1].split('/')[1]}",
                    'w', encoding="utf-8")
    result_json = open(f"exit_files/Result_pesimista {argv[1].split('/')[1].split('.')[0]}.json",
                    'w', encoding="utf-8")

    json_word = json.dumps(average_word_emotion, ensure_ascii=False)
    result_json.writelines(json_word)
    for key in average_word_emotion.keys():
        result_file.writelines(f'{key} :' + os.linesep)

        for w_key in average_word_emotion[key].keys():
            result_file.writelines(f'\t{w_key} :' + os.linesep)

            for e_key in average_word_emotion[key][w_key].keys():
                average = average_word_emotion[key][w_key][e_key]
                result_file.writelines(f'\t\t{e_key} : O(wi, Ej) =\
 {format(average, ".6f")}' + os.linesep)

    result_file.close()
    result_json.close()

    print(f"Terminado, resultado en: \
exit_files/Result_pesimista {argv[1].split('/')[1]}")
except IndexError:
    print(dedent("""
        Por favor introdusca un archivo de entrada
        con los comentarios a analizar.
        EJ: python3 main_script.py entry_files/ex.txt
                 """))
