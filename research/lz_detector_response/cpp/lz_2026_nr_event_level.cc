// Event-level LZ NR pilot using the pinned NEST source and LZ WS2024 detector class.
// Outputs NEST-corrected S1c/S2c in phd plus intrinsic quanta.
// This is a candidate response study, not an official LZ 2026 likelihood reproduction.
#include <cmath>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

#include "NEST/NEST.hh"
#include "Detectors/LZ_WS2024.hh"
#include "NEST/RandomGen.hh"

namespace {
const std::vector<double> kLZ2026NRYields = {
    11.2, 1.1, 0.052, -0.0533, 10.8, 0.53, 1.4,
    0.31, 2.5, 0.50, 1.39, 1.74, 0.0230, 0.0289, 74.7};

const std::vector<double> kGenericWidths = {
    0.4, 0.4, 0.04, 0.5, 0.19, 2.25, -0.001,
    0.046452, 0.45, 0.205, -0.2, 0.0, 0.0};

const std::vector<double> kLZWS2024Widths = {
    0.404, 0.393, 0.0383, 0.497, 0.1906, 2.220,
    0.3, 0.04311, 0.46894, 0.15505, -0.26564, 0.0, 0.0};
}

int main(int argc, char** argv) {
  if (argc != 5) {
    std::cerr << "Usage: lz_2026_nr_event_level energy_keV n_events seed "
                 "width_set(ws2024|generic)\n";
    return 2;
  }
  try {
    const double energy_keV = std::stod(argv[1]);
    const int n_events = std::stoi(argv[2]);
    const long seed = std::stol(argv[3]);
    const std::string width_set = argv[4];
    if (!(energy_keV > 0.) || n_events <= 0)
      throw std::invalid_argument("energy and event count must be positive");
    if (width_set != "ws2024" && width_set != "generic")
      throw std::invalid_argument("width_set must be ws2024 or generic");

    LZ_Detector_2024 detector;
    NEST::NESTcalc calc(&detector);
    NEST::RandomGen::rndm()->SetSeed(seed);

    const double density = calc.SetDensity(detector.get_T_Kelvin(),
                                           detector.get_p_bar());
    const double field = detector.FitEF(0., 0., detector.get_TopDrift() / 2.);
    const double drift_speed = calc.SetDriftVelocity(
        detector.get_T_Kelvin(), density, field, detector.get_p_bar());
    const double z_mm = detector.get_TopDrift() - drift_speed * detector.get_dtCntr();
    if (!(z_mm > 0. && z_mm < detector.get_TopDrift()))
      throw std::runtime_error("reference drift-time position is outside active liquid");

    const double A = detector.get_molarMass();
    const double Z = 54.;
    const auto& widths = (width_set == "ws2024")
        ? kLZWS2024Widths : kGenericWidths;
    const auto g2_params = calc.CalculateG2(0);
    const std::vector<double> eryields = NEST::default_ERYieldsParam;
    std::vector<int64_t> s1_wf_time, s2_wf_time;
    std::vector<double> s1_wf_amp, s2_wf_amp;

    std::cout << "event,energy_keV,density_g_cm3,field_V_cm,x_mm,y_mm,z_mm,"
                 "drift_time_us,n_photons,n_electrons,s1r_phd,s1c_phd,"
                 "s2r_phd,s2c_phd,s1_pass,s2_pass\n";
    std::cout << std::setprecision(12);
    for (int i = 0; i < n_events; ++i) {
      const auto result = calc.FullCalculation(
          NEST::NR, energy_keV, density, field, A, Z,
          kLZ2026NRYields, widths, eryields, false);
      const double drift_time = (detector.get_TopDrift() - z_mm) / drift_speed;
      const auto& s1 = calc.GetS1(
          result.quanta, 0., 0., z_mm, 0., 0., z_mm,
          drift_speed, drift_speed, NEST::NR, static_cast<uint64_t>(i),
          field, energy_keV, NEST::S1CalculationMode::Parametric,
          -1, s1_wf_time, s1_wf_amp);
      const auto& s2 = calc.GetS2(
          result.quanta.electrons, 0., 0., z_mm, 0., 0., z_mm,
          drift_time, drift_speed, static_cast<uint64_t>(i), field,
          NEST::S2CalculationMode::Full, -1, s2_wf_time, s2_wf_amp,
          g2_params);
      // NEST execNEST.cpp store_signals mapping: s1[5]=S1c phd, s2[7]=S2c phd.
      const double s1c = std::abs(s1.at(5));
      const double s2c = std::abs(s2.at(7));
      const double s1r = std::abs(s1.at(4));
      const double s2r = std::abs(s2.at(6));
      std::cout << i << ',' << energy_keV << ',' << density << ',' << field
                << ",0,0," << z_mm << ',' << drift_time << ','
                << result.quanta.photons << ',' << result.quanta.electrons
                << ',' << s1r << ',' << s1c << ',' << s2r << ',' << s2c
                << ',' << (s1c > 0. ? 1 : 0) << ','
                << (s2c > 0. ? 1 : 0) << '\n';
    }
  } catch (const std::exception& e) {
    std::cerr << "ERROR: " << e.what() << '\n';
    return 1;
  }
  return 0;
}
