#!/anaconda3/bin/python

import numpy as np
import pandas as pd
import math
try:
    from collections.abc import defaultdict
except ImportError:
    from collections import defaultdict

from IPython.display import display, Markdown
from itertools import combinations
import datetime

class Pairs():

    ########################## INITIALIZATION ################################
    def __init__(self,students_file = "",past_pairs_file = "",
    samples=100000,new_pairs_file='./new_pairs.csv',verbose=False):
        # TODO: docstring!!!
        self.samples = samples
        self.verbose = verbose
        self.students_file=students_file
        self.past_pairs = past_pairs_file
        # self._load_students(students_file)
        # self._load_past_pairs(past_pairs_file)
        self._new_pairs_file = new_pairs_file
        if verbose:
            self._student_check(self.past_pairs, 'past pairs')
            self._student_check(self.past_xPairs, 'past pairs within trios')
            self._student_check(self.past_trios, 'past trios')

    def _load_students(self, students_file):
        self.students = (pd.read_csv(students_file)
        .sort_values(by='Students')
        .reset_index(drop=True))

        self.students['Average'] = self.students['Average'].map(lambda x: float(x.strip('%')))
        self.stuDico = self.students.set_index('Students').to_dict(orient='Index')
        self.studArr = self.students['Students'].to_numpy().flatten()
        self.len = len(self.studArr)

    def _load_past_pairs(self, past_pairs_file):
        past_df = pd.read_csv(past_pairs_file)
        past_df.fillna('', inplace=True)
        self.past_pairs, self.past_trios, self.past_xPairs = self._create_pairs(past_df)
        # self.past_pairs2, _, __ = self._create_groups(past_df)

    def _student_check(self, pairs, pair_name):
        # Make sure the students in the pairs belong to the student population
        for pair in pairs:
            for student in pair:
                if student not in self.stuDico:
                    print(f'ERROR in {pair_name}!: {student} is not in student roster')

    ######################## FIND OPTIMAL PAIRS ##############################
    def find_min(self,print_results=True):
        # returns a pairing with no repeat, or None
        # start = datetime.datetime.now()
        best = {'set': set(), 'loss': math.inf}

        for _ in range(self.samples):
            draw = np.random.choice(self.studArr, self.len, replace=False)
            newPairs = set()
            newTrios = set()
            newTrio = None
            if self.len % 2 == 0:
                for i in range(math.floor(self.len/2)):
                    newPairs.add(frozenset([draw[2*i], draw[2*i+1]]))
            else:
                for i in range(math.floor(self.len/2) - 1):
                    newPairs.add(frozenset([draw[2*i], draw[2*i+1]]))
                newTrio = frozenset([draw[self.len-3], draw[self.len-2], draw[self.len-1]])

            if newTrio != None:
                newTrios.add(newTrio)
            pair_count, xPair_count, trio_count = self.check_new(newPairs, newTrios)
            loss = 10 * pair_count + xPair_count + 5 * trio_count

            if best['loss'] > loss:
                best['pairs'] = newPairs
                best['trios'] = newTrios
                best['loss'] = loss
                print(f'Lowest loss: {loss}')
                # Add the following line to avoid a systematic side effect:
                # if loss < 18: break

        display('\n***** Optimal pairing found:')
        df = pd.DataFrame(best['pairs'] | best['trios']).fillna('')
        if  __name__ == "__main__":
            self._console_print(df, '\t')

            print('\n\nCopy-paste the following comma-separated version of the pairing to past_pairs.csv using a text editor:')
            self._console_print2(df) #, ',')
        elif print_results == True:
            df.columns = [''] * len(df.columns)
            display(df.set_index(0))

        return best['pairs'], best['trios']

    def _print_formatter(self, x, extra_char):
        x = x.strip()
        x += extra_char
        return x

    def _console_print(self, df, extra_char):
        print_formatter = (lambda x: self._print_formatter(x, extra_char))
        print(
            df.to_string(header=[''] * len(df.columns),
                         index=False,
                         index_names=False,
                         formatters=[print_formatter] * len(df.columns),
                         justify=None))

    def _console_print2(self, df):
        # Print for pasting in csv and Google sheets
        df2 = df.applymap(lambda x: self._print_formatter(x, ','))
        df2.apply(lambda x: print(''.join(x)), raw=True, axis=1)

    def find_min2(self):
        # TODO: fix bugs using trio_test notebook
        start = datetime.datetime.now()
        best = {
            'set': set(),
            'loss': math.inf
        }

        for _ in range(self.samples):
            draw = np.random.choice(self.studArr, self.len, replace=False)
            newPairs = set()
            newTrio = set()
            if self.len % 2 == 0:
                for i in range(math.floor(self.len/2)):
                    newPairs.add(frozenset([draw[2*i], draw[2*i+1]]))
            else:
                for i in range(math.floor(self.len/2) - 1):
                    newPairs.add(frozenset([draw[2*i], draw[2*i+1]]))
                newTrio = (frozenset([draw[self.len-3], draw[self.len-2], draw[self.len-1]]))

            loss = self.total_pair_loss(newPairs)

            if best['loss'] > loss:
                best['set'] = newPairs
                best['loss'] = loss
                print('Lowest loss: {0:.2f}'.format(loss))

        display('\nFinal lowest loss: {0:.2f}'.format(best['loss']))
        display('\nPairing with lowest loss:')
        if len(newTrio) > 0:
            newPairs.add(newTrio)
        display(pd.DataFrame(newPairs).fillna('').set_index(0))


        print('Elapsed time:',str(datetime.datetime.now() - start))

    ######################## LOSS COMPUTATIONS ###############################
    def total_pair_loss(self, new_pairs=None, verbose=False):
        # TODO 1st: test this with good pairing detected by other algo
        if new_pairs == None:
            new_df = pd.read_csv(self._new_pairs_file)
            new_df.fillna('', inplace=True)
            new_pairs, new_trios, new_xPairs = self._create_pairs(new_df)

        # Total loss
        pipeline = [
            (10, self._pair_loss, [self.past_pairs2], 'Pair loss'),
            # (0.001, self._diff_loss, [], 'Level difference loss'),
        ]
        loss = 0
        for weight, func, args, title in pipeline:
            delta = weight * func(new_pairs, *args)
            if verbose:
                print(title + ': ', delta)
            loss += delta
        return loss

    def _diff_loss(self, new_pairs):
        # Avoid large gaps between pair average grades
        # Precondition: only pairs
        loss = 0
        for i in new_pairs:
            pair = [0,0]
            for j, name in enumerate(i):
                pair[j] = name
            delta = (self.stuDico[pair[1]]['Average'] -
              self.stuDico[pair[0]]['Average']) ** 2
            loss += delta
        return loss

    def _pair_loss(self, new_pairs, pairs):
        # return len(new_pairs & pairs)
        loss = 0
        HIGHER_ORDER_BOOST = 3  # Needed so 1st repeat of higher order > any lower order repeat
        for repeats, repeat_set in enumerate(pairs):
            # print(repeats, repeat_set)
            hits = len(repeat_set & new_pairs)
            if hits > 0:
                loss += (HIGHER_ORDER_BOOST + hits)**(repeats + 2)
                # print('hits', hits, 'repeats:', repeats)
            else:
                # print('Found one w/ no hits!')
                pass
        if loss == 0:
            print('No pair loss!')
            print(new_pairs)
        return loss


    ############################# CHECKS #####################################
    def check_new(self,new_pairs=None,new_trios=set(), verbose=None):
        # Returns number of matches with previous pairs
        if verbose == None:
            verbose = self.verbose

        if new_pairs == None:
            new_df = pd.read_csv(self._new_pairs_file)
            new_df.fillna('', inplace=True)
            new_pairs, new_trios, new_xPairs = self._create_pairs(new_df)
        else:
            new_xPairs = set()
            if len(new_trios) != 0:
                for trio in new_trios:
                    if trio != None:
                        for combo in combinations(trio, 2):
                            new_xPairs.add(frozenset(combo))

        pair_count = 0
        trio_count = 0
        xPair_count = 0

        # PAIRS
        matches = self.past_pairs & new_pairs
        if verbose:
            print(len(new_pairs), 'pairs found')
            print(len(new_trios), 'trios found')
        if len(matches) > 0:
            if verbose:
                print('Pairs repeat:', matches)
            pair_count += len(matches)
        else:
            if verbose:
                print('No exact pair repeat found')

        # TRIOS
        matches = self.past_trios & new_trios
        if len(matches) > 0:
            if verbose:
                print('Trios repeat:', matches)
            trio_count = len(matches)
        else:
            if verbose:
                print('No trio repeat found')

        # PAIRS WITHIN TRIOS
        matches = (self.past_xPairs & new_pairs) | (self.past_pairs & new_xPairs)
        if len(matches) > 0:
            xPair_count = len(matches)
            if verbose:
                print('Pairs found in trios:', matches)
        else:
            if verbose:
                print('No pair in trio repeat found')
        return pair_count, xPair_count, trio_count


    ##################### PAIRS AND TRIOS CREATIONS ##########################
    def _create_pairs(self, df):
        pairs = set()
        trios = set()
        xPairs = set()
        for i, j, k in zip(df['pair1'], df['pair2'], df['pair3']):
            i = i.strip()
            j = j.strip()
            k = k.strip()
            if i == '':
                continue
            if k != '' and k.lower() !='none':
                trios.add(frozenset([i, j, k]))
                xPairs.add(frozenset([i, j]))
                xPairs.add(frozenset([i, k]))
                xPairs.add(frozenset([k, j]))
            else:
                pairs.add(frozenset([i, j]))

        return pairs, trios, xPairs

    def _create_groups(self, df):
        pairs = []
        trios = defaultdict(lambda: set())
        xPairs = defaultdict(lambda: set())
        for pair1, pair2, pair3 in zip(df['pair1'], df['pair2'], df['pair3']):
            if pair1 == '':
                continue
            if pair3 != '' and pair3.lower() !='none':
                pass # TODO!
                # trios.add(frozenset([i, j, k]))
                # xPairs.add(frozenset([i, j]))
                # xPairs.add(frozenset([i, k]))
                # xPairs.add(frozenset([k, j]))
            else:
                pair = frozenset([pair1, pair2])
                found = False
                for i in range(len(pairs)-1,-1,-1):
                    pair_set = set()
                    pair_set.add(pair)
                    if pairs[i] & pair_set:
                        self._add(pair, pairs, i+1)
                        pairs[i] -= pair_set
                        found = True
                        break
                if found == False:
                    self._add(pair, pairs, 0)
        return pairs, trios, xPairs

    def _add(self, pair, pairs, idx):
        if idx == len(pairs):
            pairs.append(set())
        elif idx > len(pairs):
            raise Exception('Precondition not met in _add!')

        pairs[idx].add(pair)


