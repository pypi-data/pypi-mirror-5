#include <cmath>
#include "MathFunctions.hpp"
#include "ExponentialDistribution.hpp"

namespace statistics {

    double ExponentialDistribution::pdf(const double x) const {
        if (x < 0)
            return 0.0;
        return lambda * std::exp(-lambda * x);
    }

    double ExponentialDistribution::cdf(const double x) const {
        if (x < 0)
            return 0.0;
        return 1.0 - std::exp(-lambda * x);
    }

    double ExponentialDistribution::expectedvalue() const {
        return 1.0 / lambda;
    }

    double ExponentialDistribution::variance() const {
        return 1.0 / (lambda * lambda);
    }

}
