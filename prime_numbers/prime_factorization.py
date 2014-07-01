__author__ = 'salman wahed'


def prime_factor(num):
    for d in seive(num):
        if num % d == 0:
            print d
            num /= d
            if num / d == 1:
                print num
                return
            return prime_factor(num)


def seive(n):
    flag = [True] * n
    flag[0] = flag[1] = False
    for i, is_prime in enumerate(flag):
        if is_prime:
            yield i
            for j in xrange(i + i, n, i):
                flag[j] = False


#prime_factor(7560)

#prime_factor(2160)

#prime_factor(864)