if __name__ == "__main__":
    from os import system
    import sys

    system('clear')

    import argparse

    # create parser
    parser = argparse.ArgumentParser()

    # add arguments to the parser
    parser.add_argument("students")
    parser.add_argument("past_pairs")

    # parse the arguments
    args = parser.parse_args()

    Test = False
    if not Test:
        # Normal operation
        students_file= args.students
        past_pairs_file= args.past_pairs
        new_pairs_file='./new_pairs.csv'
        verbose = False
        samples = 100000
        print(sys.argv[1])
    else:
        # TEST
        print('\n@@@@@@@ WARNING! RUNNING IN TEST MODE @@@@@@@\n')
        test_id = '2'
        students_file='./test/data/students_'+test_id+'.csv'
        past_pairs_file='./test/data/past_pairs_'+test_id+'.csv'
        new_pairs_file='./test/data/new_pairs_'+test_id+'.csv'
        verbose = False
        samples = 10

    if len(sys.argv) > 1:
        arg0 = sys.argv[1]
        try:
            samples = int(arg0)
        except:
            print('\nUsage: python pairs.py [optional argument: number of random combinations]\n')

    pairs = Pairs(samples, students_file, past_pairs_file, new_pairs_file, verbose)

    print('      PAIR GENERATOR\n')
    print(f'Number of random combinations: {pairs.samples} \n')
    newPairs, newTrios = pairs.find_min()
    print('\n***** Result check:\n')
    pairs.check_new(newPairs, new_trios=newTrios, verbose=True)

    print("\nIMPORTANT!\nRemember to add the day's pairs to past_pairs.csv before generating pairs for the next day!!!\n")
