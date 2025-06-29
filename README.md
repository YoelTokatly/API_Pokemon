# API Pokemon Project

A simple Python application that interacts with the PokeAPI to randomly draw Pokemon cards and save their data to a local SQLite database.

The project includes automated AWS deployment capabilities.

## Project Overview

This project consists of two main components:

1. **Pokemon Game** - A Python application that:
   - Connects to the [PokeAPI](https://pokeapi.co/)
   - Randomly draws Pokemon cards
   - Saves Pokemon data to a local SQLite database
   - Provides a simple command-line interface

2. **AWS Deployment** - Automated AWS infrastructure deployment that:
   - Creates an EC2 instance with all required dependencies
   - Sets up a secure SSH connection
   - Clones the repository to the instance
   - Configures the necessary environment

## Prerequisites

- Python 3.x
- pip (Python package manager)
- AWS account with appropriate permissions
- AWS CLI configured with your credentials
- Git

## Installation

### Local Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/YoelTokatly/API_Pokemon.git
   cd API_Pokemon
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
   ```

### AWS Deployment

The project includes an automated deployment script that will set up an EC2 instance with all necessary dependencies.

1. Run the deployment script:
   ```bash
   python deploy.py
   ```

2. The script will:
   - Create a key pair for SSH access (if it doesn't exist)
   - Create a security group with SSH access
   - Launch an EC2 instance
   - Install all dependencies
   - Clone the repository to the instance
   - Set up the environment

3. Once the deployment is complete, you can SSH into the instance using:
   ```bash
   ssh -i pokemon-key.pem ec2-user@<instance-public-dns>
   ```
   (The actual public DNS will be provided in the script output)

## Usage

1. Run the application:
   ```bash
   python main.py
   ```

2. When prompted, type 'y' to draw a Pokemon card.

3. The program will:
   - Connect to the PokeAPI
   - Randomly select a Pokemon
   - Check if it already exists in the local database
   - If new, display information about the Pokemon and save it to the database

## Project Structure

- `main.py` - The main Pokemon game application
- `deploy.py` - AWS deployment script
- `pokemon2.db` - SQLite database file (created on first run)
- `pokemon-key.pem` - AWS EC2 key pair file (created by deploy.py)

## Database Schema

The application uses a simple SQLite database with the following schema:

```sql
CREATE TABLE IF NOT EXISTS pokemons (
    id INTEGER PRIMARY KEY,
    name TEXT,
    height INTEGER,
    weight INTEGER,
    base_experience INTEGER,
    pokemon_order INTEGER
)
```

## Security Notes

- The `pokemon-key.pem` file contains a private key for SSH access to your EC2 instance.
- Keep this file secure and do not share it.
- The deployment script sets appropriate permissions (400) on this file.

