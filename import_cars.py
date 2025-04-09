import requests
from bs4 import BeautifulSoup
import json
import os
from urllib.parse import unquote

def kebab_to_camel_case(kebab_str):
    """Converts kebab-case to Camel Case with spaces"""
    return ' '.join(word.capitalize() for word in kebab_str.split('-'))

def download_image(url, filename, folder='logos', force=False):
    """Downloads and saves an image to disk, checking if it already exists"""
    try:
        if not os.path.exists(folder):
            os.makedirs(folder)
        
        # Try to determine the extension before checking existence
        possible_extensions = ['png', 'jpg', 'jpeg', 'svg', 'webp']
        existing_file = None
        
        # Check if the file already exists with any of the possible extensions
        for ext in possible_extensions:
            test_path = os.path.join(folder, f"{filename}.{ext}")
            if os.path.exists(test_path):
                existing_file = test_path
                break
        
        # If file already exists and force=False, return the existing path
        if existing_file and not force:
            print(f"File already exists: {existing_file} (use --force to download again)")
            return existing_file
        
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        
        # Try to get the file type from Content-Disposition header
        content_disposition = response.headers.get('content-disposition', '')
        if 'filename=' in content_disposition:
            import re
            cd_filename = re.findall('filename=(.+)', content_disposition)
            if cd_filename:
                ext_from_cd = cd_filename[0].strip('"\'').split('.')[-1].lower()
                if ext_from_cd in ['png', 'jpg', 'jpeg', 'svg', 'webp']:
                    extension = ext_from_cd
                    
        # If not found in Content-Disposition, check Content-Type
        if 'extension' not in locals():
            content_type = response.headers.get('content-type', '').lower()
            if 'png' in content_type:
                extension = 'png'
            elif 'jpeg' in content_type or 'jpg' in content_type:
                extension = 'jpg'
            elif 'svg' in content_type:
                extension = 'svg'
            elif 'webp' in content_type:
                extension = 'webp'
            else:
                # Download a bit of content to check the file type
                first_bytes = next(response.iter_content(32))
                
                # Check common file signatures
                if first_bytes.startswith(b'\x89PNG'):
                    extension = 'png'
                elif first_bytes.startswith(b'\xff\xd8'):
                    extension = 'jpg'
                elif b'<svg' in first_bytes:
                    extension = 'svg'
                elif first_bytes.startswith(b'RIFF') and b'WEBP' in first_bytes:
                    extension = 'webp'
                else:
                    # Last resort: try to get from URL
                    from urllib.parse import urlparse
                    path = urlparse(url).path
                    ext_from_url = path.split('.')[-1].split('?')[0].lower()
                    if ext_from_url in ['png', 'jpg', 'jpeg', 'svg', 'webp']:
                        extension = ext_from_url
                    else:
                        extension = 'bin'  # Unknown format
        
        # Sanitize the filename
        filename = "".join(c for c in filename if c.isalnum() or c in ('_', '-')).rstrip()
        full_path = os.path.join(folder, f"{filename}.{extension}")
        
        # If file exists with another extension and we're forcing download,
        # remove the old file if the extension is different
        if existing_file and force and existing_file != full_path:
            os.remove(existing_file)
            print(f"Removed old file: {existing_file}")
        
        # Restart the stream to download the full file
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        
        with open(full_path, 'wb') as f:
            for chunk in response.iter_content(8192):
                if chunk:
                    f.write(chunk)
        
        if existing_file and force:
            print(f"Replaced: {full_path}")
        else:
            print(f"Downloaded: {full_path}")
            
        return full_path
    except Exception as e:
        print(f"Error downloading {url}: {str(e)}")
        return existing_file if existing_file else None

def scrape_car_logos(save_images=False, force_download=False):
    url = "https://car-logos.org/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # Check if JSON file already exists
        json_exists = os.path.exists('car_brands.json')
        existing_brands = []
        
        if json_exists and not force_download:
            try:
                with open('car_brands.json', 'r', encoding='utf-8') as f:
                    existing_brands = json.load(f)
                print(f"Existing car_brands.json file found with {len(existing_brands)} brands.")
                
                # If we don't need to download images, we can return existing data
                if not save_images:
                    print("Use --force to update the data.")
                    return existing_brands
            except Exception as e:
                print(f"Error reading existing JSON file: {str(e)}")
                existing_brands = []
        
        # Make HTTP request
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all brand elements
        brands = []
        brand_links = soup.find_all('a', class_='elementor-post__thumbnail__link')
        
        # Mapping to reuse local paths of existing files
        existing_paths = {}
        if existing_brands:
            for brand in existing_brands:
                if 'name' in brand and 'local_path' in brand:
                    existing_paths[brand['name']] = brand['local_path']
        
        for link in brand_links:
            if link.has_attr('href'):
                try:
                    # Extract brand name from URL
                    brand_url = link['href']
                    brand_kebab = unquote(brand_url.strip('/').split('/')[-1])
                    
                    # Convert to safe filename
                    filename = "".join(c if c.isalnum() or c == '-' else '_' for c in brand_kebab)
                    brand_name = kebab_to_camel_case(brand_kebab)
                    
                    # Extract image URL
                    img = link.find('img')
                    if img and img.has_attr('src'):
                        logo_url = img['src']
                        
                        # Standardize URL
                        if logo_url.startswith('//'):
                            logo_url = f"https:{logo_url}"
                        elif not logo_url.startswith('http'):
                            logo_url = f"https://car-logos.org{logo_url}"
                        
                        # Add to JSON
                        brand_data = {
                            "name": brand_name,
                            "logo": logo_url
                        }
                        
                        # Check if we already have a local path for this brand
                        if brand_name in existing_paths and not force_download:
                            brand_data["local_path"] = existing_paths[brand_name]
                            print(f"Keeping existing file: {existing_paths[brand_name]}")
                        
                        # Download the image if requested
                        elif save_images:
                            saved_path = download_image(logo_url, filename, force=force_download)
                            if saved_path:
                                brand_data["local_path"] = saved_path
                            else:
                                print(f"Failed to download: {brand_name}")
                        
                        brands.append(brand_data)
                except Exception as e:
                    print(f"Error processing {link}: {str(e)}")
                    continue
        
        # Save to JSON file
        with open('car_brands.json', 'w', encoding='utf-8') as f:
            json.dump(brands, f, ensure_ascii=False, indent=2)
            
        print(f"\nSuccess! {len(brands)} brands processed.")
        if save_images:
            downloaded = sum(1 for b in brands if 'local_path' in b)
            print(f"JSON file generated: car_brands.json")
            print(f"Logos available: {downloaded}/{len(brands)} in 'logos/' folder")
        return brands
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Scrape car logos from car-logos.org')
    parser.add_argument('--download', action='store_true', help='Download logos to local folder')
    parser.add_argument('--force', action='store_true', help='Force download even if files already exist')
    args = parser.parse_args()
    
    scrape_car_logos(save_images=args.download, force_download=args.force)