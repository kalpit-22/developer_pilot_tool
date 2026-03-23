#!/usr/bin/env python3
"""A simple number guessing game."""

import random
import sys


def main():
    """Run the main game loop."""
    print("Welcome to the Number Guessing Game!")
    print("I'm thinking of a number between 1 and 100.")
    
    # Generate random number
    secret_number = random.randint(1, 100)
    attempts = 0
    
    while True:
        try:
            # Get user input
            guess_input = input("Enter your guess (or 'quit' to exit): ").strip()
            
            if guess_input.lower() == 'quit':
                print(f"Thanks for playing! The number was {secret_number}.")
                break
            
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
        except KeyboardInterrupt:
            print(f"\nGame interrupted. The number was {secret_number}.")
            break


if __name__ == "__main__":
    main()