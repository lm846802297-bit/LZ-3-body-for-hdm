// Full-S1c NR calibration-band proxy using the public LZ EFT2024 NEST configuration.
// Samples uniform recoil energy and uniform active-TPC volume. This is an explicit
// spatial prior proxy, NOT the collaboration's D-D/AmBe source geometry.
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
const std::vector<double> kTableS5 = {
    11.2, 1.1, 0.052, -0.0533, 10.8, 0.53, 1.4,
    0.31, 2.5, 0.50, 1.39, 1.74, 0.0230, 0.0289, 74.7};
}

int main(int argc, char** argv) {
  if (argc != 5) {
    std::cerr << "Usage: lz_2026_nr_full_calibration_band model "
                 "n_events seed energy_max_keV\n"
                 "model: eft2024|tableS5|ws2024|generic\n";
    return 2;
  }
  try {
    const std::string model = argv[1];
    const int n_events = std::stoi(argv[2]);
    const long seed = std::stol(argv[3]);
    const double e_max = std::stod(argv[4]);
    const double e_min = 0.1;
    if (model!="eft2024" && model!="tableS5" && model!="ws2024" && model!="generic")
      throw std::invalid_argument("unknown model family");
    if (n_events<=0 || !(e_max>e_min))
      throw std::invalid_argument("invalid event count or energy maximum");

    LZ_Detector_2024 detector;
    std::vector<double> nr_yields, nr_widths;
    if (model=="eft2024" || model=="tableS5" || model=="generic") {
      detector.SetEFT2024Configuration();
      if (model=="eft2024") {
        nr_yields=detector.get_nr_yield_params();
        nr_widths=detector.get_nr_er_width_params();
      } else if (model=="tableS5") {
        nr_yields=kTableS5;
        nr_widths=detector.get_nr_er_width_params();
      } else {
        nr_yields=default_NRYieldsParam;
        nr_widths=default_NRERWidthsParam;
      }
    } else {
      nr_yields=detector.get_nr_yield_params();
      nr_widths=detector.get_nr_er_width_params();
    }

    NEST::NESTcalc calc(&detector);
    RandomGen::rndm()->SetSeed(seed);
    const double density=calc.SetDensity(detector.get_T_Kelvin(),detector.get_p_bar());
    const double radius=detector.get_radmax();
    const double zmax=detector.get_TopDrift();
    const double A=detector.get_molarMass(), Z=54.;
    const auto g2=calc.CalculateG2(0);
    const std::vector<double> er_yields=default_ERYieldsParam;

    // Separate design RNG ensures identical (E_R,x,y,z) points across model families.
    std::mt19937_64 design_rng(static_cast<uint64_t>(seed));
    std::uniform_real_distribution<double> u(0.0,1.0);
    std::vector<int64_t> s1_wf_time,s2_wf_time;
    std::vector<double> s1_wf_amp,s2_wf_amp;
    std::cout<<"event,model,energy_keV,x_mm,y_mm,z_mm,field_V_cm,drift_time_us,"
               "n_photons,n_electrons,s1c_signed_phd,s2c_signed_phd\n";
    std::cout<<std::setprecision(12);

    for(int i=0;i<n_events;++i) {
      const double energy=e_min+(e_max-e_min)*u(design_rng);
      const double r=radius*std::sqrt(u(design_rng));
      const double phi=2.0*M_PI*u(design_rng);
      const double x=r*std::cos(phi), y=r*std::sin(phi);
      const double z=0.5+ (zmax-1.0)*u(design_rng);
      const double field=detector.FitEF(x,y,z);
      const double drift_speed=calc.SetDriftVelocity(
          detector.get_T_Kelvin(),density,field,detector.get_p_bar());
      const double drift_time=(zmax-z)/drift_speed;
      const auto result=calc.FullCalculation(
          NEST::NR,energy,density,field,A,Z,nr_yields,nr_widths,er_yields,false);
      const auto& s1=calc.GetS1(
          result.quanta,x,y,z,x,y,z,drift_speed,drift_speed,NEST::NR,
          static_cast<uint64_t>(i),field,energy,NEST::S1CalculationMode::Parametric,
          -1,s1_wf_time,s1_wf_amp);
      const auto& s2=calc.GetS2(
          result.quanta.electrons,x,y,z,x,y,z,drift_time,drift_speed,
          static_cast<uint64_t>(i),field,NEST::S2CalculationMode::Full,
          -1,s2_wf_time,s2_wf_amp,g2);
      std::cout<<i<<','<<model<<','<<energy<<','<<x<<','<<y<<','<<z<<','
               <<field<<','<<drift_time<<','<<result.quanta.photons<<','
               <<result.quanta.electrons<<','<<s1.at(5)<<','<<s2.at(7)<<'\n';
    }
  } catch(const std::exception& e) {
    std::cerr<<"ERROR: "<<e.what()<<'\n'; return 1;
  }
  return 0;
}
