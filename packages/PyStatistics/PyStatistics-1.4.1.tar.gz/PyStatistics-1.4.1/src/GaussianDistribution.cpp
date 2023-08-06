#include <cmath>
#include <math.h> // for the erf() function, std::erf was added to C++ recently
#include <ostream>
#include <sstream>
#include "GaussianDistribution.hpp"
#include "MathFunctions.hpp"

namespace statistics {

    double GaussianDistribution::pdf(const double x) const {
        double exponent = -std::pow(x - mu, 2) / (2 * sigma * sigma);
        double denominator = std::sqrt(2*PI) * sigma;
        return std::exp(exponent) / denominator;
    }

    double GaussianDistribution::cdf(const double x) const {
        double erfparam = (SQRT2/2.0) * (x - mu) / sigma;
        return  (1.0 + erf(erfparam)) / 2.0;
    }

    double GaussianDistribution::expectedvalue() const {
        return mu;
    }

    double GaussianDistribution::variance() const {
        return sigma*sigma;
    }

    std::ostream& operator<<(std::ostream& os, const GaussianDistribution& dist) {
        os << "Gaussian distributed variable with:" << std::endl
          << "  Mu: " << dist.mu << std::endl
          << "  Sigma: " << dist.sigma << std::endl
          << "  E(X): " << dist.expectedvalue() << std::endl
          << "  Var(X): " << dist.variance() << std::endl;
        return os;
    }

}
