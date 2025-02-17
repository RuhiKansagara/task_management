# Task Management README

## Requirements

Before starting, ensure you have the following installed:

- Python 3.8+
- pip (Python package installer)
- virtualenv (optional but recommended)
- Django 5.x
- PostgreSQL

## Installation

Follow these steps to set up the project on your local machine:

1. **Clone the Repository**:

   ```bash
   git clone 

   cd backpackercars-backend
   ```

2. **Set Up a Virtual Environment** (recommended):

   ```bash
   python -m .venv venv

   source .venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**:
   Create a `.env` file in the project root and configure the necessary environment variables:

   ```bash
    cp env.example .env
   ```

## Setup

1. **Apply Migrations**:

   ```bash
   python manage.py migrate
   ```

3. **Run the Development Server**:

   ```bash
   python manage.py runserver
   ```


## Quick Start: Access API Health-Check

1. **Ensure the Server is Running**:
   Run the development server if it isn’t already:

   ```bash
   python manage.py runserver
   ```

2. **Navigate to the Health-Check Route**:
   Open your browser or use a tool like Postman to check the api health:

   You should see a response indicating the health of the API, such as:

   ```json
    {
        "status": "ok",
        "message": "API is working"
    }
   ```

---
