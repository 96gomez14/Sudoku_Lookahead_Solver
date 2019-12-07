import board
import copy
from multiprocessing import Process, Manager

M = 7
Tree_List = [{0:(1, 2, 3, 4, 5, 6, 7), 1:(), 2:(), 3:(), 4:(), 5:(), 6:(), 7:()}, {0:(1, 2, 3, 4, 5, 6), 1:(7,), 2:(), 3:(), 4:(), 5:(), 6:(), 7:()}, {0:(1, 2, 3, 4, 5), 1:(6, 7), 2:(), 3:(), 4:(), 5:(), 6:(), 7:()}, {0:(1, 2, 3, 4), 1:(5, 6), 2:(7,), 3:(), 4:(), 5:(), 6:(), 7:()}, {0:(1, 2, 3), 1:(4, 5), 2:(6,), 3:(), 4:(7,), 5:(), 6:(), 7:()}, {0:(1, 2), 1:(3, 4), 2:(5, ), 3:(6,), 4:(), 5:(), 6:(7, ), 7:()}, {0:(1, 2), 1:(3, 4), 2:(), 3:(5, ), 4:(), 5:(6, ), 6:(7, ), 7:()}, {0:(1, 2), 1:(3,), 2:(), 3:(4, ), 4:(5, ), 5:(6, ), 6:(7, ), 7:()}, {0:(1,), 1:(2, ), 2:(3,), 3:(4,), 4:(5,), 5:(6,), 6:(7, ), 7:()} ]

class Tree(object):
        def __init__(self):
                self.id = None
                self.parent = None
                self.left_child = None
                self.sibling = None

def construct_tree(T, ident):
        T.id = ident
        curr_child = None
        children = d[ident]
        if isinstance(children, tuple):
                for child in children:
                        Tp = Tree()
                        Tp.parent = T
                        construct_tree(Tp, child)
                        if T.left_child == None:
                                 T.left_child = Tp
                        else:
                                curr_child.sibling = Tp
                        curr_child = Tp

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
        tree = choose_tree(lamed)
        proc_list = []
        for i in range(M):
            return_dict[i] = (False, None)
            p = Process(target=transition, args=(i, tree, return_dict, lamed))
            proc_list.append(p)
            p.start()

        for i in range(M):
            proc_list[i].join()
	solver = choose_state(tree, return_dict, lamed)

        T = T*alef 

if __name__ == '__main__':
    solver = Sudoku_Sq(PROBLEM)
    lookahead_anneal(solver)
