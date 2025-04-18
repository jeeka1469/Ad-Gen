import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
import openai
import os
import requests
from io import BytesIO
import razorpay
import bcrypt
import pandas as pd

# Load environment variables
load_dotenv()

# API keys
openai.api_key = os.getenv("OPENAI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
razorpay_client = razorpay.Client(auth=(os.getenv("RAZORPAY_KEY_ID"), os.getenv("RAZORPAY_KEY_SECRET")))

# Supabase setup
supabase: Client = create_client(SUPABASE_URL, SUPABASE_API_KEY)

# --- Functions ---

def generate_ad(product_name, target_audience, tone, key_features, product_description):
    try:
        prompt = f"Create a catchy tagline and description for a product. The product is {product_name}. Target audience: {target_audience}. Tone: {tone}. Key features: {key_features}. Description: {product_description}. Highlight its comfort, sustainability, and performance."
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an assistant that generates ad copy."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Error: {e}"

def generate_ab_test(product_name, target_audience, tone, key_features, product_description):
    try:
        prompt_a = f"Create an ad for {product_name}. Target audience: {target_audience}. Tone: {tone}. Key features: {key_features}. Description: {product_description}. Make it catchy and engaging."
        prompt_b = f"Create a different ad for {product_name}. Target audience: {target_audience}. Tone: {tone}. Key features: {key_features}. Description: {product_description}. Focus on benefits and quality."

        ad_a = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt_a}],
            max_tokens=150
        )
        ad_b = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt_b}],
            max_tokens=150
        )
        return ad_a['choices'][0]['message']['content'].strip(), ad_b['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Error: {e}", None

def generate_image(prompt, num_images=1):
    try:
        response = openai.Image.create(prompt=prompt, n=num_images, size="1024x1024")
        return [img['url'] for img in response['data']]
    except Exception as e:
        return [f"Error: {e}"]

def download_image(image_url):
    try:
        response = requests.get(image_url)
        return BytesIO(response.content)
    except Exception as e:
        return f"Error downloading image: {e}"

# --- Streamlit UI ---
st.title("Ad Gen using AI")
menu = ["Login", "Sign Up"]
choice = st.sidebar.selectbox("Menu", menu)

# --- Sign Up ---
if choice == "Sign Up":
    st.subheader("Create a New Account")
    full_name = st.text_input("Full Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Sign Up"):
        try:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            user = supabase.auth.sign_up({"email": email, "password": password})
            supabase.table("users").insert({
                "full_name": full_name,
                "email": email,
                "password": hashed_password.decode('utf-8')
            }).execute()
            st.success("Account created! You can now log in.")
        except Exception as e:
            st.error(f"Signup Error: {e}")

# --- Login ---
elif choice == "Login":
    st.subheader("Login to Your Account")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        try:
            user = supabase.auth.sign_in_with_password({"email": email, "password": password})
            st.session_state["user"] = user
            st.session_state["email"] = email

            admin_check = supabase.table("admins").select("*").eq("email", email).execute()
            if admin_check.data:
                st.success("Welcome Admin!")
                st.title("Admin Dashboard")

                ads_data = supabase.table("ads").select("*").execute()
                ads = ads_data.data

                if ads:
                    df = pd.DataFrame(ads)

                    # 1. Total Ads
                    st.metric("📢 Total Ads Created", len(df))

                    # 2. Top Users
                    st.subheader("👥 Top Users by Ad Count")
                    st.bar_chart(df['user_email'].value_counts().head(5))

                    # 3. Popular Tones
                    st.subheader("🎙️ Most Popular Tones")
                    st.bar_chart(df['tone'].value_counts())

                    # 4. Product Names
                    st.subheader("🛍️ Most Used Product Names")
                    st.dataframe(df['product_name'].value_counts().head(5))

                    # 5. Recent Ads
                    st.subheader("🕒 Recent Ads")
                    st.dataframe(df.sort_values(by="created_at", ascending=False).head(5))

                else:
                    st.info("No ads created yet.")
            else:
                st.success("Login successful!")

        except Exception as e:
            st.error(f"Login Error: {e}")

# --- User Section ---
if "user" in st.session_state and st.session_state["email"] != "admin@gmail.com":
    user_email = st.session_state["email"]
    st.sidebar.success(f"Welcome {user_email}!")

    st.subheader("Generate Your Ad")

    product_name = st.text_input("Product Name")
    target_audience = st.text_input("Target Audience")
    tone = st.selectbox("Ad Tone", ["Professional", "Friendly", "Humorous", "Inspirational"])
    key_features = st.text_area("Key Features")
    product_description = st.text_area("Product Description")
    ab_test_choice = st.selectbox("Do you want to perform A/B testing?", ["No", "Yes"])
    generate_image_choice = st.selectbox("Generate Image?", ["No", "Yes"])

    if generate_image_choice == "Yes":
        image_description = st.text_input("Image Description")
        num_images = st.slider("Number of Images", 1, 5, 1)

    if st.button("Generate Ad, Image, and Video"):
        if ab_test_choice == "Yes":
            ad_a, ad_b = generate_ab_test(product_name, target_audience, tone, key_features, product_description)
            st.subheader("Ad A")
            st.write(ad_a)
            st.subheader("Ad B")
            st.write(ad_b)
            final_ad = ad_a + "\n---\n" + ad_b
        else:
            ad = generate_ad(product_name, target_audience, tone, key_features, product_description)
            st.subheader("Your Ad")
            st.write(ad)
            final_ad = ad

        supabase.table("ads").insert({
            "user_email": user_email,
            "product_name": product_name,
            "target_audience": target_audience,
            "tone": tone,
            "key_features": key_features,
            "product_description": product_description,
            "generated_ad": final_ad
        }).execute()

        if generate_image_choice == "Yes":
            image_urls = generate_image(image_description, num_images)
            st.subheader("Generated Images")
            for i, url in enumerate(image_urls):
                st.image(url, caption=f"Image {i+1}")
                img = download_image(url)
                st.download_button(f"Download Image {i+1}", data=img, file_name=f"image_{i+1}.png", mime="image/png")
