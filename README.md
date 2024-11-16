# BIV Hack | Case 1

## Running

```sh
docker build -t bivhackinfer:latest .
docker run -v ./data:/data bivhackinfer:latest /data/$INPUT_TSV /data/$OUTPUT_TSV
```
