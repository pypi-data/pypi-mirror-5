#include <cmath>
#include <vector>

namespace statistics {

    double mean(const std::vector<double>& data) {
        double sum = 0.0;
        for (auto it = data.begin(); it != data.end(); it++)
            sum += *it;
        return sum / data.size();
    }

    double variance(const std::vector<double>& data) {
        double sum = 0.0;
        double avg = mean(data);
        for (auto it = data.begin(); it != data.end(); it++)
            sum += std::pow(*it - avg, 2);
        return sum / data.size();
    }

}
