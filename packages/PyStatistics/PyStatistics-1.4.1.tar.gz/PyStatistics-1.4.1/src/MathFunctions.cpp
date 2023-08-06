#include <cmath>
#include <math.h>  // for the tgamma function, recently added to C++ though
#include <vector>
#include "MathFunctions.hpp"
#include "InvalidParameter.hpp"

namespace statistics {

    long factorial(const int n) {
        if (n < 0)
            throw InvalidParameter("The factorial function cannot accept negative inputs.");
        long product = 1L;
        for (int i = 2; i <= n; i++)
            product *= i;
        return product;
    }

    bool isprime(const int n) {
        if (n <= 1)
            return false;
        int max = int(std::sqrt(n));
        for (int i = 2; i <= max; i++) {
            if (n % i == 0)
                return false;
        }
        return true;
    }

    std::vector<int> primesuntil(const int max) {
        std::vector<int> primes;
        for (int i = 2; i <= max; i++) {
            if (isprime(i))
                primes.push_back(i);
        }
        return primes;
    }

    double approxfactorial(const int n) {
        if (n < 0)
            throw InvalidParameter("The approxfactorial function cannot accept negative inputs.");
        return tgamma(n + 1);
    }

    double polyeval(const int length, const double coeff[], const double x) {
        double val = 0.0;
        for (int i = 0; i < length; i++) {
            // There is a slightly faster way to evaluate polynomials - but this is so simple!
            val += coeff[i] * std::pow(x, i);
        }
        return val;
    }

    double polyeval(const std::vector<double> coeff, const double x) {
        return polyeval(coeff.size(), &coeff[0], x);
    }

}
