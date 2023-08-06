#ifndef MATHFUNCTIONS_HPP
#define MATHFUNCTIONS_HPP

#include <cmath>
#include <vector>
#include "InvalidParameter.hpp"

namespace statistics {

    /// Euler's constant
    const double E = std::exp(1.0);

    /// Pi
    const double PI = 4.0 * std::atan(1.0);

    /// Square root of 2.
    const double SQRT2 = std::sqrt(2.0);

    /*
     * Returns the (exact) factorial of n.
     * @throw an InvalidParameter if n is negative
     */
    long factorial(const int n);

    /*
     * Simple function for checking if an integer is prime.
     */
    bool isprime(const int n);

    /*
     * Computes a vector of all prime numbers less than or equal to max.
     */
    std::vector<int> primesuntil(const int max);

    /*
     * Returns an approximation of the factorial of n.
     * @throw an InvalidParameter if n is negative
     */
    double approxfactorial(const int n);

    /**
     * Evalutes a polynomial (given by the coefficients in an array)
     * at the value x.
     * @param length number of coefficients = order of polynomial + 1
     * @param coeff array of coefficients for the polynomial
     * @param x the x-value to compute f(x) for
     */
    double polyeval(const int length, const double coeff[], const double x);

    /**
     * Evalutes a polynomial (given by the coefficients in a vector)
     * at the value x.
     * @param coeff array of coefficients for the polynomial
     * @param x the x-value to compute f(x) for
     */
    double polyeval(const std::vector<double> coeff, const double x);

}

#endif // MATHFUNCTIONS_HPP
