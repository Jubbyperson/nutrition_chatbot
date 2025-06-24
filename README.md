# NutriChat - AI Nutrition Coach

A personalized nutrition tracking and coaching application that uses AI to provide tailored nutrition advice and progress analysis. Created with the help of Cursor AI.

## Features

- User authentication and profile management
- Daily nutrition logging
- Progress tracking with visualizations
- AI-powered nutrition coaching
- Personalized meal plans and recommendations
- Progress analysis and insights

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the project root with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```
5. Run the application:
   ```
   streamlit run app.py
   ```

## Project Structure

- `app.py` - Main application and UI
- `models/` - AI coach implementation
- `db.py` - Database operations
- `logic.py` - Business logic and calculations
- `utils.py` - Utility functions
- `config.py` - Configuration settings

## Requirements

See `requirements.txt` for full list of dependencies.

## Security

- API keys are stored in `.env` file (not committed to git)
   - Create own '.env' file for testing with same format as .env.example
- User passwords are securely hashed
- Database is local and encrypted

## License

This project is for educational purposes.
