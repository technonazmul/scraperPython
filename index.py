import requests
from bs4 import BeautifulSoup
import csv
import os
import re
import time


# Define the number of times to loop
num_iterations = 6
# Create a list to store data from each iteration
all_product_data = []
counter_for_check_if_first_time = 0
# Initialize a counter for image
counter = 1
for iteration in range(num_iterations):
# URL of the main page with the list of products
    if counter_for_check_if_first_time == 0:
        main_url = "https://www.batteryfactory.co.uk/collections/leisure-batteries/"
    else:
        main_url = "https://www.batteryfactory.co.uk/collections/leisure-batteries/?page="+ str(counter_for_check_if_first_time)

    counter_for_check_if_first_time += 1
    print(counter_for_check_if_first_time)
    # Send an HTTP request to the main page
    main_response = requests.get(main_url)

    # Check if the request to the main page was successful (status code 200)
    if main_response.status_code == 200:
        # Parse the HTML content of the main page
        main_soup = BeautifulSoup(main_response.content, "html.parser")
        # Save the main_soup content to a text file
        # with open("main_soup_content.txt", "w", encoding="utf-8") as text_file:
        #     text_file.write(str(main_soup))

        # print("main_soup content saved to main_soup_content.txt")
       
        #loop break counter
        #loopbreaker = 1
        # Create a list to store data for each product
        product_data_list = []
        # # Extract product links from the main page
        # product_links = [a['href'] for a in main_soup.select('.grid-product__content .grid-product__link ')]

        
        # Find the specific div containing the product grid
        product_grid_div = main_soup.find("div", id="gf-products")
        # Save the content of product_grid_div to a text file
        # with open("product_grid_content.txt", "w", encoding="utf-8") as text_file:
        #     text_file.write(str(product_grid_div))

        # print("product_grid_div content saved to product_grid_content.txt")
        # Extract product links from inside the product grid
        product_links = [a['href'] for a in product_grid_div.select('a.grid-product__link ')]


        
        # Loop through each product link
        for product_link in product_links:
           
            full_product_url = f"https://www.batteryfactory.co.uk{product_link}"
            
            
            # Send an HTTP request to the product page
            product_response = requests.get(full_product_url)

            # Check if the request to the product page was successful (status code 200)
            if product_response.status_code == 200:
                # Parse the HTML content of the product page
                product_soup = BeautifulSoup(product_response.content, "html.parser")

                # Extract title, description, and price
                title = product_soup.find("h1", class_="product-single__title").text.strip()
                description = product_soup.find("div", class_="product-single__description").text.strip()
                description = description + "Starting New Description"
                price = product_soup.find("span", class_="dualPrice").text.strip()
                price = price.replace("GBP", "").strip()
                price = float(price)
                discounted_price = price - (price * 0.2)
                
                # Print the results
                print("Title:", title)
                print("Description:", description)
                print("Price:", discounted_price)

                
                

                # Create a folder to save images
                image_folder = "product_images"
                os.makedirs(image_folder, exist_ok=True)

                # Extract and save images
                image_tag = product_soup.find("div", class_="image-wrap").find("img")
                if image_tag:
                    data_photoswipe_src = image_tag.get("data-photoswipe-src")
                    image_url = data_photoswipe_src if data_photoswipe_src else image_tag.get("src")

                    image_response = requests.get("https:"+image_url)
                    #Remove special character from title
                    image_new_title = re.sub(r'[^\w\s]', '', title)
                    image_filename = os.path.join(image_folder, f"{counter}_{image_new_title.replace(' ', '_')}_image.jpg")

                    with open(image_filename, "wb") as img_file:
                        img_file.write(image_response.content)
                    # Increment the counter
                    counter += 1
                    print(f"Image saved to {image_filename}")
                    # Append data to the product_data_list
                    product_data_list.append([title, description, discounted_price, image_filename])
                    
                else:
                    print("Image not found on the webpage.")
                    # Introduce a delay to avoid rate limiting
                # Add a 1-second delay between requests time.sleep(1)
                all_product_data.extend(product_data_list)
            else:
                print(f"Failed to retrieve the product page ({full_product_url}). Status code:", product_response.status_code)
                # Append the product data from the current iteration to the main list
                
                # Introduce a delay to avoid rate limiting
                # time.sleep(1)  # Add a 1-second delay between requests


    else:
        print("Failed to retrieve the main page. Status code:", main_response.status_code)
# Save data to CSV file
csv_filename = "product_data.csv"

with open(csv_filename, mode='w', newline='', encoding='utf-8') as csv_file:
    csv_writer = csv.writer(csv_file)

    # Write headers
    csv_writer.writerow(["Title", "Description", "Price", "Image Filename"])

    # Write data for all iterations
    csv_writer.writerows(all_product_data)

print(f"Data saved to {csv_filename}")