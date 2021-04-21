import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
import sklearn.metrics as met

file_p = 'optimist_pre_pros_tf_idf.xlsx'
print(f'Procesando {file_p}...')
datos = pd.read_excel(f'{file_p}')
# datos = datos.astype(float).fillna(0.0)

y = datos.emoción
x = datos.drop('emoción', axis=1)
x = x.astype(float).fillna(0.0)

# print(datos['emoción'].value_counts())

x_train, x_test, y_train, y_test = train_test_split(x, y,
                                                    test_size=0.2,
                                                    random_state=42,
                                                    stratify=y)

# SVC
print('MÉTRICAS PARA SVC:')
clf = SVC(kernel='rbf').fit(x_train, y_train)
y_pred = clf.predict(x_test)

print('Score: ', clf.score(x_test, y_test))
print('Accuracy: ', met.accuracy_score(y_test, y_pred))
print('Precision: ', met.precision_score(y_test, y_pred, average=None))
print('Recall: ', met.recall_score(y_test, y_pred, average=None))
print('F1 Score: ', met.f1_score(y_test, y_pred, average=None))

print("#####################################################################")

# RL
print('MÉTRICAS PARA REGRESIÓN LOGÍSTICA:')
clf = LogisticRegression(random_state=0).fit(x_train, y_train)
y_pred = clf.predict(x_test)

print('Score: ', clf.score(x_test, y_test))
print('Accuracy: ', met.accuracy_score(y_test, y_pred))
print('Precision: ', met.precision_score(y_test, y_pred, average=None))
print('Recall: ', met.recall_score(y_test, y_pred, average=None))
print('F1 Score: ', met.f1_score(y_test, y_pred, average=None))

print("#####################################################################")

# NB
print('MÉTRICAS PARA NB:')
clf = GaussianNB().fit(x_train, y_train)
y_pred = clf.predict(x_test)

print('Score: ', clf.score(x_test, y_test))
print('Accuracy: ', met.accuracy_score(y_test, y_pred))
print('Precision: ', met.precision_score(y_test, y_pred, average=None))
print('Recall: ', met.recall_score(y_test, y_pred, average=None))
print('F1 Score: ', met.f1_score(y_test, y_pred, average=None))

print("#####################################################################")

# MLP
print('MÉTRICAS PARA MLP:')
clf = MLPClassifier(random_state=1, max_iter=300).fit(x_train, y_train)
y_pred = clf.predict(x_test)

print('Score: ', clf.score(x_test, y_test))
print('Accuracy: ', met.accuracy_score(y_test, y_pred))
print('Precision: ', met.precision_score(y_test, y_pred, average=None))
print('Recall: ', met.recall_score(y_test, y_pred, average=None))
print('F1 Score: ', met.f1_score(y_test, y_pred, average=None))