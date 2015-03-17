import math

def find_first_primes(num):
    primes = []
    a = 1
    while(len(primes) < num):
        a+=1
        if(less_dumb_is_prime(a, primes)):
            primes.append(a)

    return primes


# Tests againsts list of smaller primes
def less_dumb_is_prime(num,first_primes):
    if len(first_primes) == 0:
        return dumb_is_prime(num)
    
    for i in range(0,len(first_primes)):
        if num % first_primes[i] == 0:
            return False
        if first_primes[i] > math.sqrt(num):
                return True

    return dumb_is_prime(num)

# test number to see if any smaller number divides it
def dumb_is_prime(num):

    if num == 2:
        return True

    a = 0
    
    while a < math.sqrt(num):
        a += 2
        if(num % a == 0):
            return False
        
    return True

def run_tests():
    assert(dumb_is_prime(257))
    assert(dumb_is_prime(2))
    assert(dumb_is_prime(3))
    ten_first = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    assert(find_first_primes(10) == ten_first)


def get_diffs(nums):
    diffs = []
    for i in range(1,len(nums)):
        diffs.append(nums[i] - nums[i-1])
    return diffs

def diff_info(num):
    primes = find_first_primes(num)
    diffs = get_diffs(primes)
    print("diffs: "+str(diffs))
    print("max: "+str(max(diffs)))

run_tests()
diff_info(10000)
