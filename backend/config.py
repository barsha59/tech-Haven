import stripe
import os

# Use your Stripe test keys
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_YourTestSecretKey")
STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY", "pk_test_YourTestPublicKey")
