import streamlit as st
import openai
import requests
from io import BytesIO
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# Set the OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Function to generate ad copy
def generate_ad_copy(product_name, target_audience, tone, key_features, product_description):
    try:
        # Construct the prompt for ad copy
        prompt = f"Create a catchy tagline and description for a product. The product is {product_name}. Target audience: {target_audience}. Tone: {tone}. Key features: {key_features}. Description: {product_description}. Emphasize comfort, sustainability, and performance."
        
        # Send the request to GPT-4 using the correct endpoint for chat models
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are a helpful assistant that generates ad copy."},
                      {"role": "user", "content": prompt}],
            max_tokens=150
        )
        
        ad_copy = response['choices'][0]['message']['content'].strip()
        return ad_copy

    except Exception as e:
        return f"Error: {e}"

# Function to generate image for the ad
def generate_image(prompt, num_images=1):
    try:
        # Request image generation from DALL·E
        response = openai.Image.create(
            prompt=prompt,
            n=num_images,  # Number of images to generate
            size="1024x1024"  # Image size
        )

        # Get URLs of generated images
        image_urls = [image['url'] for image in response['data']]
        return image_urls

    except Exception as e:
        return f"Error: {e}"

# Function to download image
def download_image(image_url):
    try:
        # Request image from URL
        response = requests.get(image_url)
        img = BytesIO(response.content)
        return img
    except Exception as e:
        return f"Error downloading image: {e}"

# Function for A/B Testing
def generate_ab_test_ads(product_name, target_audience, tone, key_features, product_description):
    try:
        # Create two different prompts for the A/B test
        prompt_a = f"Create an ad for {product_name}. Target audience: {target_audience}. Tone: {tone}. Key features: {key_features}. Description: {product_description}. Make it catchy and engaging."
        prompt_b = f"Create a different ad for {product_name}. Target audience: {target_audience}. Tone: {tone}. Key features: {key_features}. Description: {product_description}. Focus on benefits and quality."
        
        # Generate two variations of ad copy
        ad_a = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are a helpful assistant that generates ad copy."},
                      {"role": "user", "content": prompt_a}],
            max_tokens=150
        )
        
        ad_b = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are a helpful assistant that generates ad copy."},
                      {"role": "user", "content": prompt_b}],
            max_tokens=150
        )
        
        # Extract and return both ad versions
        ad_a_copy = ad_a['choices'][0]['message']['content'].strip()
        ad_b_copy = ad_b['choices'][0]['message']['content'].strip()
        
        return ad_a_copy, ad_b_copy

    except Exception as e:
        return f"Error: {e}"

# Streamlit Frontend
st.title("AI Ad Generator")
st.write("Generate creative ads for your products or services using AI!")

# Input fields for the product details
product_name = st.text_input("Product Name", placeholder="e.g., Eco-friendly water bottle")
target_audience = st.text_input("Target Audience", placeholder="e.g., Health-conscious individuals")
tone = st.selectbox("Ad Tone", ["Professional", "Friendly", "Humorous", "Inspirational"])
key_features = st.text_area("Key Features (separate with commas)", placeholder="e.g., Lightweight, Sustainable, Stylish")
product_description = st.text_area("Product Description", placeholder="e.g., Made from recyclable materials and perfect for active lifestyles")

# A/B Testing Option
ab_test_choice = st.selectbox("Do you want to perform A/B testing on the ad copy?", ["No", "Yes"])

# Ask if the user wants to generate an image
generate_image_choice = st.selectbox("Do you want to generate an image for your ad?", ["No", "Yes"])

# Image description input box, appears only if the user chooses "Yes" to generate an image
image_description = None
num_images = 1
if generate_image_choice == "Yes":
    image_description = st.text_input("Enter the image description", placeholder="e.g., Eco-friendly water bottle on a green background")
    num_images = st.slider("Number of Images to Generate", min_value=1, max_value=5, value=1)

# Button to generate both ad copy and image
if st.button("Generate Ad, Image, and Video"):
    if generate_image_choice == "Yes" and not image_description:
        st.error("Please provide an image description to generate the image.")
    else:
        # Generate ad copy
        if ab_test_choice == "Yes":
            ad_a, ad_b = generate_ab_test_ads(product_name, target_audience, tone, key_features, product_description)
            st.subheader("Ad A - Version 1")
            st.write(ad_a)
            st.subheader("Ad B - Version 2")
            st.write(ad_b)
        else:
            ad_text = generate_ad_copy(product_name, target_audience, tone, key_features, product_description)
            st.subheader("Your Generated Ad")
            st.write(ad_text)

        # Video generation notice
        st.subheader("Video Ad Generation")
        st.write("We are currently working on integrating video generation. Stay tuned for future updates!")

        if generate_image_choice == "Yes":
            # Generate the images
            image_urls = generate_image(image_description, num_images)

            # Display generated images
            st.subheader(f"Generated {num_images} Image(s)")
            for i, url in enumerate(image_urls, 1):
                st.image(url, caption=f"Image {i}", use_column_width=True)

                # Download image button
                img = download_image(url)
                st.download_button(
                    label=f"Download Image {i}",
                    data=img,
                    file_name=f"image_{i}.png",
                    mime="image/png"
                )
