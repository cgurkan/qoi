A python implementation of a QOI “Quite OK Image” image converter. It writes PIL Images (PNG files) into QOI files or Opens QOI files and loads them as PIL Images (PNG file).

Original implementation for QOI format can be found on this [link](https://www.qoiformat.org/).

# Setup
<pre>
pip install -r requirements.txt
</pre>

# Usage
<pre>
usage: qoi.py [-h] [-opr OPERATION] -f FILE_PATH [-o [OUT_PATH]]

optional arguments:
  -h, --help            show this help message and exit
  -opr OPERATION, --operation OPERATION
                        operation to perform (e)ncode or (d)ecode
  -f FILE_PATH, --file-path FILE_PATH
                        path to image file to be encoded(png) or decoded (qoi)
  -o [OUT_PATH], --out-path [OUT_PATH]
                        path to encoded (qoi) or decoded (png) image file
</pre>

# Test
<pre>
Encoding:
python .\qoi.py -opr e -f 001.png -o out.qoi
</pre>
<pre>
Decoding
python .\qoi.py -opr d -f 001.qoi -o out.png
</pre>

# License
This project is licensed under the MIT License.
