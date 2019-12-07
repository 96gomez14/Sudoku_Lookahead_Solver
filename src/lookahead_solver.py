import board
import copy
from multiprocessing import Process, Manager

T = 10000
alef = 0.99
M = 7

Tree_List = [{0:(1, 2, 3, 4, 5, 6, 7), 1:(), 2:(), 3:(), 4:(), 5:(), 6:(), 7:()}, {0:(1, 2, 3, 4, 5, 6), 1:(7,), 2:(), 3:(), 4:(), 5:(), 6:(), 7:()}, {0:(1, 2, 3, 4, 5), 1:(6, 7), 2:(), 3:(), 4:(), 5:(), 6:(), 7:()}, {0:(1, 2, 3, 4), 1:(5, 6), 2:(7,), 3:(), 4:(), 5:(), 6:(), 7:()}, {0:(1, 2, 3), 1:(4, 5), 2:(6,), 3:(), 4:(7,), 5:(), 6:(), 7:()}, {0:(1, 2), 1:(3, 4), 2:(5, ), 3:(6,), 4:(), 5:(), 6:(7, ), 7:()}, {0:(1, 2), 1:(3, 4), 2:(), 3:(5, ), 4:(), 5:(6, ), 6:(7, ), 7:()}, {0:(1, 2), 1:(3,), 2:(), 3:(4, ), 4:(5, ), 5:(6, ), 6:(7, ), 7:()}, {0:(1,), 1:(2, ), 2:(3,), 3:(4,), 4:(5,), 5:(6,), 6:(7, ), 7:()} ]


def fill_states(i, tree, returns, prob, parent_solver):
    parent_copy = parent_solver
    if i != 0:	# We only modify the returns dict for non-root nodes in our tree
        parent_copy = copy.deepcopy(parent_solver)
        parent_copy.move()
        returns[i] = []
        returns[i].append(parent_copy)
    proc_list = []
    children = tree[i]
    for child_index in children:
        p = multiprocessing.Process(target=fill_states, args=(child_index, tree, returns, prob, parent_copy))
        proc_list.append(p)
        p.start()
    for proc in proc_list:
        proc.join()
    
def evaluate_tree(returns):
    proc_list = []
    for i in range(M):
        p = multiprocessing.Process(target=returns[i][0].solve, args=((returns, i)))
        proc_list.append(p)
        p.start()
    for proc in proc_list:
        proc.join()
        

def lookahead_anneal(solver): 
    prior_avg = solver.energy()
    curr_score = prior_avg
    manager = Manager()
    return_dict = None
    while solver.user_exit == False:
	"""This will act as our result holder for each round, i.e., 
	it will hold the tree's nodes' states, and their respective 
	energy levels."""
        if return_dict == None:
            return_dict = manager.dict()
        else:
            prior_avg = compute_avg(return_dict)
        return_dict.clear()
        lamed = compute_lamed(curr_score, prior_avg)
        tree_dict = choose_tree(lamed)
        fill_states(0, tree_dict, return_dict, lamed, solver)
	evaluate_tree(return_dict)
	solver = choose_state(tree, return_dict, lamed)

        T = T*alef 

if __name__ == '__main__':
    solver = board.Sudoku_Sq(PROBLEM)
    lookahead_anneal(solver)
