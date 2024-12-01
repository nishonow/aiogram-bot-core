# Aiogram Bot Core Template

This repository is a **template** for building Telegram bots with the Aiogram framework. It is designed for simplicity, scalability, and ease of use. You can quickly get started with this structure to focus on building bot features rather than setting up from scratch.

## Features

- **Basic Bot Functions**: Includes handlers for basic commands like `/start` and admin functionalities like `/count`.
- **Modular Structure**: A well-organized folder system for scalability.
- **Database Integration**: Includes SQLite to store user and admin data.
- **Custom Keyboards**: Ready-to-use keyboards for user interaction.


## Installation

### Prerequisites
- Python 3.8 or higher
- Telegram Bot Token (from [BotFather](https://core.telegram.org/bots#botfather))

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/nishonow/aiogram-bot-core.git
   ```

2. Install dependencies:
    ```bash
   pip install -r requirements.txt
    ```

3. Configure the bot: Open config.py and set your bot token and admin IDs:
    ```bash
    BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
    ADMINS = [123456789, 987654321]  # Replace with admin Telegram IDs
    ```

4. Run the bot:
    ```
   python app.py
   ```

## Extending the Template

- **Add Handlers:** Add new features in the `handlers/` folder and import them in `handlers/__init__.py`.

- **Update Keyboards:** Modify or add new keyboard layouts in `core/keyboards.py`.

- **Custom Utilities:** Add shared helper functions in `core/utils.py`.


## Project Structure

```aiogram-bot-core/
├── app.py
├── config.py
├── loader.py
├── requirements.txt
├── LICENSE
├── README.md
├── core/
│   ├── __init__.py
│   ├── db.py
│   ├── keyboards.py
│   ├── utils.py
├── handlers/
│   ├── __init__.py
│   ├── admin.py
│   ├── messages.py
├── db/
│   └── bot.db
```
