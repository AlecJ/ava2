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

-   purchase phase
-   able to undo turn

-   pre-combat movement phase (player may move into hostile territory)
-   post-combat movement phase (player may not move into hostile territory)

-   order of play
-   player key request validation

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
-   ship movement
-   loading and unloading
-   fighters on carriers
-   plane movement

-   combat
-   territory capture

-   player list and order
    current country’s turn indicated

-   polling for team select lobby (if first and waiting)
-   add logging
-   backend tests
-   remove console logs
-   check TODOs

Future Work:

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
