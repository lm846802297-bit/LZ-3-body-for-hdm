// Flat-in-energy LZ NR response using the public NEST EFT2024 candidate configuration.
// NEST source is pinned externally by the workflow. EFT2024 is a public candidate,
// not a confirmed copy of the collaboration's final 2026 production build.
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <random>
#include <stdexcept>
#include <string>
#include <vector>

#include "NEST/NEST.hh"
#include "NEST/RandomGen.hh"
#include "Detectors/LZ_WS2024.hh"

namespace {
constexpr double kPi = 3.1415926535897932384626433832795;
constexpr double kCandidateXmm = 459.0;
constexpr double kCandidateYmm = 0.0;
constexpr double kCandidateZmm = 264.0;

double uniform01(std::mt19937_64& engine) {
  return std::generate_canonical<double, 53>(engine);
}
}

int main(int argc, char** argv) {
  if (argc != 7) {
    std::cerr << "Usage: lz_2026_nr_flat_spectrum_eft2024 "
                 "E_min_keV E_max_keV n_events seed config(eft2024|ws2024|generic) "
                 "position(candidate|uniform_tpc)\n";
    return 2;
  }
  try {
    const double e_min = std::stod(argv[1]);
    const double e_max = std::stod(argv[2]);
    const int n_events = std::stoi(argv[3]);
    const long seed = std::stol(argv[4]);
    const std::string config = argv[5];
    const std::string position_mode = argv[6];

    if (!(e_min > 0. && e_max > e_min) || n_events <= 0)
      throw std::invalid_argument("invalid energy range or event count");
    if (config != "eft2024" && config != "ws2024" && config != "generic")
      throw std::invalid_argument("config must be eft2024, ws2024, or generic");
    if (position_mode != "candidate" && position_mode != "uniform_tpc")
      throw std::invalid_argument("position must be candidate or uniform_tpc");

    LZ_Detector_2024 detector;
    if (config == "eft2024" || config == "generic")
      detector.SetEFT2024Configuration();
    // The default constructor selects the WS2024 detector/model configuration.

    std::vector<double> nr_yields = detector.get_nr_yield_params();
    std::vector<double> er_yields = detector.get_er_yield_params();
    std::vector<double> nr_er_widths = detector.get_nr_er_width_params();
    if (config == "generic") {
      nr_yields = default_NRYieldsParam;
      er_yields = default_ERYieldsParam;
      nr_er_widths = default_NRERWidthsParam;
    }

    NEST::NESTcalc calc(&detector);
    RandomGen::rndm()->SetSeed(seed);
    std::mt19937_64 input_rng(static_cast<uint64_t>(seed) ^ 0x9e3779b97f4a7c15ULL);

    const double density = calc.SetDensity(detector.get_T_Kelvin(),
                                           detector.get_p_bar());
    const double g2_field = detector.FitEF(0., 0., detector.get_TopDrift()/2.);
    const double drift_speed = calc.SetDriftVelocity(
        detector.get_T_Kelvin(), density, g2_field, detector.get_p_bar());
    if (!(drift_speed > 0.))
      throw std::runtime_error("NEST returned non-positive drift speed");
    const auto g2_params = calc.CalculateG2(0);

    std::vector<int64_t> s1_wf_time, s2_wf_time;
    std::vector<double> s1_wf_amp, s2_wf_amp;

    std::cerr << "config=" << config
              << " position=" << position_mode
              << " NRYieldsParam.size=" << nr_yields.size()
              << " ERYieldsParam.size=" << er_yields.size()
              << " NRERWidthsParam.size=" << nr_er_widths.size()
              << " density_g_cm3=" << density
              << " g1=" << detector.get_g1()
              << " g1_gas=" << detector.get_g1_gas()
              << " s2_threshold_phe=" << detector.get_s2_thr()
              << " electron_lifetime_us=" << detector.get_eLife_us()
              << " drift_speed_mm_us=" << drift_speed << "\n";

    std::cout
      << "event,config,position_mode,energy_keV,x_mm,y_mm,z_mm,r_mm,"
         "drift_time_us,field_V_cm,density_g_cm3,n_photons,n_electrons,"
         "s1c_phd,s2c_phd,log10_s2c_phd\n";
    std::cout << std::setprecision(12);

    for (int i = 0; i < n_events; ++i) {
      const double energy = e_min + (e_max - e_min) * uniform01(input_rng);
      double x_mm = kCandidateXmm, y_mm = kCandidateYmm, z_mm = kCandidateZmm;
      if (position_mode == "uniform_tpc") {
        const double r = detector.get_radmax() * std::sqrt(uniform01(input_rng));
        const double phi = 2. * kPi * uniform01(input_rng);
        x_mm = r * std::cos(phi);
        y_mm = r * std::sin(phi);
        z_mm = 1. + (detector.get_TopDrift() - 2.) * uniform01(input_rng);
      }
      const double r_mm = std::hypot(x_mm, y_mm);
      const double field = detector.FitEF(x_mm, y_mm, z_mm);
      const double drift_time =
          (detector.get_TopDrift() - z_mm) / drift_speed;

      const auto result = calc.FullCalculation(
          NEST::NR, energy, density, field, detector.get_molarMass(), 54.,
          nr_yields, nr_er_widths, er_yields, false);

      const auto& s1 = calc.GetS1(
          result.quanta, x_mm, y_mm, z_mm, x_mm, y_mm, z_mm,
          drift_speed, drift_speed, NEST::NR, static_cast<uint64_t>(i),
          field, energy, NEST::S1CalculationMode::Parametric,
          -1, s1_wf_time, s1_wf_amp);
      const auto& s2 = calc.GetS2(
          result.quanta.electrons, x_mm, y_mm, z_mm, x_mm, y_mm, z_mm,
          drift_time, drift_speed, static_cast<uint64_t>(i), field,
          NEST::S2CalculationMode::Full, -1, s2_wf_time, s2_wf_amp,
          g2_params);

      const double s1c = std::abs(s1.at(5));
      const double s2c = std::abs(s2.at(7));
      const double log_s2c = s2c > 0. ? std::log10(s2c) : -999.;
      std::cout << i << ',' << config << ',' << position_mode << ','
                << energy << ',' << x_mm << ',' << y_mm << ',' << z_mm << ','
                << r_mm << ',' << drift_time << ',' << field << ',' << density
                << ',' << result.quanta.photons << ','
                << result.quanta.electrons << ',' << s1c << ',' << s2c << ','
                << log_s2c << '\n';
    }
  } catch (const std::exception& e) {
    std::cerr << "ERROR: " << e.what() << '\n';
    return 1;
  }
  return 0;
}
