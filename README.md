# Some scripts to manipulate the GRIB files

## Create Highway data using historical H0 time slots 

See Stan Honey talk explaining what it is in [this clip](https://youtu.be/Nl8cGyzakTE?t=1734)  

### Create the set of historical HRRR H0 GRIB files
```bash
python3 gribs-from-aws.py @args/spin-cup-highway.txt
```

### Create set of routes using weather routing software 

I used the [LuckGRIB](https://luckgrib.com/) Here is how I did it:

- LuckGrib->Preferences->Routing 
  - Enable "Allow the solver to accept multiple wind GRIB files"
- Option 1 using Ensemble GRIB
  - Tool->Weather Routing
    - "Your boat" settings ->  "Routing ensemble settings" settings -> try with multiple GRIB files
    - [x] Create routes for all wind variations
    - Click "Solve"
- Option 2 using multiple GRIB files (legacy option)
  - Tool->Weather Routing
    - "Your boat" settings -> try with multiple GRIB files
    - Enter GRIB prefixes as a string "hrrr-2015052018 hrrr-2015052118 hrrr-2015052218"
    - To create this string use this bash command: 
    - ``` ls data/h0-gribs/ | cat - | sed "s/-24.*//g" | tr '\n' ' ' ```
    - Click "Solve"
    
## Compare the HRRR H0 time slot with boat instruments data:
```bash
python3 verify_model.py @args/spin-cup-highway.txt
```
