# IDE(uy) Controls

## Short Description

Set of controls for satellite images and some vector products generated from them.

## Context

These scripts were developed in order to assist the control of raster and vector data result of the project "Proyecto de producción y control de Ortoimágenes, Modelos Digitales de Elevación y Cartografía", carry by IDE (1).

IDE is the Uruguayan national agency that establishes public standards for global access and the exchange of geographic information in Uruguay.

The project produced and certified digital ortho-images of all national coverage, digital terrain models and basic cartography at a scale of 1: 10,000.

## Folder Structure

* **controls** _(controls source code)_
  * **commons_controls** _(share funtionality for timing programs and file handling)_
  * **db_division**
  * **imagery_controls** _(image handling functionality and main program for imagery data controls)_
  * **postgis_controls** _(postgis database handling functionality and main program for vectorial data controls)_
  * **pyqgis_controls**
* **locales** _(locales files)_
  * **controls**
    * **commons_controls**
    * **imagery_controls**
    * **postgis_controls**
* **scripts** _(bat files for locales generation, test running and environment settings)_
* **sql** _(sql scripts for unit test data generation)_
* **tests** _(unit tests)_
  * **commons_controls_tests**
  * **imagery_controls_tests**
  * **postgis_controls_tests**

## Imagery Data Controls

### General Imagery Program

```bash
> python imagery_controls.py $input_folder $output_folder --control $control  --conform $conform_value --deviation $deviation_value
```

`Control = { pixel_size, dig_level, bands_len, rad_balance, nodata, aall }`

The `$input_folder` can be recursive explored adding the option `--recursive`. By default, this option is `False` (`--non-recursive`).

Help can be display with option `-h`.

### Pixel size (_pixel_size_)

Analize that every _.tif_ file of a directory complies with a stablish spatial resolution given by the pixel size.

If the program is executed with the option `--twf`, then if found, _.twf_ files will be used first.

### Digital level (_dig_level_)

Analize that every _.tif_ file of a directory complies with a stablished digital level given by the datatype of the bands.

### Number of Bands (_bands_len_)

Analize that every _.tif_ file of a directory complies with a stablish spectral resolution given by the number of bands.

### Radiometric Balance (_rad_balance_)

Analize that every _.tif_ file of a directory complies with a stablished radiometric balance given by the percentage of pixels in the extremes values.

### _NODATA_ Percentage (_nodata_)

Analize that every _.tif_ file of a directory complies with a stablished percentage of `NODATA` pixels.

## Vectorial Data Controls

### General Vectorial Program

```bash
> python postgis_controls.py $dbname $dbschema $user $password $output_folder --control $control --host $host --port $port --summary $summary
```

`Rule = { invalid, duplicate, multipart, intersect, null, aall }`

The `$input_folder` can be recursive explored adding the option `--recursive`. By default, this option is `False` (`--non-recursive`).

Help can be display with option `-h`.

### Invalids (_invalid)

Search invalid geometries of all tables in a given schema. Uses `ST_Invalid` PostGIS for the task function.

### Duplicates (_duplicate)

Search duplicate geometries of all tables in a given schema.

### Multiparts (multipart_)

Search multipart geometries of all tables in a given schema.

### Not Allowed Intersections (_intersect_)

Search not allowed intersection between geometries of all tables in a given schema. Allowed intersections are taken from a json file passed with the option `--admissibles path\to\admissibles.json`.

The admissibles file has the following format,

```json
{
  "table_i1": ["table_j1", .., "table_k1"],
  "table_i2": ["table_j2", .., "table_k2"],
  ..,
  "table_iN": ["table_jN", .., "table_kN"]
}
```

where `1 <= i,j,k <= N`.

### Null (_nodata_)

Search null geometries of all tables in a given schema.

## References

 1 - ["Proyecto de producción y control de Ortoimágenes, Modelos Digitales de Elevación y Cartografía"](https://www.gub.uy/infraestructura-datos-espaciales/proyecto-produccion-control-ortoimagenes-modelos-digitales-elevacion-cartografia)
