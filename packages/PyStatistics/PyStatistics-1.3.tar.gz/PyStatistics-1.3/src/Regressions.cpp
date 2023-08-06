#include <exception>
#include <utility>
#include <vector>
#include "Regressions.hpp"
#include "InvalidParameter.hpp"

namespace statistics {

    double* linreg(const std::vector<Point>& data) {
        const int n = data.size();
        double sumX = 0.0;
        double sumY = 0.0;
        double sumXY = 0.0;
        double sumXSq = 0.0;
        double sumYSq = 0.0;

        for (auto it = data.begin(); it != data.end(); it++) {
            double x = it->first;
            double y = it->second;
            sumX += x;
            sumXSq += x*x;
            sumXY += x*y;
            sumY += y;
            sumYSq += y*y;
        }

        double slope = (n*sumXY - sumX*sumY) / (n*sumXSq - sumX*sumX);
        double intercept = (sumY - slope*sumX) / n;
        double *ret = new double[2];
        ret[0] = intercept;
        ret[1] = slope;
        return ret;
    }

    double* quadreg(const std::vector<Point>& data) {
        throw std::exception();
    }

    std::vector<double> regression(const std::vector<Point>& data,
                                   const RegressionTechnique& t) {
        double* outArray;
        int outLen;

        if (t == LINEAR) {
            outArray = linreg(data);
            outLen = 2;
        } else if (t == QUADRATIC) {
            outArray = quadreg(data);
            outLen = 3;
        } else {
            std::string msg = "Only Linear and Quadratic Regression are supported.";
            throw InvalidParameter(msg);
        }

        std::vector<double> v;
        v.assign(outArray, outArray + outLen);
        return v;
    }

}
