// Event-level NR response pilot for the LZ 2026 extended-NR analysis.
// Calls the pinned NEST implementation directly; no hand-written g1/g2
// multiplication is used to construct S1c or S2c.
//
// NEST source pin: 423b9745a5bfbb0402514f1d7955e67445de0810
// Detector candidate: LZ_WS2024.hh (LZ SR3 / WS2024).
// NR mean-yield input: LZ 2026 Supplemental Table S5 (15 parameters).
//
// Output conventions:
//   S1c = GetS1(...)[5], corrected phd area, signed (negative = failed
//         NEST's S1 coincidence condition).
//   S2c = GetS2(...)[7], corrected phd area, signed (negative = failed
//         NEST's configured S2 threshold).
//
// This is an NR-only detector-response pilot, not the official LZ likelihood.

#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <vector>

#include "NEST/NEST.hh"
#include "NEST/RandomGen.hh"
#include "Detectors/LZ_WS2024.hh"

namespace {

const std::vector<double> kEnergiesKeV = {
    5.4, 10.0, 50.0, 74.7, 100.0, 150.0, 200.0, 248.0, 269.9};

const std::vector<double> kGenericNRERWidths = {
    0.4, 0.4, 0.04, 0.5, 0.19, 2.25, -0.001,
    0.046452, 0.45, 0.205, -0.2, 0.0, 0.0};

const std::vector<double> kDefaultERYields(10, -1.0);

std::vector<double> ReadParameterVector(const std::string& path,
                                        std::size_t expected_size) {
  std::ifstream input(path);
  if (!input) {
    throw std::runtime_error("Cannot open NR Table S5 parameter file: " + path);
  }
  std::vector<double> values;
  double value = 0.0;
  while (input >> value) {
    if (!std::isfinite(value)) {
      throw std::runtime_error("Non-finite value in parameter file: " + path);
    }
    values.push_back(value);
  }
  if (!input.eof()) {
    throw std::runtime_error("Malformed numeric parameter file: " + path);
  }
  if (values.size() != expected_size) {
    throw std::runtime_error("Expected " + std::to_string(expected_size) +
                             " NR yield parameters, found " +
                             std::to_string(values.size()));
  }
  return values;
}

void CheckFinitePositive(double value, const std::string& label) {
  if (!std::isfinite(value) || value <= 0.0) {
    throw std::runtime_error(label + " must be finite and positive");
  }
}

}  // namespace

