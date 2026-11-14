# Upstream AFH / DMFormFactor v6 package

This directory preserves the upstream AFH / DMFormFactor v6 source material used by the nuclear-response calculations.

## Contents

- `dmformfactor-V6.m`: Wolfram Language source package.
- `DarkMatterIV.pdf` and `documentation-standalone.pdf`: accompanying upstream documentation/reference PDFs.

## Usage and provenance

The Xe-131 and natural-xenon AFH studies use the package's built-in default-density isotope definitions. The selected isotope and response convention are documented in the corresponding study README files:

- `research/afh_default_density_xe131/README.md`
- `research/afh_default_density_natural_xenon_halo/README.md`

Keep these files as upstream source assets. Do not edit the package in place to implement a local convention or normalization correction. Put any extraction, translation, wrapper, or validation code in the relevant `research/` study directory, and record the exact source-file checksum there.

The presence of this source package does not mean a native Mathematica run has been completed. Native execution status must be reported from the generated comparison data and metadata, not inferred from the availability of the .m file.
