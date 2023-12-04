# OpenMSLA
Open-source resin 3D printer based on masked stereolithography (MSLA) technology

## Purpose

The purpose of the OpenMSLA project is to build an open-source, Python controlled 3D printer that provides operators with an extremely high level of control over printer operation.

## Why?

- As opposed to FDM 3D printing where there is a wide offering of open source 3D printers, almost all commercially available resin printers are closed source.
- Nearly all MSLA resin printers operate on macro based architecture where mahcine parameters are defined on a layerwise basis and these parameters are duplicated for use in every subsequent layer.
  - This does not allow the operate to customize printing parameters beyond very simple ones.

## Objective

The objective of this project is to build a Gcode controlled resin printer that in principle will operate much more like an FDM 3D printer. Using this familiar interface should incentivize adoption and provide machine operators with an extremely high level of control over printing parameters of their printer.
