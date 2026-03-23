#!/usr/bin/env python3
"""
Number Guessing Game
The computer picks a random number and the user tries to guess it.
"""

import random
import sys


def main():
    # Game settings
    min_number = 1
    max_number = 100
    max_attempts = 10
    
    # Generate random number
    secret_number = random.randint(min_number, max_number)
    
    print(f"Welcome to the Number Guessing Game!")
    print(f"I'm thinking of a number between {min_number} and {max_number}.")
    print(f"You have {max_attempts} attempts to guess it.")
    print()
    
    attempts = 0
    
    while attempts < max_attempts:
        attempts += 1
        attempts_left = max_attempts - attempts + 1
        
        try:
            guess = int(input(f"Attempt {attempts}/{max_attempts} (left: {attempts_left}): Enter your guess: "))
        except ValueError:
            print("Please enter a valid number.")
            attempts -= 1  # Don't count invalid attempts
            continue
        
        if guess < min_number or guess > max_number:
            print(f"Please enter a number between {min_number} and {max_number}.")
            attempts -= 1  # Don't count out-of-range attempts
            continue
        
        if guess == secret_number:
            print(f"Congratulations! You guessed the number {secret_number} in {attempts} attempts!")
            break
        elif guess < secret_number:
            print("Too low! Try a higher number.")
        else:
            print("Too high! Try a lower number.")
        
        print()
    
    if attempts >= max_attempts and guess != secret_number:
        print(f"Sorry, you've used all {max_attempts} attempts.")
        print(f"The secret number was {secret_number}.")
        print("Better luck next time!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGame interrupted. Thanks for playing!")
        sys.exit(0)