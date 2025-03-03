"""buithienkhiem-25/2/2025"""
def sieve_of_eratosthenes(N):
    primes = []
    num = 2  # Số nguyên tố đầu tiên

    while len(primes) < N:
        is_prime = True
        for prime in primes:
            if prime * prime > num:
                break
            if num % prime == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(num)
        num += 1

    print(primes)


N = int(input("How many prime numbers? "))
sieve_of_eratosthenes(N)
