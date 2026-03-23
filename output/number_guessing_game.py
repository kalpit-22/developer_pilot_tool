#!/usr/bin/env python3
"""
Number Guessing Game
The computer picks a random number and the user tries to guess it.
"""

import random
import sys


def main():
    """Main game function."""
    print("Welcome to the Number Guessing Game!")
    print("I'm thinking of a number between 1 and 100.")
    
    # Generate random number
    secret_number = random.randint(1, 100)
    attempts = 0
    
    while True:
        try:
            # Get user's guess
            guess_input = input("Enter your guess (or 'quit' to exit): ").strip()
            
            if guess_input.lower() == 'quit':
                print(f"The secret number was {secret_number}. Thanks for playing!")
                sys.exit(0)
            
            guess = int(guess_input)
            attempts += 1
            
            # Check the guess
            if guess < 1 or guess > 100:
                print("Please enter a number between 1 and 100.")
                continue
                
            if guess < secret_number:
                print("Too low! Try again.")
            elif guess > secret_number:
                print("Too high! Try again.")
            else:
                print(f"Congratulations! You guessed the number {secret_number} in {attempts} attempts!")
                break
                
        except ValueError:
            print("Please enter a valid number or 'quit' to exit.")


if __name__ == "__main__":
    main()