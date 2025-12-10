Hi,

Thanks for taking the time to check my github. I'm very proud of this project and hope it
accurately demonstrates my skills as a developer.

Best,
Alec

Try it now: [AlliesVsAxis.com](https://AlliesVsAxis.com)

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

-   AA battles may not be happening

-   move phase -- chance of shot down (already exists)
-   add message if survived or shot down

-   opening fire is its own turn
-   bombers have ability to retreat (to any territory)

-   bombers should be able to do a factory attack and retreat immediately
    (part of opening fire)
    (button to see AA fire)

-   auto launch fighters on battleships during fights
-   way to see units you have purchased
-   production updated immediately

-   cannot see troops on transports (unless its your turn)

-   game log

-   see other battles in action

-   ui to show production of a factory and how many are remaining

-   west russia border removed

-   if rejoining, show loading spinner if session ID provided, otherwise straight to landing page

-   clear "place units" after placing units

-   remove console logs
-   add logging

-   backend tests
-   check TODOs
-   type checking functions

## Potential Issues

-   anti-aircraft cannot be placed

## Future Work

-   sesion id is 6 characters? 4?

-   show unit tiles (vs flags) and numbers
-   increase polling only during mobilization phase
-   allow undo during mobilization/purchase phases?

-   show current production per player
-   selectTerritory validation rules

-   dragging units into "territory" boxes

-   :param game_state:

-   refactor getPlayerTeamNum
-   see what units are in a transport during combat?
-   opening mobilization units, close territory data

-   mobile design

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

-   Submarines can submerge
-   Develop weapons stage and Research Dice
-   National Advantages Table

-   Victory City
-   Liberating Territories

-   can easily share game code verbally

## Special Rules

You cannot use a canal unless your team controls it.
The Panama canal is controlled by Panama.
The Suez Canal is controlled by whoever controls both Anglo-Egypt and Trans-Jordan.
