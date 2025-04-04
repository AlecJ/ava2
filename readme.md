# AVA

Tactical Espionage Strategy?

## Installation

install Node 23
install Docker

## Run

run with
`cd ui`
`npm install`
`npm run dev`

## To Do

-   player key request validation (except end phase/turn)
-   prevent player from buying industrial complexs > territories owned

SATURDAY

Final tile fix in blender
Eastern United States / Panama / Mexico

Ocean Tiles
11 and 17 do NOT border
12 and 18 DO border
14 and 16 DO border
17 and 22 DO border
17 and 11 do NOT border
21 and 22 do NOT border

22: 17, 18, 23, 24, 25
ocean_tile_26 missing
Confirm "Anglo-Egypt"

-   finish territory data

-   fighters and bombers can "launch" instead of unload
-   if they don't launch, they lose movement equal to the ship's movement
-   fighter and bombers automatically land on aircraft carriers they are in the same territory as
-   mobilization: can place fighters and bombers in the same territories as ships as long as there is room in cargo

SUNDAY

-   combat
-   territory capture
-   tank can capture empty territory and move again (pre-combat)

MONDAY

-   polling for team select lobby (if first and waiting)

-   remove console logs
-   add logging
-   toast popup with api error status

TUESDAY

-   player key request validation (end phase/turn)

-   backend tests
-   check TODOs

-   toast message for purchasing unit
-   toast message for each phase

WEDNESDAY

-   compiling vue app
-   hosting site

Future Work:

-   submarine logic
-   bomber logic
-   AA logic

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
