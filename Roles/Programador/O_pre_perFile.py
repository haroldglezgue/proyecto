from sys import argv
from textwrap import dedent

import xlrd
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import openpyxl

print('Procesando...')
file_ = xlrd.open_workbook("constant_files/SEL.xlsx")

emotions = file_.sheet_by_index(0)
omit = ['Repulsión', 'Sorpresa']

emotion_dic = {}
for i in range(1, emotions.nrows):
    fila = emotions.row(i)
    if fila[3].value not in emotion_dic.keys() and fila[3].value not in omit:
        emotion_dic[fila[3].value] = []

for i in range(1, emotions.nrows):
    fila = emotions.row(i)

    if fila[3].value in omit:
        pass
    else:

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

    min_pfa = 1
    for key in emotion_dic.keys():
        suma = 0
        prom = 0
        for pfa in emotion_dic[key]:
            suma += pfa[1]

        prom = round((suma / len(emotion_dic[key])), 4)
        if prom < min_pfa:
            min_pfa = prom

    emotion_dic_umbral = {}
    for key in emotion_dic.keys():
        emotion_dic_umbral[key] = []
        for pfa in emotion_dic[key]:
            if pfa[1] >= min_pfa:
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

    vector = {}
    for commnet in average_word_emotion.keys():
        commnet_dic = {}
        for words in average_word_emotion[commnet].keys():
            word_emo = average_word_emotion[commnet][words]
            for emotion in word_emo.keys():
                o = word_emo[emotion]
                if emotion not in commnet_dic.keys():
                    commnet_dic[emotion] = o
                else:
                    commnet_dic[emotion] += o

        max_prom = 0
        max_emo = ''
        module_o = len(average_word_emotion[commnet])
        for emot in commnet_dic.keys():
            prom = commnet_dic[emot] / module_o
            if prom > max_prom:
                max_emo = emot
                max_prom = prom

        for w in average_word_emotion[commnet].keys():
            try:
                emotion = average_word_emotion[commnet][w][max_emo]
                word_O_tuple = (w, emotion)
                if emotion > 0 and word_O_tuple not in vector:
                    vector[w] = emotion
            except KeyError:
                pass

    # print(vector)

    tf_idf = []
    O_w = []
    count = 1
    for comment in tokenized_comments:
        fila = []
        fila1 = []
        for vector_word in vector.keys():
            if vector_word in comment:
                fila.append(1)
                fila1.append(vector[vector_word])
            else:
                fila.append(0)
                fila1.append(0)

        fila.append(argv[2])
        fila1.append(argv[2])

        count += 1

        tf_idf.append(fila)
        O_w.append(fila1)

    wb = openpyxl.Workbook()
    sheet = wb.active
    sheet.append(list(vector.keys()) + ['emoción'])
    for com in tf_idf:
        sheet.append(com)
    wb.save(f'{argv[2]}_pre_pros_tf_idf.xlsx')

    wb = openpyxl.Workbook()
    sheet = wb.active
    sheet.append(list(vector.keys()) + ['emoción'])
    for com in O_w:
        sheet.append(com)
    wb.save(f'{argv[2]}_pre_pros_O_w.xlsx')

except IndexError:
    print(dedent("""
        Por favor introdusca un archivo de entrada
        con los comentarios a analizar.
        EJ: python3 main_script.py entry_files/ex.txt enfado
                 """))
