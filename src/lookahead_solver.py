import board
import copy
from multiprocessing import Process, Manager

M = 7

def lookahead_anneal(solver): 
    T = 10000
    alef = 0.99
    
    prior_avg = solver.energy()
    curr_score = prior_avg
    manager = Manager()
    return_dict = None
    while solver.user_exit == False:
        if return_dict == None:
            return_dict = manager.dict()
        else:
            prior_avg = compute_avg(return_dict)
        return_dict.clear()
        lamed = compute_lamed(curr_score, prior_avg)
        tree_info = choose_tree(lamed)
        proc_list = []
        for i in range(M):
            p = Process(target=transition, args=(i, tree_info, return_dict, lamed))
            proc_list.append(p)
            p.start()

        for i in range(M):
            proc_list[i].join()

        T = T*alef 

if __name__ == '__main__':
    solver = Sudoku_Sq(PROBLEM)
    lookahead_anneal(solver)
