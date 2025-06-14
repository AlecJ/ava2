Hi,

Thanks for taking the time to check my github. I'm very proud of this project and hope it
accurately demonstrates my skills as a developer.

Best,
Alec

# Allies vs Axis

This game is played with up to 5 players, although a player can control multiple teams
by joining with multiple web tabs.

## Local Development

Requirements:

-   Node 23
-   Docker

## Run

Frontend:
`cd ui`
`npm install`
`npm run dev`

Backend:
`docker-compose up`

Connect to the mongo service and create a db named `ava` (or anything and update the mongo URI in the docker-compose.)

Run tests with:
`cd src`
`pytest`

## To Do

-   highlight selectable territories
-   highlight selected territory

-   way to see unit details (anytime)

-   indicate if country has units for each player

-   if rejoining, show loading spinner if session ID provided, otherwise straight to landing page

-   clear "place units" after placing units
-   anti-aircraft cannot be placed
-   increase polling only during mobilization phase
-   allow undo during mobilization/purchase phases?
-   during mobilization, highlight factory tiles

-   show current production per player

-   dragging units into "territory" boxes

-   selectTerritory validation rules

-   cannot select hawaii
-   west russia border removed

-   remove console logs
-   add logging

-   toast popup with api error status
-   toast message for purchasing unit
-   toast message for each phase

## Future Work

-   fix loading spinners

-   :param game_state:
-   backend tests
-   check TODOs
-   type checking functions

-   refactor getPlayerTeamNum
-   see what units are in a transport during combat?
-   opening mobilization units, close territory data

-   mobile design

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

-   Submarines can submerge
-   Develop weapons stage and Research Dice
-   National Advantages Table

-   Victory City
-   Liberating Territories

-   can easily share game code verbally
-   sesion id is 6 characters? 4?

## Special Rules

You cannot use a canal unless your team controls it.
The Panama canal is controlled by Panama.
The Suez Canal is controlled by whoever controls both Anglo-Egypt and Trans-Jordan.
