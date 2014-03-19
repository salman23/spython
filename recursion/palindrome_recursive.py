st = raw_input('Enter a string>>')
def is_palindrome(st):
    """ Check if the given string is palindrome or not"""
    if st == '' : 
        return True
    else :
        if st[0] != st[len(st)-1]  :
            return False
        else :
            st = st[1:-1]
            return is_palindrome(st)
                
print is_palindrome(st)         
