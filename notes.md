
In the VIAME tracker branch the file `vital/algo/compute_track_descriptors.h` was changed to accept an
  additional timestamp input as well as changing one of the input types from `track_set_sptr` to
  `object_track_set_sptr`.
This change seems to go against the spirit of a vital algorithm because it restricts the input type.
Shouldn't the more general abstract type be used here?


What is the right way to do this?
