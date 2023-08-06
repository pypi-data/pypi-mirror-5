#ifndef GAUSSIANDISTRIBUTION_HPP
#define GAUSSIANDISTRIBUTION_HPP

#include <ostream>
#include "ProbabilityDistribution.hpp"

namespace statistics {

    /**
     * Class that models a Gaussian, or normal, distribution.
     */
    class GaussianDistribution : public ProbabilityDistribution {


    public:
        /// Mu parameter, the offset parameter for a normal distribution.
        const double mu;

        /// Sigma parameter, the scaling parameter for a normal distribution.
        const double sigma;

        /**
         * Constructs a new GaussianDistribution.
         */
        GaussianDistribution(const double mu, const double sigma) : mu(mu), sigma(sigma) {}

        virtual ~GaussianDistribution() {}

        double pdf(const double x) const;

        double cdf(const double x) const;

        double expectedvalue() const;

        double variance() const;

    };

    std::ostream& operator<<(std::ostream& os, const GaussianDistribution& dist);

}

#endif // GAUSSIANDISTRIBUTION_HPP
