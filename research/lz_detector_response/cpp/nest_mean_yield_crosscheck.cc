// This executable calls the pinned NEST GetYieldNR implementation directly.\n#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

#include "NEST/NEST.hh"
#include "Detectors/VDetector.hh"

int main(int argc, char** argv) {
  if (argc < 7) {
    std::cerr
        << "Usage: nest_mean_yield_crosscheck density_g_cm3 field_V_cm "
        << "molar_mass_g_mol isotope_mass_number old_w13ev(true|false) "
        << "energy_keV [energy_keV ...]\n";
    return 2;
  }

  try {
    const double density = std::stod(argv[1]);
    const double field = std::stod(argv[2]);
    const double molar_mass = std::stod(argv[3]);
    const double mass_number = std::stod(argv[4]);
    const std::string old_flag = argv[5];
    if (old_flag != "true" && old_flag != "false") {
      throw std::invalid_argument("old_w13ev must be true or false");
    }

    VDetector detector;
    detector.set_molarMass(molar_mass);
    detector.set_OldW13eV(old_flag == "true");
    NEST::NESTcalc calculator(&detector);

    const std::vector<double> nr_parameters = {
        11.2, 1.1, 0.052, -0.0533, 10.8, 0.53, 1.4,
        0.31, 2.5, 0.50, 1.39, 1.74, 0.0230, 0.0289, 74.7};

    std::cout << "energy_keV,photons_mean,electrons_mean,lindhard,exciton_ratio\n";
    std::cout << std::setprecision(17);
    for (int i = 6; i < argc; ++i) {
      const double energy = std::stod(argv[i]);
      const auto result = calculator.GetYieldNR(
          energy, density, field, mass_number, nr_parameters);
      std::cout << energy << ","
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
