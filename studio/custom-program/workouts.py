# -*- coding: utf-8 -*-
"""Custom Program pe Payhip: toate antrenamentele (o postare video pentru fiecare), construite DOAR din clipurile pe care le avem.
Numele postărilor se potrivesc cu ce scrie chestionarul („Day 1: Lower body and core (gym)”), ca membrul să-și găsească ziua.
Seturile scrise sunt pentru Intermediate; textul postării spune cum se adaptează la Beginner și Advanced.
Clipurile: clips/preview/<id>.mp4 (540×960, din previzualizare) sau out/<id>.mp4 (1080×1920, filmate pe 10 nov)."""

NAMES = {
    "incalzire-coarda": "Jump rope", "incalzire-cercuri-brate": "Arm circles", "incalzire-leg-swings": "Leg swings",
    "incalzire-mars-pe-loc": "March in place", "incalzire-step-jack": "Step jacks", "incalzire-jumping-jacks": "Jumping jacks",
    "incalzire-inchworm": "Inchworm", "mobilitate-cat-cow-v2": "Cat-cow", "mobilitate-worlds-greatest-stretch": "World's greatest stretch",
    "mobilitate-flexori-sold": "Kneeling hip flexor stretch", "mobilitate-childs-pose": "Child's pose reach", "mobilitate-cobra": "Cobra stretch",
    "mobilitate-extensie-toracica": "Thoracic extension on a bench", "mobilitate-rasucire-sezut": "Seated spinal twist",
    "picioare-goblet-a": "Goblet squat", "picioare-fandare-inapoi": "Reverse lunge", "picioare-split-a": "Split squat",
    "picioare-varfuri": "Calf raises", "picioare-hip-thrust": "Hip thrust", "picioare-rdl": "Romanian deadlift",
    "spate-lat-pulldown": "Lat pulldown", "spate-face-pull": "Face pull", "spate-ramat-gantera": "One-arm dumbbell row",
    "spate-fluturari-inverse": "Reverse fly", "impins-flotare-inclinata": "Incline push-up", "impins-flotare": "Push-up",
    "impins-umeri-gantere": "Seated shoulder press", "umeri-ridicari-laterale": "Lateral raise",
    "core-plank": "Plank", "core-bird-dog": "Bird dog", "core-plank-lateral": "Side plank", "core-dead-bug": "Dead bug",
    "core-hollow-hold": "Hollow hold", "gat-chin-tucks-sezut": "Chin tucks", "incheieturi-palma-sus": "Wrist stretch, palm up",
    "cardio-banda": "Incline walk", "cardio-skaters": "Skaters",
}
# varianta de acasă, scrisă sub nume (fără clip separat)
HOME_NAMES = {
    "picioare-goblet-a": "Squat (dumbbell or hands at chest)", "picioare-rdl": "Romanian deadlift (dumbbells or a backpack)",
    "picioare-hip-thrust": "Hip thrust on the sofa, or glute bridge", "spate-ramat-gantera": "One-arm row (dumbbell or water bottle)",
    "impins-umeri-gantere": "Shoulder press (light dumbbells)", "umeri-ridicari-laterale": "Lateral raise (light dumbbells or bottles)",
    "spate-fluturari-inverse": "Reverse fly (light dumbbells or bottles)", "mobilitate-extensie-toracica": "Thoracic extension on the sofa",
    "picioare-split-a": "Split squat", "picioare-fandare-inapoi": "Reverse lunge",
}

def W(title, tags, warm, main, cool, home=False, note=""):
    return dict(title=title, tags=tags, warm=warm, main=main, cool=cool, home=home, note=note)

