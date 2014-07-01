__author__ = 'salman wahed'


def seive(n):
    flag = [True] * n
    flag[0] = flag[1] = False
    for i, is_prime in enumerate(flag):
        if is_prime:
            yield i
            for j in xrange(i+i, n, i):
                flag[j] = False


for prime in seive(100):
    print prime