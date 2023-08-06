#ifndef EXPONENTIALDistribution_HPP
#define EXPONENTIALDistribution_HPP

#include <ostream>
#include "InvalidParameter.hpp"
#include "ProbabilityDistribution.hpp"

namespace statistics {

    /**
     * Distrubtion Models a exponentially distributed random variable.
     */
class ExponentialDistribution : public ProbabilityDistribution {
    public:
        /// Lambda parameter for an exponentional distrubtion.
        const double lambda;

        /**
         * Constructs a new ExponentialDistrubtion.
         */
        ExponentialDistribution(const double lambda) : lambda(lambda) {
            if (lambda <= 0.0) {
                throw InvalidParameter("Exponential distrubtions must have a lambda value greater than zero.");
            }
        }

        virtual ~ExponentialDistribution() {}

        double pdf(const double x) const;

        double cdf(const double x) const;

        double expectedvalue() const;

        double variance() const;

    };

}

#endif // EXPONENTIALDistribution_HPP
