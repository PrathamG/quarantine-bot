import typing
import itertools

def read_from_txt_file(filename):
    with open(filename, 'r') as file:
        file_list = [item[:-1] for item in file] # using [:-1] to get rid of the newline character
    return file_list

wordlist = read_from_txt_file('wordle-answers-alphabetical.txt')
WORDLIST = [each_string.upper() for each_string in wordlist]
guesslist = read_from_txt_file('wordle-allowed-guesses.txt')
guesslist = [each_string.upper() for each_string in guesslist]
GUESSLIST = list(itertools.chain(WORDLIST, guesslist))
WORDLEN = 5
MAX_ATTEMPTS = 6

def validate_guess(guess: str, wordlen: int) -> bool:
    guess = guess.upper()
    if len(guess) != wordlen:
        print("Please enter a {} letter word".format(wordlen))
        return False
    if guess not in GUESSLIST:
        print("Word not in list. Please try again")
        print(guess)
        return False
    return True

def find_all_char_positions(word: str, letter: str) -> typing.List[int]:
    positions = []
    pos = word.find(letter)
    while pos != -1:
        positions.append(pos)
        pos = word.find(letter, pos + 1)
    return positions

def compare(game_word: str, guess_word: str) -> typing.List[str]:
    result = ["◼️"] * WORDLEN
    counted_pos = set()
    for index, letter in enumerate(guess_word):
        if letter == game_word[index]:
            result[index] = "🟩"
            counted_pos.add(index)
    for index, letter in enumerate(guess_word):
        if letter in game_word and result[index] != "🟩":
            positions = find_all_char_positions(game_word, letter)
            for pos in positions:
                if pos not in counted_pos:
                    result[index] = "🟨"
                    counted_pos.add(pos)
                    break
    return result