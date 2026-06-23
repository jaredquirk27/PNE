Changelog

v1.3 - Memory Extraction Fixes

Fixed

* Fixed sentence splitting issue where user messages and character replies were being merged into a single sentence.
* Fixed memory extraction failing on preference statements during live chat.
* Fixed duplicate detection being global across all characters.
* Updated duplicate detection to be character-specific.

Added

* Automatic canonization during live chat persistence.
* Improved memory relevance scoring.
* Preference extraction for:
    * Favorite movie
    * Favorite color
    * Favorite sports team
    * Favorite dinosaur

Validated

* Rue successfully stores:
    * Jared’s favorite movie is The Fifth Element.
    * Jared’s favorite NHL team is the Tampa Bay Lightning.
    * Jared’s favorite color is purple.
    * Jared’s favorite dinosaur is raptor.
* Duplicate protection prevents repeated insertion of identical memories.

Notes

* Investigate whether memory_already_canonized() should be character-specific instead of global.
* Continue testing relationship memories and initiative generation using extracted preferences.