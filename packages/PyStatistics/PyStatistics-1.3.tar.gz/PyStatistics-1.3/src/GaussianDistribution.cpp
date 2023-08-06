#include <cmath>
#include <ostream>
#include "MathFunctions.hpp"
#include "GaussianDistribution.hpp"

namespace statistics {

    double GaussianDistribution::pdf(const double x) const {
        double exponent = -std::pow(x - mu, 2) / (2 * sigma * sigma);
        double denominator = std::sqrt(2*PI) * sigma;
        return std::exp(exponent) / denominator;
    }

    double GaussianDistribution::cdf(const double x) const {
        double erfparam = (SQRT2/2.0) * (x - mu) / sigma;
        return  (1.0 + std::erf(erfparam)) / 2.0;
    }

    double GaussianDistribution::expectedvalue() const {
        return mu;
    }

    double GaussianDistribution::variance() const {
        return sigma*sigma;
    }

    std::ostream& operator<<(std::ostream& os, const GaussianDistribution& dist) {
        os << "Gaussian distributed variable with:" << std::endl
          << "  Mu: " << std::to_string(dist.mu) << std::endl
          << "  Sigma: " << std::to_string(dist.sigma) << std::endl
          << "  E(X): " << std::to_string(dist.expectedvalue()) << std::endl
          << "  Var(X): " << std::to_string(dist.variance()) << std::endl;
        return os;
    }

}
