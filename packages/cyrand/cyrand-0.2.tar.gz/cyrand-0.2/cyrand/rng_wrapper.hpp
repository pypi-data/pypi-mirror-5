#include <ctime>
#include "boost/random/mersenne_twister.hpp"
#include "boost/random/normal_distribution.hpp"
#include "boost/random/gamma_distribution.hpp"
#include "boost/random/exponential_distribution.hpp"
#include "boost/random/uniform_real_distribution.hpp"
#include "boost/random/chi_squared_distribution.hpp"

using namespace boost::random;

template<typename float_t=double>
class rng_sampler {

public:
  typedef float_t result_type;
  
  rng_sampler(mt19937 &in_R) : R(in_R) {}
  rng_sampler() {
    R = mt19937(); 
    R.seed(std::clock());
  }

  result_type normal(result_type mu, result_type sigma) { 
    normal_distribution<result_type> nrm(mu, sigma);
    return nrm(R);
  }
  
  result_type gamma(result_type alpha, result_type beta) {
    gamma_distribution<result_type> gam(alpha);
    return (1/beta)*gam(R);
  }

  result_type chisq(result_type nu) {
    chi_squared_distribution<result_type> chi(nu);
    return chi(R);
  }

  result_type uniform(result_type a, result_type b) {
    uniform_real_distribution<result_type> unif(a, b);
    return unif(R);
  }

  result_type exp(result_type mu) {
    exponential_distribution<result_type> expdist(1/mu);
    return expdist(R);
  }

private:
  mt19937 R;

};
