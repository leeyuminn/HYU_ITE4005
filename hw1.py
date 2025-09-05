# Goal: to find association rules using Apriori algorithm
import sys
from itertools import combinations

transactions = []

def read_transactions(input_file):
    with open(input_file, 'r') as file:
        for line in file:
            transactions.append(line.strip().split('\t'))
    return transactions

def get_freq_first_itemset(num_msup, transactions):
    C1 = dict()
    L1 = dict()
    
    # make C1
    for trans in transactions:
        for item in trans:
            if item not in C1.keys():
                C1[item] = 1
            else:
                C1[item] += 1
                
    # make L1 <- pruning
    for item, sup in C1.items():
        if sup >= num_msup:
            L1.setdefault(item, sup)
            
    return L1
            
def apriori(num_msup, transactions):
    # 0. initially, generate frequent 1-itemset L1
    L1 = get_freq_first_itemset(num_msup, transactions)
     
    prev_L_itemlist = set(sorted(L1.keys())) #L1의 item값만 빼서 리스트 생성
    
    final_result = dict()
    final_result.update({(item,): sup for item, sup in L1.items()})
    
    k = 1
    while True:
        # 1. generate candidate - self joining
        cur_C_itemlist = list(combinations(sorted(prev_L_itemlist), (k+1)))
        cur_C = dict()
        prev_L_itemlist.clear()
        
        #initialize dict C
        for item in cur_C_itemlist:
            cur_C[item] = 0
        
        # scan, count
        for trans in transactions:
            for item_c in cur_C.keys():
                if set(item_c).issubset(set(trans)):
                    cur_C[item_c] += 1  
        
        # 2. Test - pruning
        cur_L = dict()
        for item_l, sup in cur_C.items():
            if sup >= num_msup:
                cur_L[item_l] = sup
                
        # 3. Terminate condition
        if len(cur_L) == 0:
            #print("No longer created Lk")
            break
        
        final_result.update(cur_L)
        
        for key in cur_L:
            prev_L_itemlist.update(key)
        k += 1
 
    return final_result
 
def find_association(result, total_num):
    rule = []
    
    for itemset in result.keys():
        if len(itemset) < 2:
            continue
        
        itemset_support = result[itemset]

        for i in range(1, len(itemset)):
            for A in combinations(itemset, i):
                B = tuple(sorted(set(itemset) - set(A)))
                A = tuple(sorted(A))

                if A in result and B:
                    support = (itemset_support / total_num) * 100
                    confidence = (itemset_support / result[A]) * 100

                    rule.append({
                        'rule_a': f"{{{','.join(A)}}}",
                        'rule_b': f"{{{','.join(B)}}}",
                        'support': f"{support:.2f}",
                        'confidence': f"{confidence:.2f}"
                    })
    return rule
        
def write_outfile(file, association_rules):
    with open(file, 'w') as file:
        for rule in association_rules:
            file.write(rule['rule_a'] + '\t' +
                            rule['rule_b'] + '\t' +
                            rule['support'] + '\t' + 
                            rule['confidence'] + '\n')
        
    
def main():
    # argument matching
    min_sup = float(sys.argv[1])/100
    input_file = sys.argv[2]
    output_file = sys.argv[3]
    
    # read transaction
    transactions = read_transactions(input_file)
    num_msup = int(min_sup * len(transactions))
    
    # Apriori algorithm
    final_result = apriori(num_msup, transactions)    
    
    # find Association rules
    associaton_rules = find_association(final_result, len(transactions))
    #print(associaton_rule)
    
    # write output file
    write_outfile(output_file, associaton_rules)

if __name__=="__main__":
    main()