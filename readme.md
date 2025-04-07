Hi,

Thanks for taking the time to check my github. I'm very proud of this project and hope it
accurately demonstrates my skills as a developer.

Best,
Alec

# Axis vs Allies

## Installation

install Node 23
install Docker

## Run

run with
`cd ui`
`npm install`
`npm run dev`

## To Do

-   combat
-   territory capture
-   tank can capture empty territory and move again (pre-combat)

-   fighters and bombers can "launch" instead of unload
-   if they don't launch, they lose movement equal to the ship's movement
-   fighter and bombers automatically land on aircraft carriers they are in the same territory as
-   mobilization: can place fighters and bombers in the same territories as ships as long as there is room in cargo

-   submarine logic
-   bomber logic
-   AA logic

MONDAY

-   polling for team select lobby (if first and waiting)

-   remove console logs
-   add logging
-   toast popup with api error status

TUESDAY

-   player key request validation (end phase/turn)

-   backend tests
-   check TODOs
-   type checking functions

-   toast message for purchasing unit
-   toast message for each phase

-   fix loading spinners

WEDNESDAY

-   compiling vue app
-   hosting site

Future Work:

-   ampibious assault with sea battle: player unloads as if they win battle, sea battles are always handled first, if the player loses the battle, the units are removed from the land territory before that battle occurs (if still happening)

-   prevent attempt to unload to sea
-   ocean territories occupied by no one

-   scheduled tasks
-   skip players turn after certain time

-   game log so players can see what happened (where combat happened, territories flipped)
-   help screens - button while loading that explains the specific rules
-   EndTurnButton disabled is number but should be boolean
-   centralize getUnitIconSrc and getColorForUnit

-   maybe refactor defaultTray, loading should be consistent
-   end turn should reset tray

-   move session db logic to session model
-   sort friendly and enemy units in territory (UnitTray)
-   highlight territories that you may move units to
-   hint for saving bookmark to return to game
-   home base 3d object on home countries (capitals?)

-   three js objects
    capital city
    AA gun
    industrial complex

-   Develop weapons stage and Research Dice
-   National Advantages Table

-   Victory City
-   Liberating Territories

## Special Rules

You cannot use a canal unless your team controls it.
The Panama canal is controlled by Panama.
The Suez Canal is controlled by whoever controls both Anglo-Egypt and Trans-Jordan.
