# AoCH Leaderboard

## Overview

This project shows the current statistics and leaderboard of CH members for the AoC.

## Guidelines

This script follows the guidelines stated by [Advent of Code](https://www.reddit.com/r/adventofcode/wiki/faqs/automation), namely:
- it includes the emails of the maintainers and a link to the current repo in the User-Agent header for all outbound requests;
- it throttles the requests made to the website by only requesting (private) leaderboard updates every 15 minutes (`L55: get_data()`);
- the puzzle for each day is requested only once and 'cached' runtime only, so restarting the server removes the 'cache' (`L79: get_day_assignment()`).

Do not misuse this leaderboard we created and if you decide to fork this repository, please update the User-Agent to your own email and repository.

## Installation

To run the project, follow these steps:

### 1. Create a Virtual Environment

Use the following command to create a virtual environment named "venv" within your project folder:

```bash
python -m venv venv
```

### 2. Activate the Virtual Environment

Activate the virtual environment. Use one of the following commands based on your operating system:

- On Windows:

  ```bash
  venv\Scripts\activate
  ```

- On Unix or MacOS:

  ```bash
  source venv/bin/activate
  ```

Your terminal prompt should now display `(venv)`.

### 3. Install Dependencies

Install the required packages specified in the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

**note:** Remember to update your virtual environment whenever you add or remove dependencies. You can do this by running `pip freeze > requirements.txt` to update the `requirements.txt` file

### 4. Adding environmental variables

Create a `.env` file in the project folder. Add the following two variables: `session` and `leaderboard_id`. `session` is the cookie stored by AoC if you authenticate in the browser (valid for a month) and `leaderboard_id` can be found in the url of the leaderboard you are trying to add.

### 5. Start the server

Start the server by running the `app.py` file. If the server has started, you can go to `localhost:5000` in your browser.
