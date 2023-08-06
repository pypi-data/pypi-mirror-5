#ifndef REGRESSIONS_HPP
#define REGRESSIONS_HPP

#include <vector>
#include <utility>

namespace statistics {

    typedef std::pair<double, double> Point;

    enum RegressionTechnique {
        LINEAR,    /// Linear regression: ax + b
        QUADRATIC  /// Quadratic regression: ax^2 + bx + c
    };

    // Note that the following methods are rather unsafe in returning
    // a raw array without obvious size information. This is
    // largely for demonstration purposes to make us try to wrap
    // an array - it would be far safer to use std::array or std::vector.

    /**
     * Performs a linear regression on the input vector of points.
     * @return a array of polynomial coefficients where the
     * lowest-indexed element is the coefficient of the lowest power.
     */
    double* linreg(const std::vector<Point>& data);

    /**
     * Performs a quadratic regression on the input vector of points.
     * NOTE: this function is unimplemented!
     * What kind of proper C++ project doesn't have stupid functions?
     * @return a array of polynomial coefficients where the
     * lowest-indexed element is the coefficient of the lowest power.
     */
    double* quadreg(const std::vector<Point>& data);

    /**
     * Performs the regression of the given technique on the input points.
     * @param data vector of data point
     * @param t which type of regression to use
     */
    std::vector<double> regression(const std::vector<Point>& data, const RegressionTechnique& t);


}

#endif // REGRESSIONS_HPP
