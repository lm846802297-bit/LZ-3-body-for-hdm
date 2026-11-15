// Directly compare the printed Table S5 vector with the full-precision
// public EFT2024 vector using the pinned NEST GetYieldNR implementation.
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

#include "NEST/NEST.hh"
#include "Detectors/LZ_WS2024.hh"

namespace {
const std::vector<double> kTableS5 = {
    11.2, 1.1, 0.052, -0.0533, 10.8, 0.53, 1.4,
    0.31, 2.5, 0.50, 1.39, 1.74, 0.0230, 0.0289, 74.7};
}

int main(int argc, char** argv) {
  if (argc < 8) {
    std::cerr
        << "Usage: nest_mean_yield_crosscheck density_g_cm3 field_V_cm "
        << "molar_mass_g_mol isotope_mass_number old_w13ev(true|false) "
        << "model(tableS5|eft2024) energy_keV [energy_keV ...]\n";
    return 2;
  }

  try {
    const double density = std::stod(argv[1]);
    const double field = std::stod(argv[2]);
    const double molar_mass = std::stod(argv[3]);
    const double mass_number = std::stod(argv[4]);
    const std::string old_flag = argv[5];
    const std::string model = argv[6];
    if (old_flag != "true" && old_flag != "false") {
      throw std::invalid_argument("old_w13ev must be true or false");
    }
    if (model != "tableS5" && model != "eft2024") {
      throw std::invalid_argument("model must be tableS5 or eft2024");
    }

    LZ_Detector_2024 detector;
    detector.SetEFT2024Configuration();
    detector.set_molarMass(molar_mass);
    detector.set_OldW13eV(old_flag == "true");

    const std::vector<double> nr_parameters =
        model == "tableS5" ? kTableS5 : detector.get_nr_yield_params();
    if (nr_parameters.size() != 15) {
      throw std::runtime_error("selected NR mean-yield vector must have 15 entries");
    }

    NEST::NESTcalc calculator(&detector);
    std::cout
        << "model,energy_keV,photons_mean,electrons_mean,lindhard,exciton_ratio\n";
    std::cout << std::setprecision(17);
    for (int i = 7; i < argc; ++i) {
      const double energy = std::stod(argv[i]);
      const auto result = calculator.GetYieldNR(
          energy, density, field, mass_number, nr_parameters);
      std::cout << model << ","
                << energy << ","
                << result.PhotonYield << ","
                << result.ElectronYield << ","
                << result.Lindhard << ","
                << result.ExcitonRatio << "\n";
    }
  } catch (const std::exception& error) {
    std::cerr << "ERROR: " << error.what() << "\n";
    return 1;
  }
  return 0;
}