# fiecare exercițiu: (id, „seturi”)
GYM = [
    W("Full body A (gym)", ["Get Strong", "Shape Up", "Gym"],
      [("incalzire-coarda", "2 min"), ("mobilitate-worlds-greatest-stretch", "5 / side")],
      [("picioare-goblet-a", "3 × 8–12"), ("spate-lat-pulldown", "3 × 8–12"), ("picioare-rdl", "3 × 8–12"), ("impins-umeri-gantere", "3 × 8–12"), ("core-dead-bug", "3 × 8 / side")],
      [("mobilitate-childs-pose", "30 s")]),
    W("Full body B (gym)", ["Get Strong", "Shape Up", "Gym"],
      [("incalzire-mars-pe-loc", "1 min"), ("incalzire-leg-swings", "10 / side"), ("incalzire-cercuri-brate", "30 s")],
      [("picioare-split-a", "3 × 8 / side"), ("spate-ramat-gantera", "3 × 10 / side"), ("picioare-hip-thrust", "3 × 10"), ("impins-flotare-inclinata", "3 × 8–12"), ("core-plank-lateral", "3 × 20 s / side")],
      [("mobilitate-flexori-sold", "30 s / side")]),
    W("Lower body (gym)", ["Get Strong", "Shape Up", "Gym"],
      [("incalzire-coarda", "2 min"), ("incalzire-leg-swings", "10 / side"), ("mobilitate-worlds-greatest-stretch", "5 / side")],
      [("picioare-goblet-a", "3 × 8–12"), ("picioare-rdl", "3 × 8–12"), ("picioare-fandare-inapoi", "3 × 8 / side"), ("picioare-hip-thrust", "3 × 10"), ("picioare-varfuri", "3 × 15")],
      [("mobilitate-flexori-sold", "30 s / side"), ("mobilitate-childs-pose", "30 s")],
      note="Also for: Legs · Legs and glutes"),
    W("Lower body and core (gym)", ["Get Strong", "Shape Up", "Gym"],
      [("incalzire-mars-pe-loc", "1 min"), ("mobilitate-worlds-greatest-stretch", "5 / side")],
      [("picioare-hip-thrust", "4 × 10"), ("picioare-rdl", "3 × 10"), ("picioare-split-a", "3 × 8 / side"), ("core-dead-bug", "3 × 8 / side"), ("core-plank", "3 × 30 s")],
      [("mobilitate-flexori-sold", "30 s / side")],
      note="Also for: Glutes and core · Glutes and hamstrings · Lower body + core"),
    W("Upper body and back (gym)", ["Get Strong", "Shape Up", "Gym"],
      [("incalzire-cercuri-brate", "30 s"), ("mobilitate-cat-cow-v2", "8 slow"), ("mobilitate-extensie-toracica", "6 slow")],
      [("spate-lat-pulldown", "3 × 8–12"), ("impins-umeri-gantere", "3 × 8–12"), ("spate-ramat-gantera", "3 × 10 / side"), ("impins-flotare-inclinata", "3 × 8–12"), ("spate-face-pull", "3 × 15"), ("umeri-ridicari-laterale", "2 × 12–15")],
      [("mobilitate-childs-pose", "30 s")],
      note="Also for: Upper body and core (finish with 2 rounds of the Plank)"),
    W("Shoulders and posture (gym)", ["Get Strong", "Shape Up", "Desk Reset", "Gym"],
      [("incalzire-cercuri-brate", "30 s"), ("gat-chin-tucks-sezut", "10 slow"), ("mobilitate-extensie-toracica", "6 slow")],
      [("spate-face-pull", "3 × 15"), ("spate-fluturari-inverse", "3 × 12"), ("spate-lat-pulldown", "3 × 10"), ("umeri-ridicari-laterale", "3 × 12"), ("core-bird-dog", "3 × 8 / side"), ("core-plank-lateral", "2 × 20 s / side")],
      [("mobilitate-cobra", "20 s"), ("mobilitate-childs-pose", "30 s")],
      note="Also for: Upper body and posture · Desk Reset: Upper back and core strength"),
    W("Core and full body (gym)", ["Get Strong", "Shape Up", "Gym"],
      [("incalzire-jumping-jacks", "1 min"), ("incalzire-inchworm", "5 slow")],
      [("picioare-goblet-a", "3 × 10"), ("impins-flotare", "3 × 6–10"), ("spate-ramat-gantera", "3 × 10 / side"), ("core-hollow-hold", "3 × 15 s"), ("core-dead-bug", "3 × 8 / side"), ("core-bird-dog", "2 × 8 / side")],
      [("mobilitate-cobra", "20 s")],
      note="Also for: Full body + core finisher · Desk Reset: Upper back, glutes and core"),
]

