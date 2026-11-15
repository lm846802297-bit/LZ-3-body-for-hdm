// Paired Parametric/Full S1 and common S2 response for the LZ three-body signal.
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

int main(int argc, char** argv) {
  if (argc != 6) {
    std::cerr << "Usage: lz_2026_nr_paired_s1_mode_2d_response "
                 "events_per_bin seed energy_min_keV energy_max_keV bin_width_keV\n";
    return 2;
  }
  try {
    const int events_per_bin = std::stoi(argv[1]);
    const long seed = std::stol(argv[2]);
    const double e_min = std::stod(argv[3]);
    const double e_max = std::stod(argv[4]);
    const double bin_width = std::stod(argv[5]);
    if (events_per_bin < 2 || events_per_bin % 2 != 0 ||
        !(e_max > e_min) || !(bin_width > 0.0) || seed < 0) {
      throw std::invalid_argument(
          "require even events_per_bin >= 2, non-negative seed, and increasing energy range");
    }

    LZ_Detector_2024 detector;
    detector.SetEFT2024Configuration();
    const auto nr_yields = detector.get_nr_yield_params();
    const auto nr_widths = detector.get_nr_er_width_params();
    const std::vector<double> er_yields = default_ERYieldsParam;

    NEST::NESTcalc calc_quanta(&detector);
    NEST::NESTcalc calc_parametric(&detector);
    NEST::NESTcalc calc_full(&detector);
    NEST::NESTcalc calc_s2(&detector);

    const double density =
        calc_quanta.SetDensity(detector.get_T_Kelvin(), detector.get_p_bar());
    calc_parametric.SetDensity(detector.get_T_Kelvin(), detector.get_p_bar());
    calc_full.SetDensity(detector.get_T_Kelvin(), detector.get_p_bar());
    calc_s2.SetDensity(detector.get_T_Kelvin(), detector.get_p_bar());

    const double radius = detector.get_radmax();
    const double zmax = detector.get_TopDrift();
    const double A = detector.get_molarMass();
    const double Z = 54.0;
    const auto g2_params = calc_s2.CalculateG2(0);

    // Design RNG is independent of NEST's per-event response streams.
    std::mt19937_64 design_rng(static_cast<uint64_t>(seed));
    std::uniform_real_distribution<double> u(0.0, 1.0);
    std::vector<int64_t> param_s1_time, full_s1_time, s2_time;
    std::vector<double> param_s1_amp, full_s1_amp, s2_amp;

    std::cout
        << "event,replica,energy_bin_index,energy_bin_low_keV,energy_bin_high_keV,"
           "energy_keV,x_mm,y_mm,z_mm,field_V_cm,drift_time_us,n_photons,n_electrons,"
           "s1_param_signed_phd,s1_param_abs_phd,s1_param_raw_phd,s1_param_spike_count,"
           "s1_param_pass,s1_full_signed_phd,s1_full_abs_phd,s1_full_raw_phd,"
           "s1_full_spike_count,s1_full_pass,s2_extracted_electrons,s2_pulse_area_phe,"
           "s2_signed_phd,s2_abs_phd,s2_raw_phd,s2_threshold_pass\n";
    std::cout << std::setprecision(12);

    const int n_bins = static_cast<int>(
        std::ceil((e_max - e_min) / bin_width - 1.e-12));
    const int half = events_per_bin / 2;
    int64_t event_index = 0;

    for (int ibin = 0; ibin < n_bins; ++ibin) {
      const double elo = e_min + ibin * bin_width;
      const double ehi = std::min(e_max, elo + bin_width);
      if (!(ehi > elo)) continue;

      for (int ievt = 0; ievt < events_per_bin; ++ievt) {
        const int replica = (ievt < half) ? 0 : 1;
        const double energy = elo + (ehi - elo) * u(design_rng);

        // Uniform active-TPC cylinder proxy, matching the existing response study.
        const double r = radius * std::sqrt(u(design_rng));
        const double phi = 2.0 * M_PI * u(design_rng);
        const double x = r * std::cos(phi);
        const double y = r * std::sin(phi);
        const double z = 0.5 + (zmax - 1.0) * u(design_rng);
        const double field = detector.FitEF(x, y, z);
        const double drift_speed = calc_quanta.SetDriftVelocity(
            detector.get_T_Kelvin(), density, field, detector.get_p_bar());
        const double drift_time = (zmax - z) / drift_speed;

        const long long event_seed = static_cast<long long>(seed) + 4LL * event_index;
        RandomGen::rndm()->SetSeed(static_cast<long>(event_seed + 1));
        const auto quanta = calc_quanta.FullCalculation(
            NEST::NR, energy, density, field, A, Z,
            nr_yields, nr_widths, er_yields, false);

        // Both S1 modes receive exactly the same intrinsic quanta and true position.
        RandomGen::rndm()->SetSeed(static_cast<long>(event_seed + 2));
        const auto& param_ref = calc_parametric.GetS1(
            quanta.quanta, x, y, z, x, y, z, drift_speed, drift_speed,
            NEST::NR, static_cast<uint64_t>(event_index), field, energy,
            NEST::S1CalculationMode::Parametric, -1,
            param_s1_time, param_s1_amp);
        const std::vector<double> s1_param = param_ref;

        RandomGen::rndm()->SetSeed(static_cast<long>(event_seed + 3));
        const auto& full_ref = calc_full.GetS1(
            quanta.quanta, x, y, z, x, y, z, drift_speed, drift_speed,
            NEST::NR, static_cast<uint64_t>(event_index), field, energy,
            NEST::S1CalculationMode::Full, -1,
            full_s1_time, full_s1_amp);
        const std::vector<double> s1_full = full_ref;

        // One common S2 draw is shared by the two S1 modes.
        RandomGen::rndm()->SetSeed(static_cast<long>(event_seed + 4));
        const auto& s2_ref = calc_s2.GetS2(
            quanta.quanta.electrons, x, y, z, x, y, z, drift_time,
            drift_speed, static_cast<uint64_t>(event_index), field,
            NEST::S2CalculationMode::Full, -1,
            s2_time, s2_amp, g2_params);
        const std::vector<double> s2 = s2_ref;

        const double p_signed = s1_param.at(5);
        const double f_signed = s1_full.at(5);
        const double s2_signed = s2.at(7);
        const int p_pass = p_signed > 0.0 ? 1 : 0;
        const int f_pass = f_signed > 0.0 ? 1 : 0;
        const int s2_pass = s2_signed > 0.0 ? 1 : 0;

        std::cout
            << event_index << ',' << replica << ',' << ibin << ','
            << elo << ',' << ehi << ',' << energy << ','
            << x << ',' << y << ',' << z << ',' << field << ','
            << drift_time << ',' << quanta.quanta.photons << ','
            << quanta.quanta.electrons << ','
            << p_signed << ',' << std::abs(p_signed) << ','
            << std::abs(s1_param.at(4)) << ',' << s1_param.at(8) << ','
            << p_pass << ','
            << f_signed << ',' << std::abs(f_signed) << ','
            << std::abs(s1_full.at(4)) << ',' << s1_full.at(8) << ','
            << f_pass << ','
            << std::abs(s2.at(0)) << ',' << std::abs(s2.at(4)) << ','
            << s2_signed << ',' << std::abs(s2_signed) << ','
            << std::abs(s2.at(6)) << ',' << s2_pass << '\n';

        ++event_index;
      }
    }
  } catch (const std::exception& e) {
    std::cerr << "ERROR: " << e.what() << '\n';
    return 1;
  }
  return 0;
}
