# car_brands.json

A JSON file containing brand names, logos, and the URLs from which the logos were extracted.
All the information were extracted from [Car Logos Website](https://car-logos.org/)

# import_cars.py: Usage Documentation

This script allows you to extract car brand information from car-logos.org, including names and logo URLs, with the option to download the logo images.

## Overview

The `import_cars.py` script performs the following operations:

1. Extracts car brand information from car-logos.org
2. Generates a JSON file with brand names and logo URLs
3. Optionally downloads logo images to a local folder

## Requirements

- Python 3.6+
- Libraries:
  - requests
  - BeautifulSoup4
  - json
  - os
  - urllib

To install the necessary dependencies:

```bash
pip install requests beautifulsoup4
```

## Basic Usage

### Simple Execution (without image download)

To run the script and only generate the JSON file with brand information:

```bash
python import_cars.py
```

### Execution with Image Download

To run the script, generate the JSON file, and download the logo images:

```bash
python import_cars.py --download
```

### Force Download of Images

To force download images even if they already exist locally:

```bash
python import_cars.py --download --force
```

## Output

### JSON File

The script generates a file called `car_brands.json` in the current directory, with a structure like:

```json
[
  {
    "name": "Car Brand Name",
    "logo": "https://example.com/path/to/logo.png",
    "local_path": "logos/car-brand-name.png"  // Only when used with --download
  },
  ...
]
```

### Image Folder

When executed with the `--download` option, the script creates a folder called `logos` in the current directory and saves the logo images there. The filenames are simplified versions of the brand names in kebab-case.

## Main Functions

### `scrape_car_logos(save_images=False, force_download=False)`

Main function that extracts information from the website and optionally downloads images.

**Parameters:**

- `save_images` (bool): If `True`, downloads the logo images. Default: `False`.
- `force_download` (bool): If `True`, forces download even if files already exist. Default: `False`.

**Returns:**

- List of dictionaries with brand information.

### `download_image(url, filename, folder='logos', force=False)`

Downloads and saves an image to disk, checking if it already exists.

**Parameters:**

- `url` (str): Image URL.
- `filename` (str): Base filename (without extension).
- `folder` (str): Folder where to save the image. Default: 'logos'.
- `force` (bool): If `True`, forces download even if file already exists. Default: `False`.

**Returns:**

- Full path of the saved file, or `None` in case of error.

### `kebab_to_camel_case(kebab_str)`

Converts a string in kebab-case format to Camel Case with spaces.

**Parameters:**

- `kebab_str` (str): String in kebab-case format.

**Returns:**

- String in Camel Case format with spaces.

## Error Handling

The script includes basic error handling for:

- Connection failures with the website
- Problems downloading individual images
- Errors processing brand information

Errors are displayed in the console, but the script continues execution to process all possible brands.

## Programmatic Usage Example

```python
from import_cars import scrape_car_logos

# Only extract information
brands = scrape_car_logos(save_images=False)
print(f"Extracted {len(brands)} brands")

# Extract information and download images
brands_with_images = scrape_car_logos(save_images=True)

# Extract information and force download images
brands_forced = scrape_car_logos(save_images=True, force_download=True)
```

## Limitations

- The script depends on the current structure of car-logos.org. Changes to the site layout may affect its functionality.
- Some servers may limit the number of requests in a short period.
- The script checks if images already exist locally before downloading them again, unless the `--force` option is used.
