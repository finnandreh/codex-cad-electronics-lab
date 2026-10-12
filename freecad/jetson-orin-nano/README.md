# Jetson Orin Nano reference developer-kit case

References:

- [NVIDIA Jetson downloads](https://developer.nvidia.com/embedded/downloads)
- [Jetson Orin Nano developer-kit hardware layout](https://docs.nvidia.com/jetson/orin-nano-devkit/user-guide/latest/hardware_layout.html)

The enclosure was designed around an official NVIDIA P3766/P3768
carrier/cooler reference with recorded carrier bounds of 100 × 79 × 1.57 mm.
The generated case envelope is 116 × 105 × 47.65 mm with 2.4 mm wall, floor
and lid values.

The public native FreeCAD file is a dedicated case-only copy. Its
`BoardReference` object was removed, the editable operation history was
preserved, the file reopened successfully, and the base/lid volumes remained
unchanged. The STEP and two STL files also contain only generated enclosure
geometry. No NVIDIA board/cooler model is redistributed.

Recorded checks: two valid case solids after native reopen, case-only STEP
with two solids and closed base/lid STL meshes. Earlier private checks recorded
zero board/cooler-case intersections, but the public case does not bundle the
vendor reference used for that comparison.

The exact user carrier variant, physical retention, connector/cable fit,
cooling, RF behaviour, screws and printed fit have not been tested. This is
not a validated cooling design.

