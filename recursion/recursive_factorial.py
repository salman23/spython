s = raw_input('Enter a number:>>')
i = int(s)
def factorial(n):
    if n == 0:
        return 1
    else :
        return n*factorial(n-1)
print factorial(i)
