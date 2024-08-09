import sys
from itertools import combinations
from collections import defaultdict

transactions = []

class Itemset:
    def __init__(self, itemset, sup):
        self.itemset = itemset
        self.sup = sup #num_transaction곱해진값으로 저장. 나중에 출력할 때 비율로 바꿔줘야 함.

    def __str__(self):
        return str(self.itemset)

    def get_length(self):
        return len(self.itemset)

    def get_itemset(self):
        return set(self.itemset)

def read_transactions(input_file):
    with open(input_file, 'r') as file:
        transactions = [line.strip().split('\t') for line in file.readlines()]
    return transactions

def find_first_freq_itemsets(transactions, min_support):
    num_transaction = len(transactions) #트렌잭션 수
    num_min_support = min_support * num_transaction #minimum support를 %->count로 변경
    L1 = {} # 딕셔너리 

    #1번쨰 C1 생성
    C1 = []
    #scan - 돌면서 count 세기
    for sublist in transactions:
        for item in sublist:
            if item in L1:
                L1[item] += 1
            else:
                L1[item] = 1 #없었다면

    #prune
    for item, sup in L1.items():
        if sup >= num_min_support:
            C1.append(Itemset(item, sup))           

    return C1

def find_k_freq_itemsets(transactions, C1, min_support):
    num_transaction = len(transactions) #트렌잭션 수
    num_min_support = min_support * num_transaction #minimum support를 %->count로 변경

    freq_itemsets = []
    freq_itemsets.append(list(C1))
    k = 2 #다음으로 찾을 itemset의 크기
    
    while True:
        #self-join
        cur_itemset = [itemset.itemset for itemset in freq_itemsets[-1]] #itemset만 뽑아서 저장
        if k < 3:
            cur_itemset_joined = list(combinations(cur_itemset, k)) #가능한 k개 조합의 후보 생성
        else:
            cur_itemset_joined = list(combinations({item for tup in cur_itemset for item in tup}, k))


        if len(cur_itemset_joined) == 0: #더이상 조합 만들 수 없다면 break
            print('ininin')
            print(k) 
            break

        #scan
        Lk = defaultdict(int)
        for items in cur_itemset_joined:
            itemset_candidate = set(items)
            for transaction in transactions:
                if itemset_candidate == itemset_candidate.intersection(set(transaction)):
                    Lk[','.join(sorted(itemset_candidate))] += 1 
        #prune
        temp_set = list()
        for items_p, sup in Lk.items():
            items_p_tuple = tuple(items_p.split(','))
            if sup >= num_min_support:
                temp_set.append(Itemset(items_p_tuple, sup))

        freq_itemsets.append(temp_set)
        
        for itemset in freq_itemsets[-1]:
            print(f'Frequent {k}-itemsets: {itemset.itemset}, Support: {(itemset.sup):.2f}')

        #k update
        k += 1

    return freq_itemsets, k
 
def make_subsets(sets):
    subsets = []
    for i in range(1, sets.get_length() + 1):
        for combo in combinations(sets.get_itemset(), i):
            subsets.append(set(combo))
    return subsets

def find_disjoint_pairs(sets):
    subsets = make_subsets(sets)
    disjoint_pairs = []
    # print(subsets)
    for i in range(len(subsets)):
        for j in range(i + 1, len(subsets)):
            if subsets[i].union(subsets[j]) == sets.get_itemset() and subsets[i].intersection(subsets[j]) == set():
                disjoint_pairs.append((subsets[i], subsets[j]))
                
    return disjoint_pairs

def cal_support(transactions, item_set):
    num_transactions = len(transactions)
    count = 0
    for transaction in transactions:
        if item_set == item_set.intersection(set(transaction)):
            count += 1 
    return count / num_transactions * 100 if num_transactions > 0 else 0

def cal_confidence(transactions, item_set, associative_item_set):
    
    combined_set = item_set.union(associative_item_set)
    support_combined = cal_support(transactions, combined_set)
    support_item_set = cal_support(transactions, item_set)
    
    return support_combined / support_item_set * 100 if support_item_set > 0 else 0

def find_association_rules(frequent_itemset, transactions, output_file):
    with open(output_file, 'w') as file:
        for i in range(len(frequent_itemset)):
            if i==0:
                continue
            for set in frequent_itemset[i]:
                disjoint_pair = find_disjoint_pairs(set)
                # print(disjoint_pair)

                for pair in disjoint_pair:
                    #support
                    support = cal_support(transactions, pair[0].union(pair[1]))
                    print(f'{pair[0]}: {support:.2f}')
                    #confidence
                    confidence = cal_confidence(transactions, pair[0], pair[1])
                    print(f'{pair[0]}: {pair[1]} {confidence:.2f}')

                    file.write(str(pair[0]).replace('\'', '') + '\t' + 
                               str(pair[1]).replace('\'', '') + '\t' + 
                               f'{support:.2f}' + '\t' + 
                               f'{confidence:.2f}' + '\n')


                    #support
                    support = cal_support(transactions, pair[1].union(pair[0]))
                    print(f'{pair[1]}: {support:.2f}')
                    #confidence
                    confidence = cal_confidence(transactions, pair[1], pair[0])
                    print(f'{pair[1]}: {pair[0]} {confidence:.2f}')

                    file.write(str(pair[1]).replace('\'', '') + '\t' + 
                               str(pair[0]).replace('\'', '') + '\t' + 
                               f'{support:.2f}' + '\t' + 
                               f'{confidence:.2f}' + '\n')


def main():
    min_support = float(sys.argv[1])/100
    input_file = sys.argv[2]
    output_file = sys.argv[3]
    transactions = read_transactions(input_file)
    
    #step 1
    C1_result = find_first_freq_itemsets(transactions, min_support)
    frequent_itemset, k = find_k_freq_itemsets(transactions, C1_result, min_support)
    
    #step 2
    find_association_rules(frequent_itemset, transactions, output_file)


if __name__=="__main__":
    main()