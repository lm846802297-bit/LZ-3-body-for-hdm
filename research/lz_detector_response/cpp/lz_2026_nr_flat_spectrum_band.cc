// Flat-in-recoil-energy NR band pilot following the construction described in LZ 2026 Fig. 2.
// Fixed approximate candidate position from LZ Fig. 3: r=45.9 cm, z=26.4 cm above cathode. Local-position check, not full FV averaging.
#include <cmath>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

#include "NEST/NEST.hh"
#include "NEST/RandomGen.hh"
#include "Detectors/LZ_WS2024.hh"

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
  if (argc != 6) {
    std::cerr << "Usage: lz_2026_nr_flat_spectrum_band E_min_keV E_max_keV "
                 "n_events seed width_set(ws2024|generic)\n";
    return 2;
  }
  try {
    const double e_min = std::stod(argv[1]);
    const double e_max = std::stod(argv[2]);
    const int n_events = std::stoi(argv[3]);
    const long seed = std::stol(argv[4]);
    const std::string width_set = argv[5];
    if (!(e_min > 0. && e_max > e_min) || n_events <= 0)
      throw std::invalid_argument("invalid energy range or event count");
    if (width_set != "ws2024" && width_set != "generic")
      throw std::invalid_argument("width_set must be ws2024 or generic");

    LZ_Detector_2024 detector;
    NEST::NESTcalc calc(&detector);
    RandomGen::rndm()->SetSeed(seed);
    const double density = calc.SetDensity(detector.get_T_Kelvin(), detector.get_p_bar());
    const double x_mm = 459.0, y_mm = 0.0, z_mm = 264.0;
    const double field = detector.FitEF(x_mm, y_mm, z_mm);
    const double drift_speed = calc.SetDriftVelocity(
        detector.get_T_Kelvin(), density, field, detector.get_p_bar());
    const double drift_time = (detector.get_TopDrift()-z_mm)/drift_speed;
    const auto& widths = width_set == "ws2024" ? kLZWS2024Widths : kGenericWidths;
    const auto g2_params = calc.CalculateG2(0);
    const std::vector<double> eryields = default_ERYieldsParam;
    std::vector<int64_t> s1_wf_time, s2_wf_time;
    std::vector<double> s1_wf_amp, s2_wf_amp;

    std::cout << "event,energy_keV,x_mm,y_mm,z_mm,drift_time_us,s1c_phd,s2c_phd,log10_s2c_phd,n_photons,n_electrons\n";
    std::cout << std::setprecision(12);
    for (int i=0; i<n_events; ++i) {
      const double energy = e_min + (e_max-e_min)*RandomGen::rndm()->rand_uniform();
      const auto result = calc.FullCalculation(
          NEST::NR, energy, density, field, detector.get_molarMass(), 54.,
          kLZ2026NRYields, widths, eryields, false);
      const auto& s1 = calc.GetS1(
          result.quanta,x_mm,y_mm,z_mm,x_mm,y_mm,z_mm,drift_speed,drift_speed,
          NEST::NR,static_cast<uint64_t>(i),field,energy,
          NEST::S1CalculationMode::Parametric,-1,s1_wf_time,s1_wf_amp);
      const auto& s2 = calc.GetS2(
          result.quanta.electrons,x_mm,y_mm,z_mm,x_mm,y_mm,z_mm,drift_time,
          drift_speed,static_cast<uint64_t>(i),field,NEST::S2CalculationMode::Full,
          -1,s2_wf_time,s2_wf_amp,g2_params);
      const double s1c=std::abs(s1.at(5)), s2c=std::abs(s2.at(7));
      const double log_s2c=s2c>0.?std::log10(s2c): -999.;
      std::cout<<i<<','<<energy<<','<<x_mm<<','<<y_mm<<','<<z_mm<<','<<drift_time<<','<<s1c<<','<<s2c<<','<<log_s2c<<','
               <<result.quanta.photons<<','<<result.quanta.electrons<<'\n';
    }
  } catch(const std::exception& e) {
    std::cerr<<"ERROR: "<<e.what()<<'\n'; return 1;
  }
  return 0;
}
