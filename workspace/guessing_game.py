import random
import sys

def main():
    print("Welcome to the Number Guessing Game!")
    print("I'm thinking of a number between 1 and 100.")
    
    secret_number = random.randint(1, 100)
    attempts = 0
    
    while True:
        try:
            guess_input = input("Enter your guess (or 'quit' to exit): ")
            
            if guess_input.lower() == 'quit':
                print(f"Thanks for playing! The number was {secret_number}.")
                break
            
            guess = int(guess_input)
            attempts += 1
            
            if guess < secret_number:
                print("Too low! Try again.")
            elif guess > secret_number:
                print("Too high! Try again.")
            else:
                print(f"Congratulations! You guessed the number {secret_number} in {attempts} attempts!")
                break
                
        except ValueError:
            print("Please enter a valid number or 'quit'.")
        except EOFError:
            print("\nGame ended. Thanks for playing!")
            sys.exit(0)

if __name__ == "__main__":
    main()