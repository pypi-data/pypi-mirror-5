import numpy as np
from cudatree import load_data, RandomForestClassifier, timer
from cudatree import util

x_train, y_train = load_data("inet")
x_test, y_test = load_data("inet_test")

def test_digits():
  with timer("Cuda treelearn"):
    forest = RandomForestClassifier()
    forest.fit(x_train, y_train, n_trees=100, min_samples_split = 1)
  with timer("Predict"):
    diff, total = util.test_diff(forest.predict(x_test), y_test)  
    print "%s(Wrong)/%s(Total). The error rate is %f." % (diff, total, diff/float(total))


test_digits()
