// Stratified true-NR response samples for 1/5/10 keV grid convergence.
// Each 1-keV stratum has equal Monte Carlo statistics; two independent event
// halves are labelled replica=0,1. This is a uniform-active-TPC volume proxy,
// not the collaboration's calibration-source geometry or full event selection.
#include <algorithm>
#include <cmath>
#include <cstdint>
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
const std::vector<double> kTableS5 = {
    11.2, 1.1, 0.052, -0.0533, 10.8, 0.53, 1.4,
    0.31, 2.5, 0.50, 1.39, 1.74, 0.0230, 0.0289, 74.7};
}

int main(int argc, char** argv) {
  if (argc != 7 && argc != 8) {
    std::cerr << "Usage: lz_2026_nr_stratified_energy_response "
                 "model events_per_bin seed energy_min_keV "
                 "energy_max_keV energy_bin_width_keV [events_per_keV]\n"
                 "Optional events_per_keV scales each bin's event count to its "
                 "actual width, including a partial terminal bin.\n"
                 "model: eft2024|tableS5|ws2024|generic\n";
    return 2;
  }
  try {
    const std::string model = argv[1];
    const int events_per_bin = std::stoi(argv[2]);
    const long seed = std::stol(argv[3]);
    const double e_min = std::stod(argv[4]);
    const double e_max = std::stod(argv[5]);
    const double bin_width = std::stod(argv[6]);
    const double events_per_keV = (argc == 8) ? std::stod(argv[7]) : 0.0;

    if (model != "eft2024" && model != "tableS5" &&
        model != "ws2024" && model != "generic")
      throw std::invalid_argument("unknown response model");
    if (events_per_bin < 2 || events_per_bin % 2 != 0 ||
        !(e_max > e_min) || !(bin_width > 0.) ||
        (argc == 8 && !(events_per_keV > 0.)))
      throw std::invalid_argument(
          "require even events_per_bin >= 2, e_max > e_min, bin_width > 0, "
          "and positive optional events_per_keV");

    LZ_Detector_2024 detector;
    std::vector<double> nr_yields, nr_widths;
    if (model == "eft2024" || model == "tableS5" || model == "generic") {
      detector.SetEFT2024Configuration();
      if (model == "eft2024") {
        nr_yields = detector.get_nr_yield_params();
        nr_widths = detector.get_nr_er_width_params();
      } else if (model == "tableS5") {
        nr_yields = kTableS5;
        nr_widths = detector.get_nr_er_width_params();
      } else {
        nr_yields = default_NRYieldsParam;
        nr_widths = default_NRERWidthsParam;
      }
    } else {
      nr_yields = detector.get_nr_yield_params();
      nr_widths = detector.get_nr_er_width_params();
    }

    NEST::NESTcalc calc(&detector);
    RandomGen::rndm()->SetSeed(seed);
    const double density =
        calc.SetDensity(detector.get_T_Kelvin(), detector.get_p_bar());
    const double radius = detector.get_radmax();
    const double zmax = detector.get_TopDrift();
    const double A = detector.get_molarMass();
    const double Z = 54.;
    const auto g2_params = calc.CalculateG2(0);
    const std::vector<double> er_yields = default_ERYieldsParam;

    // This RNG fixes (E_R,x,y,z) design points independently of NEST's
    // internal random stream. All response families use the same seed.
    std::mt19937_64 design_rng(static_cast<uint64_t>(seed));
    std::uniform_real_distribution<double> u(0.0, 1.0);

    std::vector<int64_t> s1_wf_time, s2_wf_time;
    std::vector<double> s1_wf_amp, s2_wf_amp;
    std::cout
        << "event,replica,energy_bin_index,energy_bin_low_keV,"
           "energy_bin_high_keV,energy_keV,x_mm,y_mm,z_mm,field_V_cm,"
           "drift_time_us,n_photons,n_electrons,s1c_signed_phd,"
           "s1c_abs_phd,s1r_abs_phd,s1_spike_count,s1_coincidence_pass,"
           "s2c_signed_phd,s2c_abs_phd,s2r_abs_phd,s2_threshold_pass\n";
    std::cout << std::setprecision(12);

    int64_t event_index = 0;
    const int n_bins = static_cast<int>(
        std::ceil((e_max - e_min) / bin_width - 1.e-12));

    for (int ibin = 0; ibin < n_bins; ++ibin) {
      const double elo = e_min + ibin * bin_width;
      const double ehi = std::min(e_max, elo + bin_width);
      if (!(ehi > elo)) continue;

      int events_this_bin = events_per_bin;
      if (argc == 8) {
        const double requested = events_per_keV * (ehi - elo);
        const long long rounded = std::llround(requested);
        if (std::abs(requested - static_cast<double>(rounded)) > 1.e-9 ||
            rounded < 2 || rounded % 2 != 0) {
          throw std::invalid_argument(
              "events_per_keV times each bin width must be an even integer >= 2");
        }
        events_this_bin = static_cast<int>(rounded);
      }
      const int half = events_this_bin / 2;
      for (int ievt = 0; ievt < events_this_bin; ++ievt) {
        const int replica = (ievt < half) ? 0 : 1;
        const double energy = elo + (ehi - elo) * u(design_rng);

        // Uniform in active-TPC cylindrical volume: r=R*sqrt(U), phi~U,
        // z~U. This is explicitly a spatial proxy, not the 4.71-t FV map.
        const double r = radius * std::sqrt(u(design_rng));
        const double phi = 2.0 * M_PI * u(design_rng);
        const double x = r * std::cos(phi);
        const double y = r * std::sin(phi);
        const double z = 0.5 + (zmax - 1.0) * u(design_rng);

        const double field = detector.FitEF(x, y, z);
        const double drift_speed = calc.SetDriftVelocity(
            detector.get_T_Kelvin(), density, field, detector.get_p_bar());
        const double drift_time = (zmax - z) / drift_speed;

        const auto result = calc.FullCalculation(
            NEST::NR, energy, density, field, A, Z,
            nr_yields, nr_widths, er_yields, false);
        const auto& s1 = calc.GetS1(
            result.quanta, x, y, z, x, y, z, drift_speed, drift_speed,
            NEST::NR, static_cast<uint64_t>(event_index), field, energy,
            NEST::S1CalculationMode::Parametric, -1,
            s1_wf_time, s1_wf_amp);
        const auto& s2 = calc.GetS2(
            result.quanta.electrons, x, y, z, x, y, z, drift_time,
            drift_speed, static_cast<uint64_t>(event_index), field,
            NEST::S2CalculationMode::Full, -1,
            s2_wf_time, s2_wf_amp, g2_params);

        // NEST's sign convention flags S1-coincidence and S2-threshold failures.
        const double s1c_signed = s1.at(5);
        const double s2c_signed = s2.at(7);
        const double s1c_abs = std::abs(s1c_signed);
        const double s1r_abs = std::abs(s1.at(4));
        const double s2c_abs = std::abs(s2c_signed);
        const double s2r_abs = std::abs(s2.at(6));
        const int s1_coin_pass = (s1c_signed > 0.0) ? 1 : 0;
        const int s2_threshold_pass = (s2c_signed > 0.0) ? 1 : 0;

        std::cout << event_index << ',' << replica << ',' << ibin << ','
                  << elo << ',' << ehi << ',' << energy << ','
                  << x << ',' << y << ',' << z << ',' << field << ','
                  << drift_time << ',' << result.quanta.photons << ','
                  << result.quanta.electrons << ',' << s1c_signed << ','
                  << s1c_abs << ',' << s1r_abs << ',' << s1.at(8) << ','
                  << s1_coin_pass << ',' << s2c_signed << ','
                  << s2c_abs << ',' << s2r_abs << ','
                  << s2_threshold_pass << '\n';
        ++event_index;
      }
    }
  } catch (const std::exception& e) {
    std::cerr << "ERROR: " << e.what() << '\n';
    return 1;
  }
  return 0;
}
