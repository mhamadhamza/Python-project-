import json
import os
import random
import textwrap

# ------------- Question Bank -------------
# You can add more questions or load from questions.json (see bottom).
QUESTIONS = [
    {
        "q": "Which language runs in a web browser?",
        "choices": ["Java", "C", "Python", "JavaScript"],
        "answer": "D"  # (A,B,C,D)
    },
    {
        "q": "What does CPU stand for?",
        "choices": ["Central Process Unit", "Central Processing Unit", "Computer Personal Unit", "Central Processor Utility"],
        "answer": "B"
    },
    {
        "q": "Which data structure uses FIFO?",
        "choices": ["Stack", "Queue", "Tree", "Graph"],
        "answer": "B"
    },
    {
        "q": "What is the value of 2**3?",
        "choices": ["6", "8", "9", "12"],
        "answer": "B"
    },
    {
        "q": "HTTP status 404 means:",
        "choices": ["OK", "Forbidden", "Not Found", "Server Error"],
        "answer": "C"
    },
]

HIGHSCORE_FILE = "quiz_highscore.json"

# ------------- Helpers -------------
def load_highscore():
    if not os.path.exists(HIGHSCORE_FILE):
        return {"name": None, "score": 0, "total": 0}
    try:
        with open(HIGHSCORE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"name": None, "score": 0, "total": 0}

def save_highscore(name, score, total):
    hs = load_highscore()
    if score > hs.get("score", 0) or total != hs.get("total", 0):
        with open(HIGHSCORE_FILE, "w", encoding="utf-8") as f:
            json.dump({"name": name, "score": score, "total": total}, f)

def print_banner(title="QUIZ GAME"):
    print("=" * 50)
    print(title.center(50))
    print("=" * 50)

def ask_yes_no(prompt):
    while True:
        ans = input(prompt + " (y/n): ").strip().lower()
        if ans in ("y", "yes"): return True
        if ans in ("n", "no"): return False
        print("Please type y or n.")

def validate_choice(prompt, valid=("A","B","C","D","L")):
    while True:
        ans = input(prompt).strip().upper()
        if ans in valid:
            return ans
        print(f"Enter one of {', '.join(valid)}.")

def fifty_fifty(choices, correct_letter):
    """Return set of letters to keep (correct + one random wrong)."""
    letters = ["A","B","C","D"]
    wrongs = [l for l in letters if l != correct_letter]
    keep_wrong = random.choice(wrongs)
    return {correct_letter, keep_wrong}

def percentage(score, total):
    return round((score / total) * 100, 2) if total else 0.0

# ------------- Game Core -------------
def play_quiz(player_name, question_set):
    score = 0
    total = len(question_set)
    lifeline_used = False

    # Shuffle questions and also shuffle each question's choices
    random.shuffle(question_set)
    for idx, q in enumerate(question_set, start=1):
        # Map choices to letters after shuffling
        letters = ["A","B","C","D"]
        paired = list(zip(letters, q["choices"]))
        random.shuffle(paired)

        # Find new correct letter after shuffle
        original_correct_text = q["choices"][["A","B","C","D"].index(q["answer"])]
        new_correct_letter = next(L for L, txt in paired if txt == original_correct_text)

        print()
        print("-" * 50)
        print(f"Q{idx}.")
        print(textwrap.fill(q["q"], width=72))
        for L, txt in paired:
            print(f"  {L}) {txt}")

        valid = ["A","B","C","D"]
        if not lifeline_used:
            valid.append("L")

        choice = validate_choice(
            "Your answer (A/B/C/D" + ("/L for 50:50" if not lifeline_used else "") + "): ",
            valid=tuple(valid)
        )

        # Lifeline 50:50
        if choice == "L":
            lifeline_used = True
            keep = fifty_fifty([t for _, t in paired], new_correct_letter)
            # Reprint filtered options
            print("\nUsing 50:50 lifeline — two options remain:")
            for L, txt in paired:
                if L in keep:
                    print(f"  {L}) {txt}")
            choice = validate_choice("Your answer (A/B/C/D): ", valid=("A","B","C","D"))

        if choice == new_correct_letter:
            print("✅ Correct!")
            score += 1
        else:
            correct_text = next(txt for L, txt in paired if L == new_correct_letter)
            print(f"❌ Wrong. Correct answer: {new_correct_letter}) {correct_text}")

    print("\n" + "=" * 50)
    print(f"🎉 Finished, {player_name}!")
    print(f"Score: {score}/{total}  ({percentage(score,total)}%)")
    print("=" * 50)
    return score, total

def main():
    print_banner()
    hs = load_highscore()
    if hs["name"] is not None:
        print(f"🏆 Current High Score: {hs['score']}/{hs['total']} by {hs['name']}")
        print("-" * 50)

    name = input("Enter your name: ").strip() or "Player"

    # Optional: load external questions if questions.json exists
    if os.path.exists("questions.json"):
        try:
            with open("questions.json", "r", encoding="utf-8") as f:
                external = json.load(f)
            # Expect list of {q, choices[4], answer:"A-D"}
            if isinstance(external, list) and external:
                print("\nLoaded custom questions from questions.json ✅")
                question_set = external
            else:
                question_set = QUESTIONS
        except Exception:
            question_set = QUESTIONS
    else:
        question_set = QUESTIONS

    score, total = play_quiz(name, question_set)
    # Save high score if better
    save_highscore(name, score, total)

    if ask_yes_no("Do you want to play again?"):
        print("\nRestarting...\n")
        main()
    else:
        print("\nThanks for playing! 👋")

if __name__ == "__main__":
    main()
