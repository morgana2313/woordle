#! /usr/bin/env python3

from collections import namedtuple
import random
import dutch_words

class Attempt:
    """
    Stores an attempt.
    parameters:
        word:           attempt to process
        CorrectWord:    word to match against

    """
    def __init__(self, word, CorrectWord, lenWord=6):
        self.word = word
        self.compare(CorrectWord)
        self.won = (word == CorrectWord)

    def compare(self, CorrectWord):
        """
        Scores a word:
         + letter at correct position
         * letter at wrong position
         - letter not in word
        """
        CorrectWord = list(CorrectWord)
        comparison = ['_'] * len(CorrectWord)

        # first find letters at right position
        for i in range(len(self.word)):
            if word[i] == CorrectWord[i]:
                comparison[i] = '+'
                # remove letter from CorrectWord to avoid duplications with * and -
                CorrectWord[i] = '_'

        # Now find other letters.
        for i in range(len(self.word)):
            if comparison[i] != '+':
                letter = self.word[i]
                c = '-' if letter not in CorrectWord else '*'
                comparison[i] = c
        self.comparison = ''.join(comparison)

    def __str__(self):
        return f'Attempt({self.word} {self.comparison} {self.won})'

class Game:
    """
    Administers a game
    parameters:
        CorrectWord:    word to match against
        maxAttemps:     maximum guesses (default: 6)
        lenWord:        length of words (default: 6)

    """
    def __init__(self, CorrectWord, maxAttemps=6, lenWord=6):
        self.CorrectWord = CorrectWord
        self.maxAttemps = maxAttemps
        self.attempts = []
        self.lenWord = lenWord

    def play(self, word):
        # Play a word.
        if len(word) != self.lenWord:
            raise ValueError(f"{word} is not {lenWord} letters long.")
        if len(self.attempts) >= self.maxAttemps:
            raise RuntimeError(f"{self.maxAttemps} maxAttemps reached.")
        attempt = Attempt(word, self.CorrectWord, lenWord=self.lenWord)
        self.attempts.append(attempt)
        return attempt

    def __str__(self):
        # represents a game
        result = [f'beurt {len(self.attempts)} ']
        for i in range(self.maxAttemps):
            if i < len(self.attempts):
                attempt = self.attempts[i]
                result += [attempt.word, attempt.comparison]
            else:
                result += [' ' * self.lenWord]
        result = [f'|{r}|' if i > 0 else r for i,r in enumerate(result)]
        return '\n'.join(result) + '\n'


def locate(str, *letters):
    # find indexes of letters in str
    # https://stackoverflow.com/a/6294205
    return [i for i, l in enumerate(str) if l in letters]

def partition(alist, indices):
    # splits a list into chunks around indices
    # https://stackoverflow.com/a/1198876
    startIndices = [0] + [ (i+1) for i in indices if i+1 < len(alist)] # skip index position itself.
    endIndices = indices + [None]
    return [alist[i:j] for i, j in zip(startIndices, endIndices)]

class Guess:
    """
    Maintains list of possible guesses and gives best guess.
    parameters:
        wordlist: list of all words with same length
    """
    def __init__(self, wordlist):
        self.wordlist = wordlist

    def bestGuess(self, attempt):
        # returns best guess based on letter frequency in possible words.
        letterFreq = {}
        # how many times occours each letter?
        for w in self.wordlist:
            for letter in w:
                if w not in letterFreq: letterFreq[w] = 1
                else: letterFreq[w] += 1

        maxScore = 0
        bestGuess = [self.wordlist[0]]
        for w in self.wordlist:
            score = 0
            # how many times do letters for this word occour in possible words?
            for letter in w:
                score += letterFreq[w]
            if score > maxScore:
                maxScore = score
                bestGuess = [w]
            elif score == maxScore:
                bestGuess.append(w)
        # return a guess with the best score
        return bestGuess[random.randrange(len(bestGuess))]

    def filter(self, attempt):
        # Filter out words that don't match the attempt
        RightPositions = self.filterPlus(attempt)
        self.filterStarMinus(attempt, RightPositions)

    def filterPlus(self, attempt):
        # Filter out wordt that don't match the plusses in the comparison.
        # And keep a list of letters at the right position (and their positions)
        RightPositions = {}
        for idx in locate(attempt.comparison, '+'):
            # Only keep words with letter at this position
            filterFn = lambda w: w[idx] == attempt.word[idx]
            self.wordlist = list(filter(filterFn, self.wordlist))
            letter = attempt.word[idx]
            # Dict with letters at right position
            if letter not in RightPositions:
                RightPositions[letter] = []
            RightPositions[letter].append(idx)
        return RightPositions

    def filterStarMinus(self, attempt, RightPositions):
        # Filter out wordt that don't match the plusses in the comparison.
        for idx in locate(attempt.comparison, '*', '-'):
            letter = attempt.word[idx]
            c = attempt.comparison[idx]
            invertIfMin = lambda b: b if c == '*' else not(b)
            letterInW = lambda w: letter in w

            if letter not in RightPositions:
                filterFn = lambda w: w[idx] != letter and invertIfMin(letterInW(w))
            else:
                def filterFn(w):
                    if w[idx] == letter: # avoid words with letter at this position
                        return False
                    # '-': cannot filter all words with this letter coz letter also in RightPositions,
                    if c == '-': return True
                    # split string in parts around the RightPositions
                    parts = partition(w, RightPositions[letter])
                    # any part that contains the letter ?
                    return any (letterInW(p) for p in parts)
            self.wordlist = list(filter(filterFn, self.wordlist))

def testfilterStarMinus():
    Attempt=namedtuple('Attempt', ('word', 'comparison'))
    words = ['caa', 'aaa', 'abb', 'aba', 'aca', 'acc', 'aac']
    guess = Guess(words)
    attempt = Attempt('aba', '+-*')
    guess.filter(attempt)
    print (f"{words} + {attempt} => {guess.wordlist}")
#testfilterStarMinus();exit(0)

random.seed(0)
lenWord = 6
words = sorted(w.lower() for w in filter(lambda w: len(w)== lenWord, dutch_words.get_ranked()) )
CorrectWord = words[random.randrange(len(words))]
print(f"len:{len(words)} {CorrectWord=} ", )

game = Game(CorrectWord, lenWord=lenWord, maxAttemps=10)
guess= Guess(words)

attempt = None
while True:
    word = guess.bestGuess(attempt)
    attempt = game.play(word)
    if attempt.won:
        print (f"Gefeliciteerd je hebt gewonnen in {len(game.attempts)} beurten: {word} == {CorrectWord}")
        break
    else:
        guess.filter(attempt)
    print(game)