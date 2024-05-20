# repbox-funnel

repbox-funnel is a 3d printable funnel to make it easier to guide filament from the R3PKORD [RepBox](https://www.repkord.com/collections/repbox-2) to a PTFE Tube 

## Code

The source file, `build.py` is used to generate the .stl files -- the 3d models. The other python files represent the shapes that are generated. The various parameters and tolerances are all stored in the .ini files -- it's possible to generate new sized parts by modifying those and executing `python3 ./build.py`

## Recommended Print Settings
layer height: .15mm or lower (lower layer heights reduce friction if the filament is rubbing against the funnel feed)

## Modifying the Source 

The included source file relies on the build123d library. I recommend following the [build123d installation instructions](https://build123d.readthedocs.io/en/latest/installation.html).

Most of changes you would like to make (changing angles, lengths, widths, fittings, etc) can be changed without modifying the code itself but by modifying `settings.ini`.

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

This project is licensed under the terms of the MIT license [MIT](https://choosealicense.com/licenses/mit/)