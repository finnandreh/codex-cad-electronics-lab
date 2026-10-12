# Evidence method

This repository keeps the evidence claim no larger than the check.

## Observed inputs

- user requirements and requested variants;
- official product drawings, dimensions or datasheets linked in the project;
- native FreeCAD or KiCad files saved by the application;
- exported STEP, STL, Gerber, drill, PDF, SVG and preview files;
- screen capture, narration and caption files where included.

## Software checks

Depending on the project, the supplied evidence records:

- valid base and lid solids;
- zero calculated base/lid and case/reference intersections;
- case-only STEP reopening with the expected solid count;
- closed STL meshes placed at Z=0;
- native project reopening/readback;
- dimensions and object names recovered from saved files;
- schematic/netlist and PCB pin/net comparisons;
- KiCad DRC counts and unconnected-pad counts;
- generated-file SHA-256 hashes;
- video stream and duration checks.

These checks can detect many file, topology, export and consistency failures.
They do not simulate every physical or electrical condition.

## Unknown until physically tested

- fit against the exact purchased board revision;
- screw, insert, cable and connector tolerances;
- print shrinkage, layer adhesion and mechanical strength;
- temperature, airflow and RF performance;
- electrical function, timing and component tolerances;
- PCB assembly, fabrication yield and regulatory compliance.

## Publication boundary

Private receipts, account identifiers, workstation paths, credentials,
customer information and non-redistributable vendor assets are excluded. The
public package contains only the files needed to inspect the bounded technical
claim.