int main(int argc, char** argv) {
  if (argc != 6) {
    std::cerr
        << "Usage:\n  lz_2026_nr_event_response "
        << "<ws2024|generic> <events_per_energy> <seed> "
        << "<output.csv> <table_s5_parameters.txt>\n";
    return 2;
  }

  try {
    const std::string baseline = argv[1];
    if (baseline != "ws2024" && baseline != "generic") {
      throw std::invalid_argument("Baseline must be 'ws2024' or 'generic'");
    }

    const int events_per_energy = std::stoi(argv[2]);
    if (events_per_energy <= 0 || events_per_energy > 1000000) {
      throw std::invalid_argument("events_per_energy must be in [1, 1000000]");
    }

    const uint64_t base_seed = std::stoull(argv[3]);
    const std::string output_path = argv[4];
    const std::vector<double> nr_yield_parameters =
        ReadParameterVector(argv[5], 15);

    LZ_Detector_2024 detector;
    NEST::NESTcalc calculator(&detector);

    // Follow the same initialization order used by NEST's runNESTvec:
    // calculate gas gain, then establish liquid density and drift velocity.
    const std::vector<double> g2_parameters = calculator.CalculateG2(0);
    if (g2_parameters.size() != 5) {
      throw std::runtime_error("NEST CalculateG2 returned an unexpected size");
    }

    const double density =
        calculator.SetDensity(detector.get_T_Kelvin(), detector.get_p_bar());
    if (detector.get_inGas()) {
      throw std::runtime_error(
          "LZ_WS2024 settings resolved to gas phase; expected liquid xenon");
    }
    CheckFinitePositive(density, "liquid xenon density");

    const double x_mm = 0.0;
    const double y_mm = 0.0;
    const double field_V_cm = detector.FitEF(x_mm, y_mm, 0.0);
    CheckFinitePositive(field_V_cm, "drift field");

    const double drift_velocity =
        calculator.SetDriftVelocity(detector.get_T_Kelvin(), density,
                                    field_V_cm, detector.get_p_bar());
    CheckFinitePositive(drift_velocity, "electron drift velocity");

    // Put the interaction at the detector's S1 correction reference depth.
    // This makes the central-position S1 spatial correction equal to unity
    // and gives the nominal reference drift time dtCntr.
    const double z_mm =
        detector.get_TopDrift() - drift_velocity * detector.get_dtCntr();
    if (z_mm <= detector.get_cathode() ||
        z_mm >= detector.get_TopDrift()) {
      throw std::runtime_error(
          "Reference-depth interaction lies outside the active drift region");
    }
    const double drift_time_us =
        (detector.get_TopDrift() - z_mm) / drift_velocity;

    const double s2_threshold_phd =
        detector.get_s2_thr() / (1.0 + detector.get_P_dphe());

    std::vector<double> nr_width_parameters;
    if (baseline == "ws2024") {
      nr_width_parameters = detector.get_nr_er_width_params();
    } else {
      nr_width_parameters = kGenericNRERWidths;
    }
    if (nr_width_parameters.size() != 13) {
      throw std::runtime_error("NRERWidthsParam must contain 13 values");
    }

    std::ofstream output(output_path);
    if (!output) {
      throw std::runtime_error("Cannot open output CSV: " + output_path);
    }
    output << std::setprecision(17);
    output
        << "baseline,energy_keV,event_id,field_V_cm,density_g_cm3,"
           "x_mm,y_mm,z_mm,drift_time_us,drift_velocity_mm_per_us,"
           "g1_phd_per_photon,g2_phd_per_electron,s2_threshold_phd,"
           "mean_photons,mean_electrons,photons,electrons,ions,excitons,"
           "recomb_probability,s1c_signed_phd,s2c_signed_phd,"
           "s1_trigger_pass,s2_threshold_pass,log10_s2c_if_pass\n";

    std::cerr << "baseline=" << baseline
              << " events_per_energy=" << events_per_energy
              << " energies=" << kEnergiesKeV.size()
              << " NEST_commit=423b9745a5bfbb0402514f1d7955e67445de0810\n"
              << "density_g_cm3=" << density
              << " field_V_cm=" << field_V_cm
              << " drift_velocity_mm_per_us=" << drift_velocity
              << " z_reference_mm=" << z_mm
              << " drift_time_us=" << drift_time_us
              << " g1=" << detector.get_g1()
              << " g2=" << g2_parameters[3]
              << " s2_threshold_phd=" << s2_threshold_phd << "\n";

    std::vector<int64_t> s1_waveform_time;
    std::vector<int64_t> s2_waveform_time;
    std::vector<double> s1_waveform_amplitude;
    std::vector<double> s2_waveform_amplitude;

    for (std::size_t energy_index = 0;
         energy_index < kEnergiesKeV.size(); ++energy_index) {
      const double energy_keV = kEnergiesKeV[energy_index];

      // Identical seed per energy for the two width baselines. This is a
      // controlled comparison, not a claim of event-by-event identical draws.
      const uint64_t energy_seed =
          base_seed + static_cast<uint64_t>(energy_index) * 1000003ULL;
      RandomGen::rndm()->SetSeed(energy_seed);

      for (int event = 0; event < events_per_energy; ++event) {
        const uint64_t event_id =
            static_cast<uint64_t>(energy_index) *
                static_cast<uint64_t>(events_per_energy) +
            static_cast<uint64_t>(event);

        const NEST::NESTresult result = calculator.FullCalculation(
            NEST::NR, energy_keV, density, field_V_cm,
            detector.get_molarMass(), 54.0, nr_yield_parameters,
            nr_width_parameters, kDefaultERYields, false);

        // FullCalculation returns intrinsic fluctuated quanta. These calls
        // then apply NEST's detector response; do not replace them by g1*Nph
        // and g2*Ne.
        const std::vector<double> s1 = calculator.GetS1(
            result.quanta, x_mm, y_mm, z_mm, x_mm, y_mm, z_mm,
            drift_velocity, drift_velocity, NEST::NR, event_id,
            field_V_cm, energy_keV, NEST::S1CalculationMode::Full, -1,
            s1_waveform_time, s1_waveform_amplitude);

        const std::vector<double> s2 = calculator.GetS2(
            result.quanta.electrons, x_mm, y_mm, z_mm, x_mm, y_mm, z_mm,
            drift_time_us, drift_velocity, event_id, field_V_cm,
            NEST::S2CalculationMode::Full, -1, s2_waveform_time,
            s2_waveform_amplitude, g2_parameters);

        if (s1.size() <= 5 || s2.size() <= 7) {
          throw std::runtime_error("NEST returned a short S1 or S2 vector");
        }

        // NEST uses the sign to retain trigger/threshold status. Preserve it.
        const double s1c_signed = s1[5];
        const double s2c_signed = s2[7];
        const bool s1_trigger_pass = s1c_signed >= 0.0;
        const bool s2_threshold_pass = s2c_signed >= 0.0;
        const double log10_s2 =
            (s2_threshold_pass && s2c_signed > 0.0)
                ? std::log10(s2c_signed)
                : std::numeric_limits<double>::quiet_NaN();

        output << baseline << ',' << energy_keV << ',' << event_id << ','
               << field_V_cm << ',' << density << ',' << x_mm << ',' << y_mm
               << ',' << z_mm << ',' << drift_time_us << ','
               << drift_velocity << ',' << detector.get_g1() << ','
               << g2_parameters[3] << ',' << s2_threshold_phd << ','
               << result.yields.PhotonYield << ','
               << result.yields.ElectronYield << ','
               << result.quanta.photons << ',' << result.quanta.electrons
               << ',' << result.quanta.ions << ',' << result.quanta.excitons
               << ',' << result.quanta.recombProb << ',' << s1c_signed << ','
               << s2c_signed << ',' << (s1_trigger_pass ? 1 : 0) << ','
               << (s2_threshold_pass ? 1 : 0) << ',' << log10_s2 << '\n';
      }
    }

    output.close();
    if (!output) {
      throw std::runtime_error("Failed while writing output CSV");
    }
    std::cerr << "Wrote event-level NEST response: " << output_path << "\n";
    return 0;
  } catch (const std::exception& error) {
    std::cerr << "ERROR: " << error.what() << "\n";
    return 1;
  }
}
