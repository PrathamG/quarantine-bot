# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

import re
from tkinter import MULTIPLE
from typing import Text, List, Dict, Any
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction, AllSlotsReset

import html
import random
import requests
import json
from wordle import MAX_ATTEMPTS, WORDLEN, WORDLIST, validate_guess, compare

class ActionPlayWordle(Action):

    def name(self) -> Text:
        return "action_play_wordle"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        msg = ""
        count = tracker.get_slot("count")
        game_word = tracker.get_slot("game_word")
        guess_word = tracker.get_slot("guess_word")
        guess_word = guess_word.upper()

        if not game_word:
            game_word = random.choice(WORDLIST)

        if(validate_guess(guess_word, WORDLEN)):
            count += 1
            result_msg = ""
            result = compare(game_word, guess_word)
            for char in result:
                result_msg += (char + " ")
            dispatcher.utter_message(result_msg)
            if(guess_word == game_word): #correct word guessed
                dispatcher.utter_message("Congrats, {} is the correct word! You took {} tries".format(guess_word, count))
                return[SlotSet("game_word", None), SlotSet("guess_word", None), SlotSet("count", 0)]
            else: #correct word not guessed
                if count >= MAX_ATTEMPTS: #max attempts have been reached
                    dispatcher.utter_message("Game Over ☹️  ☹️. The word was {}".format(game_word))
                    return[SlotSet("game_word", None), SlotSet("guess_word", None), SlotSet("count", 0)]
                else: #max attempts have not been reached
                    dispatcher.utter_message("You have used {} attempts.".format(count))
                    return[SlotSet("game_word", game_word), SlotSet("guess_word", None), SlotSet("count", count), FollowupAction("wordle_form")]
        else:
            dispatcher.utter_message("Invalid guess, please try again!")
            return[SlotSet("game_word", game_word), SlotSet("guess_word", None), SlotSet("count", count), FollowupAction("wordle_form")]

class ActionPlayTrivia(Action):

    def name(self) -> Text:
        return "action_play_trivia"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        category_dict = {
            "gk": "9",
            "movies": "11",
            "sports": "21",
            "science": "17",
            "geography": "22"
        }
        
        score = tracker.get_slot("trivia_score")
        count = tracker.get_slot("trivia_count")
        count += 1

        if count > 1: #Not the first round, so check the last answer
            last_answer = tracker.get_slot("trivia_answer")
            correct = tracker.get_slot("trivia_correct")
            if last_answer == correct:
                score += 1
                dispatcher.utter_message("That's right!")
            else:
                dispatcher.utter_message("That's incorrect :( \nThe correct answer was {}".format(correct))
        if count >= 6: #All game rounds completed
            dispatcher.utter_message("Game Over! Your final score was {}/{}".format(score, count-1))
            return [
                SlotSet("trivia_category", None),
                SlotSet("trivia_difficulty", None),
                SlotSet("trivia_correct", None), 
                SlotSet("trivia_answer", None),
                SlotSet("trivia_incorrect_1", None), 
                SlotSet("trivia_incorrect_2", None),
                SlotSet("trivia_incorrect_3", None),
                SlotSet("trivia_count", 0),
                SlotSet("trivia_score", 0)
            ]

        # Else if game continues, obtain new question, choices, and user answer:
        amount = "1"
        type = "multiple"
        category = category_dict[tracker.get_slot("trivia_category")]
        difficulty = tracker.get_slot("trivia_difficulty")
        
        req = "https://opentdb.com/api.php?amount={}&type={}&category={}&difficulty={}".format(amount, type, category, difficulty)
        response = requests.get(req)
        response = (json.loads(response.text))["results"][0]

        question = response["question"]
        question = html.unescape(question)
        incorrect_1 = response["incorrect_answers"][0]
        incorrect_1 = html.unescape(incorrect_1)
        incorrect_2 = response["incorrect_answers"][1]
        incorrect_2 = html.unescape(incorrect_2)
        incorrect_3 = response["incorrect_answers"][2]
        incorrect_3 = html.unescape(incorrect_3)
        correct = response["correct_answer"]
        correct = html.unescape(correct)
        answers = [incorrect_1, incorrect_2, incorrect_3, correct]
        random.shuffle(answers)
        button_response=[
                  {"title": answers[0], "payload": answers[0]},
                  {"title": answers[1], "payload": answers[1]},
                  {"title": answers[2], "payload": answers[2]},
                  {"title": answers[3], "payload": answers[3]}
              ]

        dispatcher.utter_message(text=question, buttons=button_response)
        
        return [
                SlotSet("trivia_correct", correct), 
                SlotSet("trivia_answer", None), 
                SlotSet("trivia_incorrect_1", incorrect_1), 
                SlotSet("trivia_incorrect_2", incorrect_2),
                SlotSet("trivia_incorrect_3", incorrect_3),
                SlotSet("trivia_count", count),
                SlotSet("trivia_score", score),
                FollowupAction("trivia_answer_form")
            ]
        
class ActionJournal(Action):

    def name(self) -> Text:
        return "action_journal"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
     
        jrnl_type = tracker.get_slot("journal_type")
        if jrnl_type == "jrnl_gratitude":
            dispatcher.utter_message(
                '''
A gratitude journal can help us focus more on the positive aspects of our life, 
and build resilience to face the negative situations. You should try and reflect on 
3 positive things that occurred today. You should try and explore how these events came to be, and why
you are grateful they occurred.
                ''')
        elif jrnl_type == "jrnl_daily":
            dispatcher.utter_message(
                '''
A daily journal is a great way to reduce stress and stay focused. For a daily journal,
you should record the day's activities, thoughts, and emotions. You can also list any interesting events
that happened today, or new ideas you thought of.
          
                ''')
        elif jrnl_type == "jrnl_goal":
            dispatcher.utter_message(
                '''
A goal-tracking journal can help you prioritize your goals and keep track of progress. To begin with,
you should write down a SMART goal. A SMART goal needs to be Specific, Measurable, Attainable, Relevant and 
Time-bound. Next, you shoud note down the milestones on the way to this goal and by when you expect to achieve
them. Finally, you should establish a way to track your daily efforts toward this goal.
                ''')
        elif jrnl_type == "jrnl_soc":
            dispatcher.utter_message(
                '''
Stream-of-consciousness journaling can help you clear your mind and get better perspectives about a situation.
This kind of journaling has no goal or structure, you simply need to write down your raw thoughts and feelings 
directly as you experience them.
                ''')
        return [SlotSet("journal_type", None)]

class ActionGetJoke(Action):

    def name(self) -> Text:
        return "action_get_joke"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            req = "https://v2.jokeapi.dev/joke/Pun?format=txt&type=single&safe-mode"
            response = requests.get(req)
            dispatcher.utter_message(response.text)
            return []