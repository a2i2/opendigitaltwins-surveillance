# Digital Twins Definition Language surveillance extensions

## Motivation and purpose

This repository extends Microsoft's [opendigitaltwins-building](https://github.com/Azure/opendigitaltwins-building) ontology with additional classes and properties for modelling and reasoning about surveillance and security. In particular, it adds the `availability` property to support reasoning about how likely a surveillance system is to actually be functioning at the time of an intrusion, as well as the concept of `failsafe` (e.g. a safe door that locks shut if there are any faults) and `failopen` (e.g. emergency exits that swing open if the building loses power).

Furthermore, it provides a sample digital twin constructed using the ontology.

