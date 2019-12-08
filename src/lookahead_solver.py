import board
from copy import deepcopy
from math import exp
from numpy.random import uniform
from multiprocessing import Process, Manager
from scipy.constants import Boltzmann

T = 10000
alef = 0.99
M = 7

Tree_List = [{0:(1, 2, 3, 4, 5, 6, 7), 1:(), 2:(), 3:(), 4:(), 5:(), 6:(), 7:()}, {0:(1, 2, 3, 4, 5, 6), 1:(7,), 2:(), 3:(), 4:(), 5:(), 6:(), 7:()}, {0:(1, 2, 3, 4, 5), 1:(6, 7), 2:(), 3:(), 4:(), 5:(), 6:(), 7:()}, {0:(1, 2, 3, 4), 1:(5, 6), 2:(7,), 3:(), 4:(), 5:(), 6:(), 7:()}, {0:(1, 2, 3), 1:(4, 5), 2:(6,), 3:(), 4:(7,), 5:(), 6:(), 7:()}, {0:(1, 2), 1:(3, 4), 2:(5, ), 3:(6,), 4:(), 5:(), 6:(7, ), 7:()}, {0:(1, 2), 1:(3, 4), 2:(), 3:(5, ), 4:(), 5:(6, ), 6:(7, ), 7:()}, {0:(1, 2), 1:(3,), 2:(), 3:(4, ), 4:(5, ), 5:(6, ), 6:(7, ), 7:()}, {0:(1,), 1:(2, ), 2:(3,), 3:(4,), 4:(5,), 5:(6,), 6:(7, ), 7:()} ]

Prob_Range_List = [(0, 0.23), (0.23, 0.28), (0.28,0.32), (0.32, 0.44), (0.44, 0.57), (0.57, 0.69), (0.69, 0.73), (0.73, 0.78), (0.78, 1)]

def compute_avg(returns):
    total = 0
    keys = returns.keys()
    for key in keys:
        if key != 0:
            total += returns[key][1]
    return total/M

def compute_lamed(curr_score, prior_avg):
    return exp((root_accept_energy - curr_child_energy)/(T * Boltzmann)) 

def choose_tree(prob):
    if prob == 1:	# Special case when we know to transition every time
        return Tree_List[M - 1]

    i = 0
    for tup in Prob_Range_List:
        if (prob >= tup[0]) and (prob < tup[1]):
            break
        i += 1 
    return Tree_List[i]

def fill_states(i, tree, returns, prob, parent_solver):
    """
    Computes each our state tree's nodes board states, from which
    we will then derive their respective energy levels using 
    evaluate_tree(). Since our returns dictionary holds, at each key,
    a length-two list of state and energy level, and we assume by induction
    that each round of SA has emptied the dictionary, we initialize this
    list, and append the state here.
    """
    parent_copy = parent_solver
    if i != 0:	# We only modify the returns dict for non-root nodes in our tree
        parent_copy = deepcopy(parent_solver)
        parent_copy.move()
        returns[i] = []
        returns[i].append(parent_copy.state)
    proc_list = []
    children = tree[i]
    for child_index in children:
        p = Process(target=fill_states, args=(child_index, tree, returns, prob, parent_copy))
        proc_list.append(p)
        p.start()
    for proc in proc_list:
        proc.join()
    
def evaluate_tree(returns):
    """
    In this round of the SA, we compute the energy level of each 
    of our tree's nodes, which we will use in deciding the state
    in which we we will end up, by the end of this round.
    """
    proc_list = []
    for i in range(M):
        p = Process(target=returns[i][0].energy, args=((returns, i)))
        proc_list.append(p)
        p.start()
    for proc in proc_list:
        proc.join()
        
def choose_state(root_index, tree, returns, prob):
    """
    Assuming the tree rooted at root_index holds this
    round's final accept state (by induction), we keep
    recursively calling this function on deeper subtrees
    until we can either accept a deeper state or this root.
    """
    children = tree[root_index]
    chose_child = False
    root_accept_state = returns[root_index][0]
    root_accept_energy = returns[root_index][1]
    desc_accept_state = None
    desc_accept_energy = None
    for child_index in children:
        if chose_child:
            break
        curr_child_energy = returns[child_index][1]
        if ((-1 * root_accept_energy) >= (-1 * curr_child_energy)) or
           (prob > uniform()):
            desc_accept_state, desc_accept_energy = choose_state(child_index, tree, returns, prob)
            chose_child = True
    if chose_child:
        return ()
    return (root_accept_state, root_accept_energy)

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
        return_dict[0] = [solver.state, curr_score]
        lamed = compute_lamed(curr_score, prior_avg)
        tree_dict = choose_tree(lamed)
        fill_states(0, tree_dict, return_dict, lamed, solver)
	evaluate_tree(return_dict)
	solver.state, curr_score = choose_state(0, tree, return_dict, lamed)
        T = T*alef 

if __name__ == '__main__':
    solver = board.Sudoku_Sq(PROBLEM)
    lookahead_anneal(solver)
