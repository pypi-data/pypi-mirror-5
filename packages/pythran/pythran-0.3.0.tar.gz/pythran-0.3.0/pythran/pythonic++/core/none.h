#ifndef PYTHONIC_NONE_H
#define PYTHONIC_NONE_H

#include <iterator>
#include <complex>

namespace pythonic {

    struct none_type { none_type(){} };

    static const none_type None;

    template<class T>
        struct none {
            T data;
            bool is_none;
            none() : data(), is_none(false) {}
            none(none_type const&) : data(), is_none(true) {}
            none(T const& data) : data(data), is_none(false) {}
            bool operator==(none_type const &) const { return is_none; }
            template <class O>
                bool operator==(O const & t) const { return not is_none and data == t; }
            operator bool() const { return not is_none and data; }
        };

#define SPECIALIZE_NONE(T)\
    template<>\
    struct none<T> {\
        T data;\
        bool is_none;\
        none() : data(), is_none(false) {}\
        none(none_type const&) : data(), is_none(true) {}\
        none(T const& data) : data(data), is_none(false) {}\
        bool operator==(none_type const &) const { return is_none; }\
        template <class O>\
        bool operator==(O const & t) const { return not is_none and data == t; }\
        operator bool() const { return not is_none and data; }\
        operator size_t() const { return data; }\
        operator long() const { return data; }\
        operator long long() const { return data; }\
        operator double() const { return data; }\
    };\
    T operator+(none<T> const& t0, T const &t1) { return t0.data + t1     ; }\
    T operator+(T const &t0, none<T> const& t1) { return t0      + t1.data; }\
    T operator-(none<T> const& t0, T const &t1) { return t0.data - t1     ; }\
    T operator-(T const &t0, none<T> const& t1) { return t0      - t1.data; }\
    T operator*(none<T> const& t0, T const &t1) { return t0.data * t1     ; }\
    T operator*(T const &t0, none<T> const& t1) { return t0      * t1.data; }\
    T operator/(none<T> const& t0, T const &t1) { return t0.data / t1     ; }\
    T operator/(T const &t0, none<T> const& t1) { return t0      / t1.data; }

    SPECIALIZE_NONE(size_t);
    SPECIALIZE_NONE(long);
    SPECIALIZE_NONE(long long);
    SPECIALIZE_NONE(double);

    template<>
    struct none<std::complex<double>> {
        std::complex<double> data;
        bool is_none;
        none() : data(), is_none(false) {}
        none(none_type const&) : data(), is_none(true) {}
        none(std::complex<double> const& data) : data(data), is_none(false) {}
        bool operator==(none_type const &) const { return is_none; }
        template <class O>
            bool operator==(O const & t) const { return not is_none and data == t; }
        operator bool() const { return not is_none and data.imag() !=0 and data.real() != 0; }
    };
    std::complex<double> operator+(none<std::complex<double>> const& t0, std::complex<double> const &t1) { return t0.data + t1     ; }
    std::complex<double> operator+(std::complex<double> const &t0, none<std::complex<double>> const& t1) { return t0      + t1.data; }
    std::complex<double> operator-(none<std::complex<double>> const& t0, std::complex<double> const &t1) { return t0.data - t1     ; }
    std::complex<double> operator-(std::complex<double> const &t0, none<std::complex<double>> const& t1) { return t0      - t1.data; }
    std::complex<double> operator*(none<std::complex<double>> const& t0, std::complex<double> const &t1) { return t0.data * t1     ; }
    std::complex<double> operator*(std::complex<double> const &t0, none<std::complex<double>> const& t1) { return t0      * t1.data; }
    std::complex<double> operator/(none<std::complex<double>> const& t0, std::complex<double> const &t1) { return t0.data / t1     ; }
    std::complex<double> operator/(std::complex<double> const &t0, none<std::complex<double>> const& t1) { return t0      / t1.data; }

    template <class T0, class T1>
        T0 operator+(T0 const& self, none<T1> const& other) { return self + other.data; }

    template <class T0, class T1>
        T0 operator+(none<T0> const& self, T1 const& other) { return self.data + other; }

    template <class T0, class T1>
         auto operator+(none<T0> const& self, none<T1> const& other)
         -> decltype(none<decltype(self.data + other.data)>(self.data + other.data)) {
             return none<decltype(self.data + other.data)>(self.data + other.data);
         }

    /* for type inference only */
    template <class T>
        typename std::enable_if<!std::is_same<T,none_type>::value, none<T>>::type operator+(T ,none_type ); 
    template <class T>
        typename std::enable_if<!std::is_same<T,none_type>::value, none<T>>::type operator+(none_type , T ); 
    none_type operator+(none_type, none_type);
}

#endif
