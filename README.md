# TheMoeWay Gatekeeper Bot

📢 **New contributors [welcome](contribute.md)!**

## What is the Gatekeeper Bot?
The TheMoeWay discord server has a role system, where users can pass certain kind of quizzes to earn a role that symbolizes their skill in the Japanese language. The Gatekeeper is responsible for handling the logic behind the quizzes, so when somebody passes a quiz it assigns them a role or prevents users from grinding the quiz.

Powerful features that it provides:
- 📬 DMs users their quiz cooldowns whenever they fail a quiz.
- 👮 Creates a fair environment to earn your rank. 
- 📣 Congratulates users when they pass a quiz.

## Usage Guide

The bot needs the [Kotoba Bot](https://github.com/mistval/kotoba), which provides the feature for actual quizzes to work. The quizzes the bot is responsible for are only available on TheMoeWay, which was decided to avoid users grinding the quiz. Because of this the bot works only on TheMoeWay and can only be developed there.
Below is a more detailed explanation:

There are 5 quiz decks for each rank.

### Student (lowest): 

`k!quiz jpdb1k(1-300) 25 hardcore nd mmq=10 dauq=1 font=5 color=#f173ff size=100`

### Trainee: 

`k!quiz jpdb1k 50 hardcore nd mmq=10 dauq=1 font=5 color=#f173ff size=100`

### Debut Idol:

`k!quiz jpdb2_5k+jpdb5k 50 hardcore nd mmq=10 dauq=1 font=5 color=#f173ff size=100 effect=antiocr`

### Major Idol:

` k!quiz jpdb5k+jpdb10k 50 hardcore nd mmq=10 dauq=1 font=5 color=#f173ff size=100 effect=antiocr` 

### Prima Idol:

`k!quiz gn2 nd 20 mmq=4`

Followed by: 

`k!quiz jpdb10k+jpdb15k 50 hardcore nd mmq=10 dauq=1 font=5 color=#f173ff size=100 effect=antiocr` 

### Divine Idol:

`k!quiz gn1 nd 20 mmq=4 `

Followed by: 

`k!quiz jpdb15k+jpdb20k 50 hardcore nd mmq=10 dauq=1 font=5 color=#f173ff size=100 effect=antiocr` 

### Eternal Idol (Highest):

`k!quiz gn1 nd 20 mmq=4`

Followed by: 

`k!quiz jpdb20k+jpdb25k 50 hardcore nd mmq=10 dauq=1 font=5 color=#f173ff size=100 effect=antiocr` 

Each of the quiz decks are available only on TheMoeWay. For example when a user wants to pass the Prima Idol quiz, they need to pass two quizzes. 
One is the grammer part:

`k!quiz gn2 nd 20 mmq=4`

One is the vocab part:

`k!quiz jpdb10k+jpdb15k 50 hardcore nd mmq=10 dauq=1 font=5 color=#f173ff size=100 effect=antiocr` 

The same goes for Divine and Eternal Idol. If a user fails a quiz they cannot retake it until Sunday 00:00 UTC+00:00.
The Student quiz (the lowest) has no fail penalty.
