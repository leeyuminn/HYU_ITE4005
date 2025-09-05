# Goal: Build a decision tree, and then classify the test dataset using the tree
import sys  
import math
from collections import Counter

class DecisionNode:
    def __init__(self, selected_attribute=None, child_branches=None, label=None):
        self.selected_attribute = selected_attribute
        self.child_branches = child_branches or {}
        self.label = label # leaf node라면 갖고 있고 아니면 None

    def is_leaf(self):
        return self.label is not None
    
def read_training_file(file):
    lines = []

    with open(file, 'r') as f:
        for line in f:
            lines.append(line.strip().split('\t'))

    full_attribute_names = lines[0] 
    full_attribute_values = lines[1:]
    # -> class값 제외한 attributes
    attribute_names = full_attribute_names[:-1]
    attribute_values = [row[:-1] for row in full_attribute_values]
    
    class_label = full_attribute_names[-1]
    class_values = [row[-1] for row in full_attribute_values]
    
    return attribute_names, attribute_values, class_label, class_values

def read_test_file(file):
    lines = []

    with open(file, 'r') as f:
        for line in f:
            lines.append(line.strip().split('\t'))
    attribute_names = lines[0] 
    attribute_values = lines[1:]

    return attribute_names, attribute_values

def majority(class_values):
    return Counter(class_values).most_common(1)[0][0]

def entropy(data):
    # compute information gain
    total_num = len(data)
    num_counts = Counter(data)
    info_gain = -sum((ncount_i / total_num) * math.log2(ncount_i / total_num) for ncount_i in num_counts.values())

    return info_gain

def gain_ratio(i, attribute_values, class_values):
    # 현재 보고 있는 attribute의 index = i    
    # get information gain before
    information_gain_before = entropy(class_values)
    
    # get information gain after
    total = len(attribute_values) 
    partitions_by_i = {}

    for row, label in zip(attribute_values, class_values):
        key = row[i]
        partitions_by_i.setdefault(key, []).append(label)
    
    information_gain_after = sum((len(k) / total) * entropy(k) for k in partitions_by_i.values())
    
    # compute Gain
    info_gain = information_gain_before - information_gain_after

    # compute SplitInfo 
    split_info = -sum((len(k) / total) * math.log2(len(k) / total) for k in partitions_by_i.values() if len(k) > 0)
    
    if split_info == 0: # 안나뉘어지는 경우
        return 0

    # compute GainRatio
    gain_ratio = info_gain / split_info

    return gain_ratio

def build_decision_tree(attribute_names, attribute_values, class_label, class_values, used_attributes = None):
    
    # index로 접근
    if used_attributes is None:
        used_attributes = set()

    # stop cond(1): they have same class     
    if all(label == class_values[0] for label in class_values):
        return DecisionNode(label=class_values[0])
    
    # stop cond(2): no more attributes -> use majority
    if len(used_attributes) == len(attribute_names):
        return DecisionNode(label=majority(class_values))
        
    # feature selection
    selected_attribute_idx = None
    biggest_gain_ratio = -1

    for i in range(len(attribute_names)):
        if i in used_attributes:
            continue
        # i번째 attribute의 gain_ratio 계산
        com_gain_ratio = gain_ratio(i, attribute_values, class_values)

        # attribute의 gain_ratio가 큰 값으로 계속 덮어쓰기 
        if com_gain_ratio > biggest_gain_ratio:
            selected_attribute_idx = i
            biggest_gain_ratio = com_gain_ratio

    if selected_attribute_idx is None:
        return DecisionNode(label=majority(class_values))

    used_attributes.add(selected_attribute_idx)

    # 노드 생성
    cur_node = DecisionNode(selected_attribute=attribute_names[selected_attribute_idx])

    partitions = {}
    for row, label in zip(attribute_values, class_values):
        key = row[selected_attribute_idx]
        partitions.setdefault(key, []).append((row, label))

    for value, items in partitions.items():
        sub_attribute_values = [row for row, _ in items]
        sub_class_values = [label for _, label in items]
        child = build_decision_tree(attribute_names, sub_attribute_values, class_label, sub_class_values, used_attributes.copy()) #sub_class_values여기서 입력
        cur_node.child_branches[value] = child

    return cur_node

def classify(decision_tree, test_attribute_names, test_attribute_values):
    predictions = []

    for row in test_attribute_values:
        cur_node = decision_tree
        while not cur_node.is_leaf():
            attr_index = test_attribute_names.index(cur_node.selected_attribute)
            value = row[attr_index]
            if value in cur_node.child_branches:
                cur_node = cur_node.child_branches[value]
            else:
                leaf_labels = []
                for child in cur_node.child_branches.values():
                    if child.is_leaf():
                        leaf_labels.append(child.label)
                if leaf_labels:
                    predictions.append(majority(leaf_labels))
                else:
                    predictions.append("unknown")
                break
        else:
            predictions.append(cur_node.label)        

    return predictions

def write_result(file, predictions, attribute_names, class_label, test_attribute_values):
    header = attribute_names + [class_label] # attribute_names는 []니까
    with open(file, 'w') as f:
        f.write('\t'.join(header) + '\n')
        for row, label in zip(test_attribute_values, predictions):
            f.write('\t'.join(row + [label]) + '\n')  

def main():
    # argument matching
    training_file = sys.argv[1]
    test_file = sys.argv[2]
    result_file = sys.argv[3]

    # read training file, test file
    attribute_names, attribute_values, class_label, class_values = read_training_file(training_file)
    test_attribute_names, test_attribute_values = read_test_file(test_file)

    # build a decision tree
    decision_tree = build_decision_tree(attribute_names, attribute_values, class_label, class_values)

    # classify the test dataset using the tree
    predictions = classify(decision_tree, test_attribute_names, test_attribute_values)

    # write result file
    write_result(result_file, predictions, attribute_names, class_label, test_attribute_values)

if __name__=="__main__":
    main()
