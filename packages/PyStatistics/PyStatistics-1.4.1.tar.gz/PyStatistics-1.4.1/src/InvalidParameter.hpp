#ifndef INVALIDPARAMETER_HPP
#define INVALIDPARAMETER_HPP

#include <string>

namespace statistics {

    /**
     * Distrubtion Models a exponentially distributed random variable.
     */
    class InvalidParameter {

    protected:
        std::string msg;

    public:
        /**
         * Constructs a new InvalidParameter from a string message.
         */
        InvalidParameter(const std::string message): msg(message) {}

        /**
         * Constructs a new InvalidParameter from a C-style string message.
         */
        InvalidParameter(const char* message): msg(message) {}

        virtual ~InvalidParameter() {}

        const char* what() {
            return msg.c_str();
        }

    };

}

#endif // INVALIDPARAMETER_HPP
