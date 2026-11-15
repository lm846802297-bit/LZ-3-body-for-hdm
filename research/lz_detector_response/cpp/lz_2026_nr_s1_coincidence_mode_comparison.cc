// Paired comparison of NEST Parametric and Full S1 coincidence modes.
// The same intrinsic NR quanta, recoil energy, and true position are supplied
// to both modes. Distinct deterministic RNG seeds are used for the two S1
// detector-response draws. Full mode applies the configured PMT/time-window
// coincidence; Parametric mode uses the analytic PMT-occupancy approximation.
#include <array>
#include <cmath>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <random>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

#include "NEST/NEST.hh"
#include "NEST/RandomGen.hh"
#include "Detectors/LZ_WS2024.hh"

namespace {
using EnergyBin = std::pair<double, double>;
const std::array<EnergyBin, 10> kEnergyBins = {{
    {5.4, 6.4},
    {10.4, 11.4},
    {15.4, 16.4},
    {20.4, 21.4},
    {30.4, 31.4},
    {35.0, 36.0},
    {101.0, 102.0},
    {210.0, 211.0},
    {247.4, 248.4},
    {269.4, 269.9},
}};
}

int main(int argc, char** argv) {
  if (argc != 6) {
    std::cerr
        << "Usage: lz_2026_nr_s1_coincidence_mode_comparison "
           "events_per_energy_bin design_seed quanta_seed_base "
           "parametric_seed_base full_seed_base\n";
    return 2;
  }

  try {
    const int events_per_bin = std::stoi(argv[1]);
    const long design_seed = std::stol(argv[2]);
    const long quanta_seed_base = std::stol(argv[3]);
    const long param_seed_base = std::stol(argv[4]);
    const long full_seed_base = std::stol(argv[5]);

    if (events_per_bin <= 0) {
      throw std::invalid_argument("events_per_energy_bin must be positive");
    }

    LZ_Detector_2024 detector;
    detector.SetEFT2024Configuration();

    const auto nr_yields = detector.get_nr_yield_params();
    const auto nr_widths = detector.get_nr_er_width_params();
    const std::vector<double> er_yields = default_ERYieldsParam;

    NEST::NESTcalc calc_quanta(&detector);
    NEST::NESTcalc calc_parametric(&detector);
    NEST::NESTcalc calc_full(&detector);

    const double density =
        calc_quanta.SetDensity(detector.get_T_Kelvin(), detector.get_p_bar());
    const double radius = detector.get_radmax();
    const double zmax = detector.get_TopDrift();
    const double A = detector.get_molarMass();
    const double Z = 54.;

    // This design RNG is independent of NEST's internal RNG. Since the same
    // design seed is used for both S1 modes, each pair has identical E_R,x,y,z.
    std::mt19937_64 design_rng(static_cast<uint64_t>(design_seed));
    std::uniform_real_distribution<double> u(0.0, 1.0);

    std::vector<int64_t> param_wf_time, full_wf_time;
    std::vector<double> param_wf_amp, full_wf_amp;

    std::cout
        << "event,energy_bin_index,energy_bin_low_keV,energy_bin_high_keV,"
           "energy_keV,x_mm,y_mm,z_mm,field_V_cm,drift_time_us,"
           "n_photons,n_electrons,s1_param_signed_phd,s1_param_abs_phd,"
           "s1_param_spike_count,s1_param_pass,s1_full_signed_phd,"
           "s1_full_abs_phd,s1_full_spike_count,s1_full_pass\n";
    std::cout << std::setprecision(12);

    uint64_t event_index = 0;
    for (size_t ibin = 0; ibin < kEnergyBins.size(); ++ibin) {
      const double elo = kEnergyBins[ibin].first;
      const double ehi = kEnergyBins[ibin].second;

      for (int ievt = 0; ievt < events_per_bin; ++ievt) {
        const double energy = elo + (ehi - elo) * u(design_rng);

        // Uniform active-TPC cylinder proxy, matching the stratified response.
        const double r = radius * std::sqrt(u(design_rng));
        const double phi = 2.0 * M_PI * u(design_rng);
        const double x = r * std::cos(phi);
        const double y = r * std::sin(phi);
        const double z = 0.5 + (zmax - 1.0) * u(design_rng);

        const double field = detector.FitEF(x, y, z);
        const double drift_speed = calc_quanta.SetDriftVelocity(
            detector.get_T_Kelvin(), density, field, detector.get_p_bar());
        const double drift_time = (zmax - z) / drift_speed;

        // Generate the intrinsic NR quanta exactly once for this paired event.
        RandomGen::rndm()->SetSeed(
            quanta_seed_base + static_cast<long>(3 * event_index));
        const auto result = calc_quanta.FullCalculation(
            NEST::NR, energy, density, field, A, Z,
            nr_yields, nr_widths, er_yields, false);

        // Same quanta and position, but independent S1-response random draws.
        RandomGen::rndm()->SetSeed(
            param_seed_base + static_cast<long>(3 * event_index));
        const auto& param_ref = calc_parametric.GetS1(
            result.quanta, x, y, z, x, y, z, drift_speed, drift_speed,
            NEST::NR, event_index, field, energy,
            NEST::S1CalculationMode::Parametric, -1,
            param_wf_time, param_wf_amp);
        const std::vector<double> s1_param = param_ref;

        RandomGen::rndm()->SetSeed(
            full_seed_base + static_cast<long>(3 * event_index));
        const auto& full_ref = calc_full.GetS1(
            result.quanta, x, y, z, x, y, z, drift_speed, drift_speed,
            NEST::NR, event_index, field, energy,
            NEST::S1CalculationMode::Full, -1,
            full_wf_time, full_wf_amp);
        const std::vector<double> s1_full = full_ref;

        const double param_signed = s1_param.at(5);
        const double full_signed = s1_full.at(5);
        const int param_pass = param_signed > 0.0 ? 1 : 0;
        const int full_pass = full_signed > 0.0 ? 1 : 0;

        std::cout
            << event_index << ',' << ibin << ',' << elo << ',' << ehi << ','
            << energy << ',' << x << ',' << y << ',' << z << ',' << field << ','
            << drift_time << ',' << result.quanta.photons << ','
            << result.quanta.electrons << ',' << param_signed << ','
            << std::abs(param_signed) << ',' << s1_param.at(8) << ','
            << param_pass << ',' << full_signed << ','
            << std::abs(full_signed) << ',' << s1_full.at(8) << ','
            << full_pass << '\n';

        ++event_index;
      }
    }
  } catch (const std::exception& e) {
    std::cerr << "ERROR: " << e.what() << '\n';
    return 1;
  }
  return 0;
}