HOME = [
    W("Full body A (home)", ["Get Strong", "Shape Up", "Home"],
      [("incalzire-mars-pe-loc", "1 min"), ("incalzire-step-jack", "30 s"), ("incalzire-inchworm", "5 slow")],
      [("picioare-goblet-a", "3 × 12"), ("impins-flotare-inclinata", "3 × 10"), ("picioare-fandare-inapoi", "3 × 8 / side"), ("spate-ramat-gantera", "3 × 10 / side"), ("core-dead-bug", "3 × 8 / side")],
      [("mobilitate-childs-pose", "30 s")], home=True),
    W("Full body B (home)", ["Get Strong", "Shape Up", "Home"],
      [("incalzire-jumping-jacks", "1 min"), ("mobilitate-worlds-greatest-stretch", "5 / side")],
      [("picioare-split-a", "3 × 8 / side"), ("impins-flotare", "3 × 6–10"), ("picioare-hip-thrust", "3 × 12"), ("core-bird-dog", "3 × 8 / side"), ("core-plank", "3 × 30 s")],
      [("mobilitate-cobra", "20 s")], home=True),
    W("Lower body (home)", ["Get Strong", "Shape Up", "Home"],
      [("incalzire-mars-pe-loc", "1 min"), ("incalzire-leg-swings", "10 / side"), ("mobilitate-worlds-greatest-stretch", "5 / side")],
      [("picioare-goblet-a", "3 × 12–15"), ("picioare-fandare-inapoi", "3 × 10 / side"), ("picioare-rdl", "3 × 12"), ("picioare-hip-thrust", "3 × 15"), ("picioare-varfuri", "3 × 20")],
      [("mobilitate-flexori-sold", "30 s / side")], home=True, note="Also for: Legs · Legs and glutes"),
    W("Lower body and core (home)", ["Get Strong", "Shape Up", "Home"],
      [("incalzire-step-jack", "1 min"), ("mobilitate-worlds-greatest-stretch", "5 / side")],
      [("picioare-hip-thrust", "4 × 15"), ("picioare-split-a", "3 × 10 / side"), ("picioare-rdl", "3 × 12"), ("core-dead-bug", "3 × 8 / side"), ("core-plank-lateral", "3 × 20 s / side"), ("core-hollow-hold", "2 × 15 s")],
      [("mobilitate-flexori-sold", "30 s / side")], home=True, note="Also for: Glutes and core · Glutes and hamstrings · Lower body + core"),
    W("Upper body and back (home)", ["Get Strong", "Shape Up", "Home"],
      [("incalzire-cercuri-brate", "30 s"), ("mobilitate-cat-cow-v2", "8 slow")],
      [("impins-flotare-inclinata", "3 × 10"), ("spate-ramat-gantera", "3 × 12 / side"), ("impins-umeri-gantere", "3 × 10"), ("umeri-ridicari-laterale", "3 × 12"), ("spate-fluturari-inverse", "3 × 12"), ("core-plank", "3 × 30 s")],
      [("mobilitate-childs-pose", "30 s")], home=True, note="Also for: Upper body and core"),
    W("Shoulders and posture (home)", ["Get Strong", "Shape Up", "Desk Reset", "Home"],
      [("incalzire-cercuri-brate", "30 s"), ("gat-chin-tucks-sezut", "10 slow"), ("mobilitate-cat-cow-v2", "8 slow")],
      [("spate-fluturari-inverse", "3 × 12"), ("umeri-ridicari-laterale", "3 × 12"), ("impins-flotare-inclinata", "3 × 10"), ("core-bird-dog", "3 × 8 / side"), ("core-plank-lateral", "2 × 20 s / side")],
      [("mobilitate-extensie-toracica", "6 slow"), ("mobilitate-cobra", "20 s")], home=True,
      note="Also for: Upper body and posture · Desk Reset: Upper back and core strength"),
    W("Core and full body (home)", ["Get Strong", "Shape Up", "Home"],
      [("incalzire-jumping-jacks", "1 min"), ("incalzire-inchworm", "5 slow")],
      [("picioare-goblet-a", "3 × 12"), ("impins-flotare", "3 × 6–10"), ("spate-ramat-gantera", "3 × 10 / side"), ("core-hollow-hold", "3 × 15 s"), ("core-dead-bug", "3 × 8 / side"), ("core-plank-lateral", "2 × 20 s / side")],
      [("mobilitate-cobra", "20 s")], home=True, note="Also for: Full body + core finisher · Desk Reset: Upper back, glutes and core"),
]

