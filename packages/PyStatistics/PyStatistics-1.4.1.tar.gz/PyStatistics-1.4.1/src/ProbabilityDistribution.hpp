#ifndef PROBABILITYDISTRIBUTION_HPP
#define PROBABILITYDISTRIBUTION_HPP

#include <ostream>

namespace statistics {

    /**
     * Abstract base class for a continuous probability distribution.
     */
    class ProbabilityDistribution {

    public:
        /**
         * Virtual destructor.
         */
        virtual ~ProbabilityDistribution() {}

        /**
         * Returns the probability density function, evaluated at x.
         */
        virtual double pdf(double x) const = 0;

        /**
         * Returns the cumulative distribution function, evaluated at x.
         */
        virtual double cdf(double x) const = 0;

        /**
         * Returns the expected value of the distribution.
         */
        virtual double expectedvalue() const = 0;

        /**
         * Returns the variance of the distribution.
         */
        virtual double variance() const = 0;

    };

}

#endif // PROBABILITYDISTRIBUTION_HPP
