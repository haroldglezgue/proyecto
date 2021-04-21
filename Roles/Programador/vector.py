from sys import argv
from textwrap import dedent
import json

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import openpyxl

print('Procesando...')

try:
    entry_file = open(argv[1])
    emotion_out = argv[2]
    json_in = entry_file.readline()
    average_dic = json.loads(json_in)

    vector = {}
    for commnet in average_dic.keys():
        commnet_dic = {}
        for words in average_dic[commnet].keys():
            word_emo = average_dic[commnet][words]
            for emotion in word_emo.keys():
                o = word_emo[emotion]
                if emotion not in commnet_dic.keys():
                    commnet_dic[emotion] = o
                else:
                    commnet_dic[emotion] += o

        max_prom = 0
        max_emo = ''
        module_o = len(average_dic[commnet])
        for emot in commnet_dic.keys():
            prom = commnet_dic[emot] / module_o
            if prom > max_prom:
                max_emo = emot
                max_prom = prom

        for w in average_dic[commnet].keys():
            try:
                emotion = average_dic[commnet][w][max_emo]
                word_O_tuple = (w, emotion)
                if emotion > 0 and word_O_tuple not in vector:
                    vector[w] = emotion
            except KeyError:
                pass

    # tf_idf = {}
    # for comment in average_dic.keys():
    #     tf_idf[comment] = {}
    #     tokens = word_tokenize(comment)
    #     words = [word.lower() for word in tokens if word.isalpha()]
    #     stop_words = stopwords.words('spanish')
    #     tokenized_comment = [w for w in words if w not in stop_words]

    #     for vector_word in vector.keys():
    #         if vector_word in tokenized_comment:
    #             tf_idf[comment][vector_word] = 1
    #         else:
    #             tf_idf[comment][vector_word] = 0

    tf_idf = []
    for comment in average_dic.keys():
        tokens = word_tokenize(comment)
        words = [word.lower() for word in tokens if word.isalpha()]
        stop_words = stopwords.words('spanish')
        tokenized_comment = [w for w in words if w not in stop_words]
        fila = []
        for vector_word in vector.keys():
            if vector_word in tokenized_comment:
                fila.append(1)
            else:
                fila.append(0)
        fila.append(emotion_out)
        tf_idf.append(fila)

    wb = openpyxl.Workbook()
    sheet = wb.active
    sheet.append(list(vector.keys()) + ['emoción'])
    for com in tf_idf:
        print(com)
        sheet.append(com)
    wb.save(f'{emotion_out}.xlsx')
    # O_w = {}
    # for comment in average_dic.keys():
    #     O_w[comment] = {}
    #     tokens = word_tokenize(comment)
    #     words = [word.lower() for word in tokens if word.isalpha()]
    #     stop_words = stopwords.words('spanish')
    #     tokenized_comment = [w for w in words if w not in stop_words]

    #     for vector_word in vector.keys():
    #         if vector_word in tokenized_comment:
    #             O_w[comment][vector_word] = vector[vector_word]
    #         else:
    #             O_w[comment][vector_word] = 0

    vector_json = json.dumps(vector, ensure_ascii=False)
    # tf_idf_json = json.dumps(tf_idf, ensure_ascii=False)
    # O_w_json = json.dumps(O_w, ensure_ascii=False)

    result_filename = f"final_vector/Vector {argv[1].split('/')[1].split('.')[0].split(' ')[1]}.json"
    result_json = open(result_filename, 'w', encoding="utf-8")
    result_json.writelines(vector_json)

    # result_filename = f"final_vector/Tf-idf {argv[1].split('/')[1].split('.')[0].split(' ')[1]}.json"
    # result_json = open(result_filename, 'w', encoding="utf-8")
    # result_json.writelines(tf_idf_json)

    # result_filename = f"final_vector/O_w {argv[1].split('/')[1].split('.')[0].split(' ')[1]}.json"
    # result_json = open(result_filename, 'w', encoding="utf-8")
    # result_json.writelines(O_w_json)

except IndexError:
    print(dedent("""
        Por favor introdusca un archivo de entrada
        con los comentarios a analizar.
        EJ: python3 main_script.py exit_files/ex.json
                 """))