OTHER = [
    W("Unstiff A: full-body mobility", ["Unstiff", "Desk Reset", "Home"],
      [("incalzire-mars-pe-loc", "1 min"), ("incalzire-cercuri-brate", "30 s"), ("incalzire-leg-swings", "10 / side")],
      [("mobilitate-cat-cow-v2", "8 slow"), ("mobilitate-worlds-greatest-stretch", "5 / side"), ("mobilitate-flexori-sold", "40 s / side"), ("mobilitate-rasucire-sezut", "30 s / side"), ("mobilitate-extensie-toracica", "8 slow"), ("core-bird-dog", "2 × 6 / side")],
      [("mobilitate-childs-pose", "45 s"), ("mobilitate-cobra", "20 s")], home=True,
      note="Go round the main part 2 times for 20 minutes, 3 times for 30. Also for: Desk Reset: Unstiff: full body"),
    W("Unstiff B: neck, shoulders and hips", ["Unstiff", "Desk Reset", "Home"],
      [("incalzire-cercuri-brate", "30 s"), ("gat-chin-tucks-sezut", "10 slow")],
      [("mobilitate-extensie-toracica", "8 slow"), ("mobilitate-cat-cow-v2", "8 slow"), ("incheieturi-palma-sus", "20 s / side"), ("mobilitate-worlds-greatest-stretch", "5 / side"), ("mobilitate-flexori-sold", "40 s / side"), ("mobilitate-rasucire-sezut", "30 s / side")],
      [("mobilitate-childs-pose", "45 s")], home=True,
      note="Go round the main part 2 times for 20 minutes, 3 times for 30. Also for: Desk Reset: Unstiff: neck, shoulders and hips"),
    W("Express 10: gym", ["Express", "Get Strong", "Shape Up", "Gym"],
      [("incalzire-coarda", "1 min")],
      [("picioare-goblet-a", "10"), ("spate-lat-pulldown", "10"), ("picioare-hip-thrust", "10"), ("impins-umeri-gantere", "10")],
      [], note="A circuit: one set of each move, then start again. 3 rounds, as little rest as you need."),
    W("Express 10: home", ["Express", "Get Strong", "Shape Up", "Home"],
      [("incalzire-mars-pe-loc", "1 min")],
      [("picioare-goblet-a", "12"), ("impins-flotare-inclinata", "10"), ("picioare-fandare-inapoi", "8 / side"), ("core-plank", "30 s")],
      [], home=True, note="A circuit: one set of each move, then start again. 3 rounds, as little rest as you need."),
    W("Cardio: jump rope intervals", ["Cardio", "Shape Up", "Home"],
      [("incalzire-mars-pe-loc", "1 min")], [("incalzire-coarda", "30 s on, 30 s off × 10"), ("incalzire-jumping-jacks", "between rounds, if you want")],
      [("picioare-varfuri", "slow, 15")], home=True, note="15 to 20 minutes in total. No jumping for you? Use the Cardio: no-jump post."),
    W("Cardio: incline walk", ["Cardio", "Shape Up", "Gym"],
      [], [("cardio-banda", "15–20 min, incline 6–10, a pace you can talk at")], [("mobilitate-flexori-sold", "30 s / side")]),
    W("Cardio: no-jump (home)", ["Cardio", "Shape Up", "Home"],
      [], [("incalzire-mars-pe-loc", "1 min fast"), ("incalzire-step-jack", "1 min"), ("picioare-fandare-inapoi", "30 s, alternating"), ("incalzire-cercuri-brate", "30 s")],
      [], home=True, note="Repeat the 4 moves for 15 to 20 minutes. Knee-friendly, no jumping."),
]

RESETS = [
    W("5-minute reset: neck", ["Resets"], [], [("gat-chin-tucks-sezut", "10 slow"), ("mobilitate-extensie-toracica", "6 slow"), ("mobilitate-cat-cow-v2", "8 slow"), ("mobilitate-childs-pose", "45 s")], [], home=True),
    W("5-minute reset: shoulders and upper back", ["Resets"], [], [("incalzire-cercuri-brate", "30 s"), ("mobilitate-extensie-toracica", "8 slow"), ("mobilitate-cat-cow-v2", "8 slow"), ("mobilitate-childs-pose", "45 s")], [], home=True),
    W("5-minute reset: lower back", ["Resets"], [], [("mobilitate-cat-cow-v2", "8 slow"), ("mobilitate-childs-pose", "45 s"), ("mobilitate-rasucire-sezut", "30 s / side"), ("core-bird-dog", "6 / side")], [], home=True),
    W("5-minute reset: hips", ["Resets"], [], [("incalzire-leg-swings", "10 / side"), ("mobilitate-flexori-sold", "40 s / side"), ("mobilitate-worlds-greatest-stretch", "4 / side"), ("mobilitate-childs-pose", "45 s")], [], home=True),
    W("5-minute reset: wrists and elbows", ["Resets"], [], [("incalzire-cercuri-brate", "30 s"), ("incheieturi-palma-sus", "30 s / side"), ("mobilitate-cat-cow-v2", "8 slow, hands on a chair"), ("mobilitate-childs-pose", "45 s")], [], home=True),
    W("5-minute reset: knee-friendly hips and ankles", ["Resets"], [], [("incalzire-leg-swings", "10 / side"), ("picioare-varfuri", "2 × 15, slow"), ("mobilitate-flexori-sold", "40 s / side"), ("picioare-hip-thrust", "2 × 12, or glute bridge")], [], home=True),
]

ALL = GYM + HOME + OTHER + RESETS
