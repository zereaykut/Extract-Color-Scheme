# Extract-Color-Scheme
Exctract color scheme from given PNG or JPG file using Kmeans algorithm

## Run Application
Clone the repo
```shell
git clone https://github.com/zereaykut/Extract-Color-Scheme
cd Extract-Color-Scheme
```

Create python environment
```shell
python -m venv venv
```

Activate environment in Mac/Linux 
```shell
source venv/bin/activate
```

Activate environment in Windows 
```shell
.\venv\Scripts\activate
```

Install required packages
```shell
pip install -r requirements.txt
```

Run application <br>
-c : number of color outputs <br>
-i : image path <br>
-n : name of json output file
```shell
python exctract_color_scheme.py -c 6 -i sample.jpg -n sample
```
