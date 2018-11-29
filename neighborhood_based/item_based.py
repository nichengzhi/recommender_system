# -*- coding: utf-8 -*-

# created on 2018-11-26
# @author: CHENGZHI NI

import math
import random



class ItemBased(object):

    def __init__(self, filepath):
        self.filepath = filepath
        #self.train = dict()
        self.train_data = dict()  # each data have users and its records
        self.test_data = dict()
        self.sim_matrix = dict()
        self.movieset = set()
    def read_file(self):
        filereader = open(self.filepath, 'r')
        for i, line in enumerate(filereader):
            yield line.strip('\r\n')
            if i % 10000 == 0:
                print "load file %s lines complete" % i
        filereader.close()

    def train_test_split(self, k=1, m=6, seed=1):
        random.seed(seed)
        for line in self.read_file():
            user, item, score, _ = line.split('\t')

            if random.randint(0, m) == k:
                # print 0
                self.train_data.setdefault(user, {})
                self.train_data[user][item] = int(score)
                self.movieset.add(item)
            else:
                # print 1
                self.test_data.setdefault(user, {})
                self.test_data[user][item] = int(score)
                self.movieset.add(item)

    def generate_sim_matrix(self):

        c = dict()  # item matrix for co occurance, if item a,b all in user mike's record
        n = dict()  # how many users brought this item
        for user, record in self.train_data.items():
            for item in record.keys():
                n.setdefault(item, 0)
                n[item] += 1
                c.setdefault(item, {})
                for other_item in record.keys():
                    if other_item == item:
                        continue
                    c[item].setdefault(other_item, 0)
                    c[item][other_item] += 1/math.log(1+len(record)*1.0)# add penality for who buy many things
        sim_max = dict()
        for i, co_exist in c.items():
            self.sim_matrix.setdefault(i, {})

            for j in co_exist.keys():
                sim_max.setdefault(j, 0.0)
                self.sim_matrix[i][j] = co_exist[j] / math.sqrt(n[i] * n[j])
                if self.sim_matrix[i][j] > sim_max[j]:
                    sim_max[j] = self.sim_matrix[i][j]
        # regularization for sim score
        for item, sim_score_matrix in self.sim_matrix.items():
            for related_item in sim_score_matrix.keys():
                self.sim_matrix[item][related_item] = self.sim_matrix[item][related_item] / sim_max[related_item]

    # recommend strategy: based on histoic record for each item the user bought, for one item i
    # select k item which is similiar with this item
    # calculate k items recommendation score
    # the score is score i from user record * similarity i,j( j from k items)
    def recommend(self,user, k=5, n=10):

        rank = dict()
        user_record = self.train_data[user]
        for item, score in user_record.items():
            sorted_sim_score = sorted(self.sim_matrix[item].items(), key=lambda x: x[1], reverse=True)[:k]

            for other_item, sim_score in sorted_sim_score:
                if other_item in user_record.keys():
                    continue
                rank.setdefault(other_item, 0)
                rank[other_item] += score * sim_score
        return sorted(rank.items(), key=lambda x: x[1], reverse=True)[:n]
    # evelate model by call back, precision, coverage, popularity rate

    def evaluate(self):

        # call back, precision
        hit = 0
        rec_count = 0
        test_count = 0
        # coverage
        total_rec_movies = set()
        # popularity
        # next time!!!
        # get concide users
        """co_exist_user = list(set(self.train_data.keys()) & set(self.test_data.keys()))
        for user in co_exist_user:
            test_movies = self.test_data[user].keys()
            rec_movies = self.recommend(user)
            hit += len(set(test_movies) & set(rec_movies))
            rec_count += len(rec_movies)
            test_count += len(test_movies)
            for rec_movie in rec_movies:
                total_rec_movies.add(rec_movie)"""
        for i, user in enumerate(self.train_data):
            if i % 500 == 0:
                print ('recommended for %d users' % i)
            test_movies = self.test_data.get(user, {})
            rec_movies = self.recommend(user)
            for movie, _ in rec_movies:
                if movie in test_movies:
                    hit += 1
                total_rec_movies.add(movie)

            rec_count += 10
            test_count += len(test_movies)

        precison = hit / (1.0 * rec_count)
        call_back = hit / (1.0 * test_count)
        coverage = len(rec_movies) / (1.0 * len(self.movieset))
        print "precision rate is %.4f\ncallback rate is %.4f\ncoverage rate is %.4f\n" % (precison, call_back, coverage)


if __name__ == '__main__':

    with open('/Users/cni/PycharmProjects/recommender_system/data/ml-100k/u.item') as f:
        lines = f.readlines()
    movie_map = {x.split('|')[0] : x.split('|')[1] for x in lines}
    filepath = '/Users/cni/PycharmProjects/recommender_system/data/ml-100k/u.data'
    movielens = ItemBased(filepath)
    movielens.train_test_split()
    movielens.generate_sim_matrix()
    movielens.evaluate()
    #get concide users
    co_exist_user = list(set(movielens.train_data.keys()) & set(movielens.test_data.keys()))

    random_user = random.choice(co_exist_user)

    rec_list = [movie_map[x[0]] for x in movielens.recommend(random_user, 3)]
    user_list_in_test = [movie_map[x] for x in movielens.test_data[random_user].keys()]
    print rec_list
    print user_list_in_test