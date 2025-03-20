This app stores data as a tree with the root being the Session object.
Game State is initialized with a new session and both are given the same session_id.

-   A Session holds the status of the game, current turn, and a list of players.

-   A Player holds the player ID, session ID, and country.

-   A Game state holds the current state of the game, including territories.

-   A Territory holds a single territories information, including all units within in.

In addition, some intialization data is stored in the models directory:
territories.json -- starting units and locations
units.json -- basic unit information
