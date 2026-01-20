# Roaster Shuffle

**Roaster Shuffle** is a lightweight web application designed to help organizers manage participants for events (like Tennis doubles) and easily shuffle them into teams.

It replaces manual spreadsheet management with a simple, interactive interface where you can track who is available ("Pool") and who is playing ("Roster"), and then automatically generate random teams.

## Features

- **Event Management**: Create multiple events (e.g., "Friday Tennis", "Sunday League").
- **Participant Management**: 
    - Register participants to a specific event.
    - **Interactive Pool & Roster**: Click a name to instantly move them between the *Pool* (managed waitlist/available) and the *Roster* (active players).
    - **HTMX Powered**: Smooth, fast interactions without full page reloads.
- **Team Shuffling**: 
    - Automatically pairs up players in the Roster into teams of 2.
    - Handles simple randomization for doubles matches.
- **Responsive Design**: Built with **Pico.css** for a clean, mobile-friendly UI that works on phones and desktops.

## Tech Stack

- **Backend**: Python 3, Flask
- **Database**: SQLite (via SQLAlchemy)
- **Frontend**: HTML5, Jinja2 Templates
- **CSS Framework**: [Pico.css](https://picocss.com/) (Classless/Minimal)
- **interactive UI**: [HTMX](https://htmx.org/) (AJAX replacement)

## Installation & Setup

1. **Clone the repository** (or download the source).

2. **Set up a Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. **Start the Server**:
   ```bash
   python roaster-shuffle.py
   ```

2. **Open in Browser**:
   Visit [http://127.0.0.1:5000](http://127.0.0.1:5000)

# Run in Docker
   
   Build the image:
   ```bash
   docker build -t roaster-shuffle .
   ```

   Run the container:
   ```bash
   docker run -p 5000:5000 roaster-shuffle
   ```
   
   *Tip: To persist the database, mount a volume:*
   ```bash
   docker run -p 5000:5000 -v $(pwd)/roaster.db:/app/roaster.db roaster-shuffle
   ```

## Running Tests

The project includes a test suite using `pytest` to ensure core functionality works as expected.

```bash
# Run all tests
pytest
```

## Usage Guide

1. **Create an Event**: on the home page, enter an event name (e.g. "Morning Practice") and click "Create".
2. **Add Participants**: Click the event name to enter the dashboard. Type a name in the "Pool" section and add them.
3. **Build the Roster**: Click on names in the **Pool** list to move them to the **Roster**.
4. **Shuffle**: Once you have enough players in the Roster, click **Shuffle Teams** to randomly assign them team numbers.
5. **Reset**: Click a name in the Roster to move them back to the Pool (this clears their team assignment).

## License

MIT License
