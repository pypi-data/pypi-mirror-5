#ifndef DISCRETESTATS_HPP
#define DISCRETESTATS_HPP

#include <vector>

namespace statistics {

    /**
     * Computes the arithmetic mean of a data set.
     */
    double mean(const std::vector<double>& data);

    /**
     * Computes the variance of a data set.
     */
    double variance(const std::vector<double>& data);

}

#endif // DISCRETESTATS_HPP
