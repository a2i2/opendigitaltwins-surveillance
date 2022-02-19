# Digital Twins Definition Language surveillance extensions

## Ontology Motivation and purpose

This ontology in this repository extends Microsoft's [opendigitaltwins-building](https://github.com/Azure/opendigitaltwins-building) ontology with additional classes and properties for modelling and reasoning about surveillance and security. In particular, it adds the `availability` property to support reasoning about how likely a surveillance system is to actually be functioning at the time of an intrusion, as well as the concept of `failclosed` (e.g. a safe door that locks shut if there are any faults) and `failopen` (e.g. emergency exits that swing open if the building loses power).

## Sample

The sample directory provides a sample digital twin constructed using the ontology. Both a spreadsheet representation and `.json` export are provided.

## Scripts

The scripts directory contains the code to compute a reliability measure, α, of the surveillance system described by the digital twin, taking into account the adversarial nature of intrusion.
